"""Composição prevista do Congresso a partir de 1º/fev/2027 (58ª legislatura; DECISIONS 2026-10-24).

- Câmara: os 513 eleitos em 2026 (TSE, situação atual), pelo partido da eleição.
- Senado: os 54 eleitos em 2026 mais as 27 cadeiras com mandato até 31/01/2031 (eleitas em 2022).
  Em cada uma dessas 27, fica quem a ocupa na data dos dados do Senado (o que já cobre suplentes
  efetivados, como na renúncia de um titular); se o ocupante foi eleito governador no 1º turno de
  2026, a cadeira passa ao 1º suplente; se disputa o 2º turno, fica com aviso.
"""

import csv
import io
import json
import unicodedata
import zipfile
from datetime import date
from pathlib import Path

import polars as pl

from congresso.transform.senado import _lista, em_exercicio, ler_exercicios
from congresso.ufs import UFS_27

FIM_MANDATO_2022 = date(2031, 1, 31)

# Causas de afastamento do titular que encerram o mandato dele (o suplente fica de vez).
DEFINITIVAS = ("renúncia", "falecimento", "perda", "cassação")


def normalizar(nome: str) -> str:
    """Maiúsculas, sem acento e sem espaços extras (para casar nomes do Senado e do TSE)."""
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFD", nome) if unicodedata.category(c) != "Mn"
    )
    return " ".join(sem_acento.upper().split())


def cadeiras_ate_2031(pasta: Path, dia: date) -> pl.DataFrame:
    """Uma linha por UF: titular e 1º suplente do mandato que termina em 31/01/2031 e quem está em
    exercício na cadeira em `dia`. Para se a fonte não fechar 27 UFs com um ocupante cada."""
    linhas = []
    for arquivo in sorted((pasta / "mandatos").glob("*.json")):
        p = json.loads(arquivo.read_text(encoding="utf-8"))["MandatoParlamentar"]["Parlamentar"]
        for m in _lista((p.get("Mandatos") or {}).get("Mandato")):
            fim = (m.get("SegundaLegislaturaDoMandato") or {}).get("DataFim")
            if fim != FIM_MANDATO_2022.isoformat() or m.get("DescricaoParticipacao") != "Titular":
                continue
            suplentes = _lista((m.get("Suplentes") or {}).get("Suplente"))
            exercicios = sorted(
                _lista((m.get("Exercicios") or {}).get("Exercicio")),
                key=lambda e: e.get("DataInicio") or "",
            )
            ultima_causa = exercicios[-1].get("DescricaoCausaAfastamento") if exercicios else None
            primeiro = next(
                (s for s in suplentes if s.get("DescricaoParticipacao", "").startswith("1")), {}
            )
            linhas.append(
                {
                    "uf": m.get("UfParlamentar"),
                    "titular_codigo": arquivo.stem,
                    "titular_nome": p.get("Nome"),
                    "suplentes": [s.get("CodigoParlamentar") for s in suplentes],
                    "primeiro_suplente_codigo": primeiro.get("CodigoParlamentar"),
                    "primeiro_suplente_nome": primeiro.get("NomeParlamentar"),
                    "causa_afastamento_titular": ultima_causa,
                }
            )
    cadeiras = pl.DataFrame(linhas, schema_overrides={"causa_afastamento_titular": pl.String})
    if sorted(cadeiras["uf"].to_list()) != sorted(UFS_27):
        raise ValueError(f"Mandatos até 2031: esperado um titular por UF, veio {cadeiras.height}")
    exercicio = em_exercicio(ler_exercicios(pasta), dia)
    ocupantes = []
    for c in cadeiras.iter_rows(named=True):
        possiveis = {c["titular_codigo"], *c["suplentes"]}
        quem = exercicio.filter(pl.col("codigo").is_in(list(possiveis)))
        if quem.height != 1:
            raise ValueError(f"{c['uf']}: {quem.height} em exercício na cadeira até 2031 em {dia}")
        ocupantes.append(
            {"uf": c["uf"], "ocupante_codigo": quem["codigo"][0], "ocupante_nome": quem["nome"][0]}
        )
    return cadeiras.drop("suplentes").join(pl.DataFrame(ocupantes), on="uf").sort("uf")


def nomes_completos(pasta: Path) -> dict[str, str]:
    """Código do senador → nome completo, pelas listas de legislatura do Senado."""
    nomes = {}
    for arquivo in (pasta / "legislaturas").glob("*.json"):
        dados = json.loads(arquivo.read_text(encoding="utf-8"))
        for p in _lista(dados["ListaParlamentarLegislatura"]["Parlamentares"]["Parlamentar"]):
            ident = p["IdentificacaoParlamentar"]
            if ident.get("NomeCompletoParlamentar"):
                nomes[ident["CodigoParlamentar"]] = ident["NomeCompletoParlamentar"]
    return nomes


def governadores_1o_turno(zip_cand: Path, ano: int) -> dict[tuple[str, str], str]:
    """(UF, nome normalizado) → situação no 1º turno ("ELEITO", "2º TURNO", ...) dos candidatos a
    governador."""
    with zipfile.ZipFile(zip_cand) as z:
        texto = z.read(f"consulta_cand_{ano}_BRASIL.csv").decode("latin-1")
    return {
        (r["SG_UF"], normalizar(r["NM_CANDIDATO"])): r["DS_SIT_TOT_TURNO"].upper()
        for r in csv.DictReader(io.StringIO(texto), delimiter=";")
        if r["DS_CARGO"].upper() == "GOVERNADOR" and r["NR_TURNO"] == "1"
    }


def afastamento_definitivo(causa: str | None) -> bool:
    return bool(causa) and any(p in causa.lower() for p in DEFINITIVAS)


def suplentes_2022(zip_cand: Path) -> dict[tuple[str, str], str]:
    """(UF, nome de urna normalizado) → sigla do partido dos suplentes de senador em 2022."""
    with zipfile.ZipFile(zip_cand) as z:
        texto = z.read("consulta_cand_2022_BRASIL.csv").decode("latin-1")
    return {
        (r["SG_UF"], normalizar(r["NM_URNA_CANDIDATO"])): r["SG_PARTIDO"]
        for r in csv.DictReader(io.StringIO(texto), delimiter=";")
        if "SUPLENTE" in r["DS_CARGO"].upper()
    }
