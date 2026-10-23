"""Deputados federais eleitos em cada eleição, a partir dos arquivos do TSE (PROJECT.md, 7.2).

"Eleito" é a situação atual no TSE (DECISIONS, A14). Só as colunas necessárias são lidas: os
arquivos trazem CPF e e-mail dos candidatos, que o projeto não guarda.
"""

import csv
import io
import zipfile
from pathlib import Path

import polars as pl

CARGO = "DEPUTADO FEDERAL"

# Valores de DS_SIT_TOT_TURNO que significam eleito (conferidos de 1994 a 2026; o rótulo da média
# muda entre os anos).
SITUACOES_ELEITO = {"ELEITO", "ELEITO POR QP", "ELEITO POR MÉDIA", "MÉDIA"}

# Candidaturas que deixaram de existir e dividem o número com o substituto (ex.: 1998, PR 4515).
SITUACOES_SUBSTITUIDO = {"RENÚNCIA", "FALECIDO"}

# Layout de VOTACAO_CANDIDATO_UF (sem cabeçalho), segundo o Leia-me do TSE de 1990.
COLUNAS_1990 = [
    "DATA_GERACAO",
    "HORA_GERACAO",
    "ANO_ELEICAO",
    "NUM_TURNO",
    "DESCRICAO_ELEICAO",
    "SIGLA_UF",
    "SIGLA_UE",
    "CODIGO_CARGO",
    "NUMERO_CAND",
    "SQ_CANDIDATO",
    "NOME_CANDIDATO",
    "NOME_URNA_CANDIDATO",
    "DESCRICAO_CARGO",
    "COD_SIT_CAND_SUPERIOR",
    "DESC_SIT_CAND_SUPERIOR",
    "CODIGO_SIT_CANDIDATO",
    "DESC_SIT_CANDIDATO",
    "CODIGO_SIT_CAND_TOT",
    "DESC_SIT_CAND_TOT",
    "NUMERO_PARTIDO",
    "SIGLA_PARTIDO",
    "NOME_PARTIDO",
    "SEQUENCIAL_LEGENDA",
    "NOME_COLIGACAO",
    "COMPOSICAO_LEGENDA",
    "TOTAL_VOTOS",
]

ESQUEMA = {
    "ano": pl.Int16,
    "uf": pl.String,
    "nr_candidato": pl.String,
    "sq_candidato": pl.String,
    "nome": pl.String,
    "nome_urna": pl.String,
    "sigla_partido": pl.String,
    "nr_partido": pl.String,
    "sigla_federacao": pl.String,
    "situacao": pl.String,
    "tse_gerado_em": pl.String,
}


def _nulo(valor: str) -> str | None:
    """O TSE marca ausência com "#NULO#", "#NULO" ou "#NE#"."""
    valor = valor.strip()
    return None if not valor or valor.startswith("#N") else valor


def _linhas_csv(dados: bytes, colunas: list[str] | None = None) -> list[dict[str, str]]:
    texto = io.StringIO(dados.decode("latin-1"))
    return list(csv.DictReader(texto, fieldnames=colunas, delimiter=";"))


def ler_1990(zip_path: Path) -> pl.DataFrame:
    """Eleitos de 1990: um TXT por UF, sem cabeçalho, uma linha por candidato e turno."""
    registros = []
    with zipfile.ZipFile(zip_path) as z:
        for nome in sorted(z.namelist()):
            if not nome.lower().endswith(".txt"):
                continue
            for r in _linhas_csv(z.read(nome), COLUNAS_1990):
                if r["DESCRICAO_CARGO"].upper() != CARGO:
                    continue
                if r["DESC_SIT_CAND_TOT"].upper() not in SITUACOES_ELEITO:
                    continue
                registros.append(
                    {
                        "ano": int(r["ANO_ELEICAO"]),
                        "uf": r["SIGLA_UF"],
                        "nr_candidato": r["NUMERO_CAND"],
                        "sq_candidato": _nulo(r["SQ_CANDIDATO"]),
                        "nome": r["NOME_CANDIDATO"].strip(),
                        "nome_urna": _nulo(r["NOME_URNA_CANDIDATO"]),
                        "sigla_partido": r["SIGLA_PARTIDO"].strip(),
                        "nr_partido": r["NUMERO_PARTIDO"],
                        "sigla_federacao": None,
                        "situacao": r["DESC_SIT_CAND_TOT"].upper(),
                        "tse_gerado_em": f"{r['DATA_GERACAO']} {r['HORA_GERACAO']}",
                    }
                )
    return _deduplicar(registros)


