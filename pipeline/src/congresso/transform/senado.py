"""Senado: períodos de exercício, filiações datadas e fotos de 1º de fevereiro (DECISIONS: fotos do
Senado só nos anos em que a fonte oficial fecha 81 cadeiras, 3 por UF)."""

import json
from datetime import date
from pathlib import Path

import polars as pl

CADEIRAS, POR_UF = 81, 3


def _lista(x) -> list:
    return x if isinstance(x, list) else ([x] if x else [])


def ler_exercicios(pasta: Path) -> pl.DataFrame:
    """Um período de exercício por linha: código, nome, UF, início, fim (vazio = em curso)."""
    linhas = []
    for arquivo in sorted((pasta / "mandatos").glob("*.json")):
        p = json.loads(arquivo.read_text(encoding="utf-8"))["MandatoParlamentar"]["Parlamentar"]
        for m in _lista((p.get("Mandatos") or {}).get("Mandato")):
            for e in _lista((m.get("Exercicios") or {}).get("Exercicio")):
                if not e.get("DataInicio"):
                    continue
                linhas.append(
                    {
                        "codigo": arquivo.stem,
                        "nome": p.get("Nome"),
                        "uf": m.get("UfParlamentar"),
                        "inicio": date.fromisoformat(e["DataInicio"]),
                        "fim": date.fromisoformat(e["DataFim"]) if e.get("DataFim") else None,
                    }
                )
    return pl.DataFrame(linhas)


def ler_filiacoes(pasta: Path) -> pl.DataFrame:
    """Filiações datadas: código, sigla (como a API grava), início, fim (vazio = vigente)."""
    linhas = []
    for arquivo in sorted((pasta / "filiacoes").glob("*.json")):
        p = json.loads(arquivo.read_text(encoding="utf-8"))["FiliacaoParlamentar"]["Parlamentar"]
        for f in _lista((p.get("Filiacoes") or {}).get("Filiacao")):
            sigla = f["Partido"].get("SiglaPartido")
            if not sigla or not f.get("DataFiliacao"):
                continue
            linhas.append(
                {
                    "codigo": arquivo.stem,
                    "sigla": sigla,
                    "inicio": date.fromisoformat(f["DataFiliacao"]),
                    "fim": date.fromisoformat(f["DataDesfiliacao"])
                    if f.get("DataDesfiliacao")
                    else None,
                }
            )
    return pl.DataFrame(linhas)


def em_exercicio(exercicios: pl.DataFrame, dia: date) -> pl.DataFrame:
    return (
        exercicios.filter(
            (pl.col("inicio") <= dia) & (pl.col("fim").is_null() | (pl.col("fim") >= dia))
        )
        .unique("codigo", keep="last")
        .select("codigo", "nome", "uf")
    )


def conferir(foto: pl.DataFrame) -> str | None:
    """Motivo da lacuna, ou None se a foto fecha 81 cadeiras com 3 por UF."""
    if foto.height != CADEIRAS:
        return f"{foto.height} senadores em exercício pelos registros da fonte, e não {CADEIRAS}"
    fora = foto.group_by("uf").len().filter(pl.col("len") != POR_UF)
    if fora.height:
        return "UF sem exatamente 3 senadores: " + ", ".join(
            f"{uf} ({n})" for uf, n in fora.sort("uf").iter_rows()
        )
    return None


def partido_na_data(
    foto: pl.DataFrame, filiacoes: pl.DataFrame, mapa: pl.DataFrame, dia: date
) -> pl.DataFrame:
    """Partido de cada senador na data, pela filiação datada que a cobre (a mais recente, se houver
    mais de uma); sem filiação datada, "nao_informado". A sigla da API vira partido pelo `mapa`
    (sigla_senado, valido_desde, valido_ate, partido_id)."""
    vigentes = (
        filiacoes.filter(
            (pl.col("inicio") <= dia) & (pl.col("fim").is_null() | (pl.col("fim") >= dia))
        )
        .sort("inicio")
        .unique("codigo", keep="last")
        .select("codigo", "sigla")
    )
    regras = mapa.select(
        "sigla_senado",
        pl.col("valido_desde").cast(pl.String).str.to_date().fill_null(date(1900, 1, 1)),
        pl.col("valido_ate").cast(pl.String).str.to_date().fill_null(date(2999, 12, 31)),
        "partido_id",
    ).filter((pl.col("valido_desde") <= dia) & (pl.col("valido_ate") >= dia))
    com_sigla = foto.join(vigentes, on="codigo", how="left").join(
        regras.select("sigla_senado", "partido_id"),
        left_on="sigla",
        right_on="sigla_senado",
        how="left",
    )
    sem_mapa = com_sigla.filter(pl.col("sigla").is_not_null() & pl.col("partido_id").is_null())
    if sem_mapa.height:
        raise ValueError(
            f"{dia}: siglas do Senado sem partido em partidos_senado.csv: "
            f"{sorted(sem_mapa['sigla'].unique())}"
        )
    return com_sigla.with_columns(pl.col("partido_id").fill_null("nao_informado"))


