"""Conferências dos eleitos (PROJECT.md, 10.1): vagas por UF e bancadas do Apêndice A."""

import polars as pl

# Tolerância por partido contra o Apêndice A: as fontes secundárias divergem em ±1–2 cadeiras.
TOLERANCIA = 2


# CF, art. 45, § 1º: nenhuma UF com menos de 8 nem mais de 70 deputados.
MINIMO_UF, MAXIMO_UF = 8, 70


def conferir_limites(eleitos: pl.DataFrame, ano: int, total: int) -> list[str]:
    """Para anos sem vagas de deputado federal no TSE (1994): total e limites constitucionais."""
    do_ano = eleitos.filter(pl.col("ano") == ano)
    problemas = []
    if do_ano.height != total:
        problemas.append(f"{ano}: {do_ano.height} eleitos, esperado {total}")
    for uf, n in do_ano.group_by("uf").len().sort("uf").iter_rows():
        if not MINIMO_UF <= n <= MAXIMO_UF:
            problemas.append(f"{ano} {uf}: {n} eleitos, fora do limite de 8 a 70")
    return problemas


def conferir_vagas(eleitos: pl.DataFrame, vagas: pl.DataFrame) -> list[str]:
    """Problemas encontrados: cada UF tem de ter exatamente as vagas do TSE. Lista vazia = ok."""
    contagem = (
        eleitos.filter(pl.col("ano").is_in(vagas["ano"].unique().implode()))
        .group_by("ano", "uf")
        .len("eleitos")
    )
    junto = vagas.join(contagem, on=["ano", "uf"], how="full", coalesce=True).with_columns(
        pl.col("vagas").fill_null(0), pl.col("eleitos").fill_null(0)
    )
    return [
        f"{r['ano']} {r['uf']}: {r['eleitos']} eleitos para {r['vagas']} vagas"
        for r in junto.filter(pl.col("vagas") != pl.col("eleitos"))
        .sort("ano", "uf")
        .iter_rows(named=True)
    ]


def conferir_referencia(eleitos: pl.DataFrame, referencia: pl.DataFrame) -> pl.DataFrame:
    """Bancadas do TSE contra a referência; só as linhas que diferem, com a marca de tolerância."""
    bancadas = (
        eleitos.group_by("ano", "sigla_partido")
        .len("tse")
        .with_columns(pl.col("tse").cast(pl.Int32))
    )
    return (
        referencia.select("ano", "sigla_partido", pl.col("cadeiras").alias("referencia"))
        .join(bancadas, on=["ano", "sigla_partido"], how="left")
        .with_columns(pl.col("tse").fill_null(0))
        .with_columns((pl.col("tse") - pl.col("referencia")).alias("diferenca"))
        .filter(pl.col("diferenca") != 0)
        .with_columns((pl.col("diferenca").abs() > TOLERANCIA).alias("fora_da_tolerancia"))
        .sort("ano", "sigla_partido")
    )
