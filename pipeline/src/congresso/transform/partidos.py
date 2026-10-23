"""Partidos com ID estável (PROJECT.md, 7.3), a partir das tabelas curadas em data/manual."""

import polars as pl


def atribuir_partido(eleitos: pl.DataFrame, mapa: pl.DataFrame) -> pl.DataFrame:
    """Acrescenta o partido (ID estável) e a sigla da época pela tabela (eleição, número).

    O número identifica o partido numa eleição; a sigla do TSE não, porque o TSE a regrava com o
    nome atual (ex.: "PATRIOTA" no arquivo de 2014, quando o partido era o PEN). Para evitar que uma
    regravação futura passe despercebida, a sigla do arquivo tem de bater com a da curadoria.
    """
    mapa = mapa.select("ano", "nr_partido", "sigla_tse", "partido_id", "sigla_na_eleicao")
    junto = eleitos.join(mapa, on=["ano", "nr_partido"], how="left")
    sem_mapa = junto.filter(pl.col("partido_id").is_null())
    if sem_mapa.height:
        pares = sem_mapa.select("ano", "nr_partido", "sigla_partido").unique().sort("ano").rows()
        raise ValueError(f"Eleitos sem partido em data/manual/partidos_tse.csv: {pares}")
    trocada = junto.filter(pl.col("sigla_tse") != pl.col("sigla_partido"))
    if trocada.height:
        pares = trocada.select("ano", "nr_partido", "sigla_tse", "sigla_partido").unique().rows()
        raise ValueError(f"Sigla do TSE mudou desde a curadoria de partidos_tse.csv: {pares}")
    return junto.drop("sigla_tse")
