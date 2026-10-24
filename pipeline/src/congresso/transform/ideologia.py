"""Posição ideológica por partido e legislatura (PROJECT.md, 7.4; DECISIONS A1, A7, A17).

- 49ª a 56ª: só a onda da BLS feita durante a legislatura, na escala da BLS (−1 a +1), sem rótulo.
  Partido que a BLS não mediu fica sem linha (= "não classificado"): uma só escala por legislatura.
- 57ª e 58ª: Bolognesi et al. 2022, média ponderada e faixa como publicadas (0 a 10).
"""

import polars as pl

# Onda da BLS feita durante cada legislatura (mapeamento dos próprios autores).
ONDA_BLS = {49: 1993, 50: 1997, 51: 2001, 52: 2005, 53: 2009, 54: 2013, 55: 2017, 56: 2021}
LEGISLATURAS_BOLOGNESI = (57, 58)

ESCALA_BLS = "BLS: −1 (esquerda) a +1 (direita), estimativa por partido (Zucco & Power)"
ESCALA_BOLOGNESI = "Bolognesi et al.: 0 (extrema-esquerda) a 10 (extrema-direita), média ponderada"

# Cortes das sete faixas (Bolognesi et al., Opinião Pública 2025, p. 13), sobre a escala 0–10.
FAIXAS = [
    (1.5, "extrema-esquerda"),
    (3.0, "esquerda"),
    (4.49, "centro-esquerda"),
    (5.5, "centro"),
    (7.0, "centro-direita"),
    (8.5, "direita"),
    (10.0, "extrema-direita"),
]

COLUNAS = {
    "legislatura": pl.Int16,
    "partido_id": pl.String,
    "fonte_id": pl.String,
    "ano_medicao": pl.Int16,
    "sigla_fonte": pl.String,
    "escala": pl.String,
    "pontuacao": pl.Float64,
    "erro_padrao": pl.Float64,
    "n": pl.Int32,
    "faixa": pl.String,
    "nota": pl.String,
}


def faixa(valor: float) -> str:
    """Faixa pelos cortes publicados (os intervalos do artigo têm duas casas: 1,5 → 1,51)."""
    for limite, nome in FAIXAS:
        if round(valor, 2) <= limite:
            return nome
    raise ValueError(f"Pontuação fora da escala 0–10: {valor}")


def de_bls(estimativas: pl.DataFrame, siglas: pl.DataFrame) -> pl.DataFrame:
    """Linhas das legislaturas 49ª a 56ª. `estimativas` é o CSV do Dataverse."""
    onda_para_leg = pl.DataFrame(
        {"ano_medicao": list(ONDA_BLS.values()), "legislatura": list(ONDA_BLS)},
        schema={"ano_medicao": pl.Int16, "legislatura": pl.Int16},
    )
    est = estimativas.select(
        pl.col("year").cast(pl.Int16).alias("ano_medicao"),
        pl.col("party.or.pres").alias("sigla_fonte"),
        pl.col("ideo").alias("pontuacao"),
        pl.col("ideo.se").alias("erro_padrao"),
    )
    return (
        siglas.filter(pl.col("fonte_id") == "bls")
        .join(est, on=["ano_medicao", "sigla_fonte"], how="left")
        .join(onda_para_leg, on="ano_medicao")
        .with_columns(
            pl.lit(ESCALA_BLS).alias("escala"),
            pl.lit(None, pl.Int32).alias("n"),
            pl.lit(None, pl.String).alias("faixa"),
            pl.col("observacao").alias("nota"),
        )
        .select(list(COLUNAS))
        .cast(COLUNAS)
    )