# Situações registradas nas votações do Senado (DECISIONS: Senado, votações e presença).
VOTOS = {"Sim": "Sim", "Não": "Não", "Abstenção": "Abstenção", "Obstrução": "Obstrução"}
VOTOS.update(
    {"Sim - Presidente Art.48 inciso XXIII": "Sim", "Não - Presidente Art.48 inciso XXIII": "Não"}
)
PRESIDENTE = {"Presidente (art. 51 RISF)"}
LICENCA = {"LS", "LP", "LG", "LA", "LAP"}
SERVICO = {"AP", "MIS", "REP", "MERC"}
NAO_VOTOU = {"NCom", "P-NRV"}


def ler_votacoes(pasta: Path, ano: int) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Votações de plenário de um ano (abertas e secretas) e votos individuais das abertas."""
    dados = json.loads((pasta / "votacoes" / f"{ano}.json").read_text(encoding="utf-8"))
    orient = json.loads((pasta / "orientacoes" / f"{ano}.json").read_text(encoding="utf-8"))
    governo = {}
    for o in orient.get("votacoes", []):
        for li in o.get("orientacoesLideranca") or []:
            if li.get("partido") == "Governo":
                voto = (li.get("voto") or "").upper()
                governo[o["sequencialVotacao"]] = {
                    "SIM": "Sim",
                    "NÃO": "Não",
                    "NAO": "Não",
                    "LIBERADO": "Liberado",
                    "LIVRE": "Liberado",
                    "OBSTRUÇÃO": "Obstrução",
                }.get(voto, voto.capitalize() or None)
    vs, votos = [], []
    for v in dados:
        ident = f"SF-{v['codigoSessaoVotacao']}"
        secreta = v.get("votacaoSecreta") == "S"
        vs.append(
            {
                "id": ident,
                "data": v["dataSessao"],
                "identificacao": v.get("identificacao") or "",
                "descricao": (v.get("descricaoVotacao") or "").strip(),
                "resultado": v.get("resultadoVotacao"),
                "secreta": secreta,
                "orientacao_governo": governo.get(v.get("sequencialVotacao")),
                "sigla_materia": v.get("sigla"),
            }
        )
        if secreta:
            continue
        for x in v.get("votos") or []:
            votos.append(
                {
                    "id_votacao": ident,
                    "data": v["dataSessao"],
                    "codigo": str(x["codigoParlamentar"]),
                    "nome": x.get("nomeParlamentar"),
                    "uf": x.get("siglaUFParlamentar"),
                    "situacao": x.get("siglaVotoParlamentar"),
                }
            )
    tab_v = pl.DataFrame(vs, schema_overrides={"orientacao_governo": pl.String})
    tab_votos = pl.DataFrame(votos)
    if tab_votos.height:
        tab_votos = tab_votos.with_columns(
            pl.col("situacao").replace_strict(VOTOS, default=None).alias("voto"),
            pl.col("situacao").is_in(list(VOTOS)).alias("votou"),
            (
                ~pl.col("situacao").is_in(list(LICENCA | SERVICO | PRESIDENTE))
                & (
                    pl.col("situacao").is_in(list(VOTOS))
                    | pl.col("situacao").is_in(list(NAO_VOTOU))
                )
            ).alias("esperado"),
        )
    return tab_v, tab_votos


def partido_nos_votos(
    votos: pl.DataFrame, filiacoes: pl.DataFrame, mapa: pl.DataFrame
) -> pl.DataFrame:
    """Partido de cada senador na data de cada votação, pela filiação datada que a cobre."""
    com_data = votos.with_columns(pl.col("data").str.to_date())
    candidatos = com_data.join(filiacoes, on="codigo", how="left").filter(
        pl.col("inicio").is_null()
        | (
            (pl.col("inicio") <= pl.col("data"))
            & (pl.col("fim").is_null() | (pl.col("fim") >= pl.col("data")))
        )
    )
    vigente = (
        candidatos.sort("inicio", nulls_last=False)
        .group_by("id_votacao", "codigo", maintain_order=True)
        .last()
        .select("id_votacao", "codigo", "sigla")
    )
    base = com_data.join(vigente, on=["id_votacao", "codigo"], how="left")
    regras = mapa.select(
        "sigla_senado",
        pl.col("valido_desde").cast(pl.String).str.to_date().fill_null(date(1900, 1, 1)),
        pl.col("valido_ate").cast(pl.String).str.to_date().fill_null(date(2999, 12, 31)),
        "partido_id",
    )
    casado = (
        base.with_row_index("_l")
        .join(regras, left_on="sigla", right_on="sigla_senado", how="left")
        .filter(
            pl.col("partido_id").is_null()
            | (
                (pl.col("data") >= pl.col("valido_desde"))
                & (pl.col("data") <= pl.col("valido_ate"))
            )
        )
        .unique("_l", keep="first")
    )
    sem = casado.filter(pl.col("sigla").is_not_null() & pl.col("partido_id").is_null())
    if sem.height:
        raise ValueError(
            f"siglas do Senado sem partido na data: {sorted(sem['sigla'].unique())[:10]}"
        )
    faltando = base.with_row_index("_l").join(casado.select("_l"), on="_l", how="anti")
    return (
        pl.concat(
            [casado, faltando.with_columns(pl.lit(None, pl.String).alias("partido_id"))],
            how="diagonal",
        )
        .sort("_l")
        .with_columns(pl.col("partido_id").fill_null("nao_informado"))
        .drop("_l", "valido_desde", "valido_ate", "sigla_senado", strict=False)
    )


def ler_mandatos(pasta: Path) -> pl.DataFrame:
    """Período de cada mandato (titular ou suplente): código, início da 1ª legislatura e fim da
    última. Mais completo que os exercícios (existe também para a 48ª legislatura)."""
    linhas = []
    for arquivo in sorted((pasta / "mandatos").glob("*.json")):
        p = json.loads(arquivo.read_text(encoding="utf-8"))["MandatoParlamentar"]["Parlamentar"]
        for m in _lista((p.get("Mandatos") or {}).get("Mandato")):
            a = m.get("PrimeiraLegislaturaDoMandato") or {}
            b = m.get("SegundaLegislaturaDoMandato") or {}
            ini, fim = a.get("DataInicio"), b.get("DataFim") or a.get("DataFim")
            if ini and fim:
                linhas.append(
                    {
                        "codigo": arquivo.stem,
                        "ini": date.fromisoformat(ini),
                        "fim_mandato": date.fromisoformat(fim),
                    }
                )
    return pl.DataFrame(linhas)


# Votação cuja lista traz muitos senadores sem mandato na data tem data ou lista errada na fonte.
# Nos dados de 2026-10-23 a distribuição é bimodal: 0 a 3 por votação (lacunas do cadastro de
# mandatos) ou 40 ou mais (25 votações de 2002, 2015, 2016 e 2017).
LIMITE_SEM_MANDATO = 10


def votacoes_inconsistentes(votos: pl.DataFrame, mandatos: pl.DataFrame) -> pl.DataFrame:
    """Votações com pelo menos LIMITE_SEM_MANDATO senadores listados sem mandato na data."""
    j = votos.select("id_votacao", "data", "codigo").join(mandatos, on="codigo", how="left")
    ok = (pl.col("ini") <= pl.col("data")) & (pl.col("fim_mandato") >= pl.col("data"))
    return (
        j.with_columns(ok.fill_null(False).alias("ok"))
        .group_by("id_votacao", "data", "codigo")
        .agg(pl.col("ok").any())
        .group_by("id_votacao", "data")
        .agg((~pl.col("ok")).sum().alias("sem_mandato"), pl.len().alias("listados"))
        .filter(pl.col("sem_mandato") >= LIMITE_SEM_MANDATO)
        .sort("data")
    )
