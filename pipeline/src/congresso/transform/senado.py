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
