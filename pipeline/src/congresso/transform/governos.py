"""Base formal de governo (PROJECT.md, 3.2 e 7.5): partidos com ministério, pelo critério do IPEA
(Almeida, Nota Técnica 53), em cada gabinete; e as cadeiras desses partidos numa data.

Os gabinetes do IPEA têm só o mês de início. Se uma data consultada cair no mesmo mês em que um
gabinete começa, não dá para saber qual vigorava: o pipeline para em vez de adivinhar.
"""

from datetime import date

import polars as pl


def ler_gabinetes(tabela: pl.DataFrame) -> pl.DataFrame:
    """Gabinetes com início (dia 1 do mês, ou a data exata, se houver) e partidos."""
    return tabela.select(
        "gabinete",
        pl.when(pl.col("inicio").str.len_chars() == 7)
        .then(pl.col("inicio") + "-01")
        .otherwise(pl.col("inicio"))
        .str.to_date()
        .alias("inicio"),
        (pl.col("inicio").str.len_chars() == 7).alias("so_mes"),
        "evento",
        pl.col("partido_ids")
        .fill_null("")
        .str.split(";")
        .list.eval(pl.element().filter(pl.element() != ""))
        .alias("partidos"),
        "fonte",
        (pl.col("observacao") if "observacao" in tabela.columns else pl.lit(None, pl.String)).alias(
            "observacao"
        ),
    ).sort("inicio")


def gabinete_em(gabinetes: pl.DataFrame, dia: date) -> dict | None:
    """O gabinete vigente no dia (o último que começou até ele)."""
    antes = gabinetes.filter(pl.col("inicio") <= dia)
    if not antes.height:
        return None
    ultimo = antes.row(-1, named=True)
    # Só o mês, e o mesmo mês do dia consultado: não dá para saber se já vigorava.
    if ultimo["so_mes"] and (ultimo["inicio"].year, ultimo["inicio"].month) == (
        dia.year,
        dia.month,
    ):
        raise ValueError(
            f"{dia}: o gabinete {ultimo['gabinete']} começa no mesmo mês e a fonte não dá o dia"
        )
    return ultimo


def base_formal(cadeiras: pl.DataFrame, gabinetes: pl.DataFrame, dia: date) -> dict:
    """Cadeiras dos partidos com ministério no gabinete vigente. `cadeiras` tem a coluna
    partido_id, uma linha por cadeira ocupada na data."""
    g = gabinete_em(gabinetes, dia)
    partidos = g["partidos"] if g else []
    na_base = cadeiras.filter(pl.col("partido_id").is_in(partidos)).height
    return {
        "data": dia,
        "gabinete": g["gabinete"] if g else None,
        "partidos": partidos,
        "cadeiras_base": na_base,
        "ocupadas": cadeiras.height,
    }