def ler_consulta_cand(zip_path: Path, ano: int) -> pl.DataFrame:
    """Eleitos de 1994 em diante, do arquivo nacional `consulta_cand_<ano>_BRASIL.csv`."""
    with zipfile.ZipFile(zip_path) as z:
        linhas = _linhas_csv(z.read(f"consulta_cand_{ano}_BRASIL.csv"))
    registros = []
    for r in linhas:
        if r["DS_CARGO"].upper() != CARGO or r["NR_TURNO"] != "1":
            continue
        situacao = r["DS_SIT_TOT_TURNO"].upper()
        if situacao not in SITUACOES_ELEITO:
            continue
        registros.append(
            {
                "ano": int(r["ANO_ELEICAO"]),
                "uf": r["SG_UF"],
                "nr_candidato": r["NR_CANDIDATO"],
                "sq_candidato": _nulo(r["SQ_CANDIDATO"]),
                "nome": r["NM_CANDIDATO"].strip(),
                "nome_urna": _nulo(r["NM_URNA_CANDIDATO"]),
                "sigla_partido": r["SG_PARTIDO"].strip(),
                "nr_partido": r["NR_PARTIDO"],
                "sigla_federacao": _nulo(r.get("SG_FEDERACAO") or ""),
                "situacao": situacao,
                "situacao_candidatura": r["DS_SITUACAO_CANDIDATURA"].upper(),
                "tse_gerado_em": f"{r['DT_GERACAO']} {r['HH_GERACAO']}",
            }
        )
    return _deduplicar(registros)


def _deduplicar(registros: list[dict]) -> pl.DataFrame:
    """Uma cadeira por UF + número. Quando um substituto herda o número de quem renunciou ou morreu,
    fica o substituto; qualquer outra duplicata é erro nos dados e para o pipeline."""
    por_chave: dict[tuple[str, str], list[dict]] = {}
    for r in registros:
        por_chave.setdefault((r["uf"], r["nr_candidato"]), []).append(r)
    finais = []
    for chave, grupo in por_chave.items():
        if len(grupo) > 1:
            grupo = [r for r in grupo if r.get("situacao_candidatura") not in SITUACOES_SUBSTITUIDO]
        if len(grupo) != 1:
            raise ValueError(f"Eleito duplicado sem substituição explicável: {chave}")
        finais.append({k: grupo[0][k] for k in ESQUEMA})
    return pl.DataFrame(finais, schema=ESQUEMA).sort("ano", "uf", "nr_candidato")


def ler_vagas(zip_path: Path, ano: int) -> pl.DataFrame:
    """Vagas de deputado federal por UF. Em 1990, TXT por UF sem cabeçalho (Leia-me do TSE)."""
    vagas: dict[str, int] = {}
    with zipfile.ZipFile(zip_path) as z:
        if ano == 1990:
            for nome in z.namelist():
                if not nome.lower().endswith(".txt"):
                    continue
                for linha in csv.reader(io.StringIO(z.read(nome).decode("latin-1")), delimiter=";"):
                    # SIGLA_UF (4), DESCRICAO_CARGO (8), QTDE_VAGAS (9)
                    if linha[8].upper() == CARGO:
                        vagas[linha[4]] = int(linha[9])
        else:
            for r in _linhas_csv(z.read(f"consulta_vagas_{ano}_BRASIL.csv")):
                if r["DS_CARGO"].upper() == CARGO:
                    # A coluna se chama QT_VAGAS em alguns anos (ex.: 2010) e QT_VAGA nos demais.
                    vagas[r["SG_UF"]] = int(r.get("QT_VAGA") or r["QT_VAGAS"])
    return pl.DataFrame(
        {"ano": [ano] * len(vagas), "uf": list(vagas), "vagas": list(vagas.values())},
        schema={"ano": pl.Int16, "uf": pl.String, "vagas": pl.Int32},
    ).sort("uf")
