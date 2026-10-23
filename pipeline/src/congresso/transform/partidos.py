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


def atribuir_partido_camara(fotos: pl.DataFrame, mapa: pl.DataFrame) -> pl.DataFrame:
    """Acrescenta o partido (ID estável) à sigla registrada pela Câmara na data de cada foto.

    A mesma sigla pode ser de partidos diferentes em épocas diferentes (ex.: "PL" até 2006 e de
    2019 em diante); por isso o mapa tem período de validade. Cada linha tem de casar com
    exatamente um partido.
    """
    mapa = mapa.select(
        "sigla_camara",
        pl.col("valido_desde").str.to_date().fill_null(pl.date(1900, 1, 1)),
        pl.col("valido_ate").str.to_date().fill_null(pl.date(2999, 12, 31)),
        "partido_id",
    )
    casados = (
        fotos.with_row_index("_linha")
        .join(mapa, left_on="sigla_partido", right_on="sigla_camara", how="left")
        .filter(
            pl.col("partido_id").is_null()
            | (
                (pl.col("data") >= pl.col("valido_desde"))
                & (pl.col("data") <= pl.col("valido_ate"))
            )
        )
    )
    contagem = casados.group_by("_linha").len()
    if (
        contagem.height != fotos.height
        or (contagem["len"] != 1).any()
        or casados["partido_id"].is_null().any()
    ):
        com_problema = fotos.with_row_index("_linha").join(
            contagem.filter(pl.col("len") == 1), on="_linha", how="anti"
        )
        sem = casados.filter(pl.col("partido_id").is_null())
        pares = pl.concat(
            [com_problema.select("data", "sigla_partido"), sem.select("data", "sigla_partido")]
        )
        raise ValueError(
            f"Siglas da Câmara sem partido único em data/manual/partidos_camara.csv: "
            f"{pares.unique().sort('data').rows()[:20]}"
        )
    return casados.sort("_linha").drop("_linha", "valido_desde", "valido_ate")