def de_bolognesi(tabela: pl.DataFrame, siglas: pl.DataFrame) -> pl.DataFrame:
    """Linhas das legislaturas 57ª e 58ª, com a média simples de 2022 e a faixa pelos cortes dos
    autores (DECISIONS 2026-10-24, revisão da A17).

    A "média ponderada" publicada é a média simples multiplicada por um fator único de ~1,03 que o
    artigo não descreve de forma reproduzível (o método do texto não gera a tabela; o UP, sem média
    de 2018, também recebe o fator). A faixa publicada continua sendo conferida contra a média
    ponderada, como teste da transcrição."""
    erradas = [
        r["sigla_fonte"]
        for r in tabela.iter_rows(named=True)
        if faixa(r["media_ponderada"]) != r["faixa_publicada"].replace(" ", "-")
    ]
    if erradas:
        raise ValueError(f"Bolognesi: faixa publicada não bate com a média ponderada: {erradas}")
    base = siglas.filter(pl.col("fonte_id") == "bolognesi").join(
        tabela.select(
            "sigla_fonte",
            pl.col("media_2022").alias("pontuacao"),
            pl.col("media_2022").map_elements(faixa, return_dtype=pl.String).alias("faixa"),
            pl.col("n_validos").alias("n"),
        ),
        on="sigla_fonte",
        how="left",
    )
    partes = []
    for leg in LEGISLATURAS_BOLOGNESI:
        # PROJECT.md 7.4.3: sinalizar a medição de 2022 aplicada à legislatura de 2027.
        nota = (
            pl.lit("medição de 2022 aplicada a legislatura iniciada em 2027")
            if leg == 58
            else (pl.col("observacao"))
        )
        partes.append(
            base.with_columns(
                pl.lit(leg).alias("legislatura"),
                pl.lit(ESCALA_BOLOGNESI).alias("escala"),
                pl.lit(None, pl.Float64).alias("erro_padrao"),
                nota.alias("nota"),
            )
            .select(list(COLUNAS))
            .cast(COLUNAS)
        )
    return pl.concat(partes)


def conferir(tabela: pl.DataFrame) -> list[str]:
    """PROJECT.md 10.1: toda pontuação tem fonte, ano e escala; um valor por partido e legislatura;
    e a faixa publicada bate com os cortes (sinal de transcrição errada se não bater)."""
    problemas = []
    sem = tabela.filter(
        pl.col("pontuacao").is_null() | pl.col("ano_medicao").is_null() | pl.col("escala").is_null()
    )
    if sem.height:
        problemas.append(
            f"sem pontuação, ano ou escala: {sem.select('legislatura', 'sigla_fonte').rows()}"
        )
    if tabela.select("legislatura", "partido_id").is_duplicated().any():
        problemas.append("partido com mais de uma pontuação na mesma legislatura")
    for r in tabela.filter(pl.col("faixa").is_not_null()).iter_rows(named=True):
        if faixa(r["pontuacao"]) != r["faixa"]:
            problemas.append(
                f"{r['sigla_fonte']}: {r['pontuacao']} não é '{r['faixa']}' pelos cortes"
            )
    return problemas


def posicao_dos_presidentes(governos: pl.DataFrame, estimativas: pl.DataFrame) -> pl.DataFrame:
    """Posição de cada presidente na escala da BLS (Zucco & Power), por governo.

    A BLS só avaliou presidentes nas ondas de 2013, 2017 e 2021, quase sempre depois do mandato.
    Escolha (DECISIONS 2026-10-24): a onda feita durante o mandato; senão, a primeira posterior;
    senão, a mais recente anterior (só Lula 3, que tem a de 2017). `relacao` diz qual foi o caso.
    """
    est = estimativas.select(
        pl.col("year").cast(pl.Int16).alias("ano"),
        pl.col("party.or.pres").alias("presidente_bls"),
        pl.col("ideo").alias("pontuacao"),
        pl.col("ideo.se").alias("erro_padrao"),
    )
    linhas = []
    for g in governos.iter_rows(named=True):
        ondas = est.filter(pl.col("presidente_bls") == g["presidente_bls"]).sort("ano")
        if ondas.height == 0:
            raise ValueError(f"{g['governo_id']}: presidente sem avaliação na BLS")
        ini, fim = g["inicio"].year, g["fim"].year
        durante = ondas.filter((pl.col("ano") >= ini) & (pl.col("ano") <= fim))
        depois = ondas.filter(pl.col("ano") > fim)
        antes = ondas.filter(pl.col("ano") < ini)
        if durante.height:
            escolhida, relacao = durante.row(-1, named=True), "durante"
        elif depois.height:
            escolhida, relacao = depois.row(0, named=True), "depois"
        else:
            escolhida, relacao = antes.row(-1, named=True), "antes"
        linhas.append(
            {
                "governo_id": g["governo_id"],
                "posicao_presidente": {
                    "pontuacao": round(escolhida["pontuacao"], 4),
                    "erro_padrao": round(escolhida["erro_padrao"], 4),
                    "ano_medicao": escolhida["ano"],
                    "relacao": relacao,
                },
            }
        )
    return pl.DataFrame(linhas)
