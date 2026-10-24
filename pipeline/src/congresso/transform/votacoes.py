"""Votações nominais de plenário da Câmara e seus votos (PROJECT.md, 6.3 e 7.6; DECISIONS A3–A8).

- Votação nominal = votação do Plenário (siglaOrgao "PLEN") com voto individual registrado.
- Orientação do Governo: bancada "GOV." (2003–2019, 2022) ou "Governo" (2020 em diante).
- "Artigo 17" é o registro do presidente da sessão: fica nos votos (para conferência), mas não
  entra em governismo, coesão nem presença (DECISIONS A3).
"""

from pathlib import Path

import polars as pl

BANCADAS_GOVERNO = {"GOV.", "Governo"}
VOTOS_VALIDOS = ("Sim", "Não", "Abstenção", "Obstrução")


def _csv(caminho: Path) -> pl.DataFrame:
    return pl.read_csv(caminho, separator=";", infer_schema=False, encoding="utf8-lossy")


def ler_ano(
    votacoes: Path, votos: Path, proposicoes: Path, orientacoes: Path | None
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Votações nominais de plenário e seus votos, de um ano."""
    v = _csv(votacoes).filter(pl.col("siglaOrgao") == "PLEN")
    vt = _csv(votos).filter(pl.col("idVotacao").is_in(v["id"].implode()))
    v = v.filter(pl.col("id").is_in(vt["idVotacao"].unique().implode()))

    props = (
        _csv(proposicoes)
        .filter(pl.col("idVotacao").is_in(v["id"].implode()))
        .with_columns(
            (
                pl.col("proposicao_siglaTipo")
                + " "
                + pl.col("proposicao_numero")
                + "/"
                + pl.col("proposicao_ano")
            ).alias("rotulo")
        )
        .group_by("idVotacao")
        .agg(
            pl.col("rotulo").unique().sort().alias("proposicoes"),
            pl.col("proposicao_siglaTipo").unique().alias("tipos"),
        )
    )
    if orientacoes is not None:
        gov = (
            _csv(orientacoes)
            .filter(pl.col("siglaBancada").is_in(list(BANCADAS_GOVERNO)))
            .group_by("idVotacao")
            .agg(pl.col("orientacao").last().alias("orientacao_governo"))
        )
    else:
        gov = pl.DataFrame(schema={"idVotacao": pl.String, "orientacao_governo": pl.String})

    contagem = vt.group_by("idVotacao").agg(
        *[(pl.col("voto") == x).sum().alias(f"n_{x}") for x in (*VOTOS_VALIDOS, "Artigo 17")]
    )
    tabela_v = (
        v.select(
            pl.col("id"),
            pl.col("dataHoraRegistro").alias("data_hora"),
            pl.col("data"),
            pl.col("descricao"),
            pl.col("ultimaAberturaVotacao_descricao").alias("descricao_abertura"),
            pl.col("aprovacao"),
        )
        .join(props, left_on="id", right_on="idVotacao", how="left")
        .join(gov, left_on="id", right_on="idVotacao", how="left")
        .join(contagem, left_on="id", right_on="idVotacao", how="left")
        .with_columns(
            pl.col("orientacao_governo").replace("", None),
            pl.col("proposicoes").fill_null([]),
            pl.col("tipos").fill_null([]),
        )
    )
    tabela_votos = vt.select(
        pl.col("idVotacao").alias("id_votacao"),
        pl.col("dataHoraVoto").alias("data_hora_voto"),
        pl.col("voto"),
        pl.col("deputado_id").cast(pl.Int64).alias("id_deputado"),
        pl.col("deputado_nome").alias("nome"),
        pl.col("deputado_siglaPartido").alias("sigla_partido"),
        pl.col("deputado_siglaUf").alias("uf"),
    ).join(tabela_v.select("id", "data"), left_on="id_votacao", right_on="id")
    return tabela_v, tabela_votos


def governismo(votos: pl.DataFrame, votacoes: pl.DataFrame, por: list[str]) -> pl.DataFrame:
    """Taxa de governismo (DECISIONS A8): votos iguais à orientação do Governo ÷ votos Sim, Não,
    Abstenção e Obstrução, só em votações em que o Governo orientou Sim ou Não."""
    orientadas = votacoes.filter(pl.col("orientacao_governo").is_in(["Sim", "Não"])).select(
        "id", "orientacao_governo"
    )
    return (
        votos.filter(pl.col("voto").is_in(list(VOTOS_VALIDOS)))
        .join(orientadas, left_on="id_votacao", right_on="id")
        .group_by(por)
        .agg(
            (pl.col("voto") == pl.col("orientacao_governo")).sum().alias("com_governo"),
            pl.len().alias("votos_considerados"),
            pl.col("id_votacao").n_unique().alias("votacoes"),
        )
        .with_columns((pl.col("com_governo") / pl.col("votos_considerados")).alias("governismo"))
    )


def rice(votos: pl.DataFrame) -> pl.DataFrame:
    """Índice de Rice por votação e partido (DECISIONS A4): |%Sim − %Não| entre Sim e Não."""
    return (
        votos.filter(pl.col("voto").is_in(["Sim", "Não"]))
        .group_by("id_votacao", "partido_id")
        .agg(
            (pl.col("voto") == "Sim").sum().alias("sim"),
            (pl.col("voto") == "Não").sum().alias("nao"),
        )
        .with_columns(
            ((pl.col("sim") - pl.col("nao")).abs() / (pl.col("sim") + pl.col("nao"))).alias("rice")
        )
    )


def presenca(votos: pl.DataFrame, votacoes: pl.DataFrame, intervalos: pl.DataFrame) -> pl.DataFrame:
    """Quem deveria ter votado e quem votou, por deputado e votação.

    A Câmara não lista os ausentes. "Esperado" = estava em exercício (intervalos do histórico) no
    momento da votação, ou votou nela (o voto prova o exercício, e o histórico tem lacunas);
    "presente" = registrou Sim, Não, Abstenção ou Obstrução ("Artigo 17" não conta, DECISIONS A3).
    Votações sem data e hora de registro ficam de fora. A coluna `pelo_historico` diz se o
    deputado estava em exercício segundo o histórico (para o relatório de lacunas).
    """
    momentos = votacoes.select(
        "id",
        pl.col("data_hora").str.to_datetime(strict=False).alias("quando"),
    ).drop_nulls("quando")
    esperados = (
        momentos.join(intervalos, how="cross")
        .filter((pl.col("quando") >= pl.col("inicio")) & (pl.col("quando") <= pl.col("fim")))
        .select(pl.col("id").alias("id_votacao"), "id_deputado")
        .unique()
    )
    presentes = (
        votos.filter(pl.col("voto").is_in(list(VOTOS_VALIDOS)))
        .select("id_votacao", "id_deputado")
        .unique()
        .with_columns(pl.lit(True).alias("presente"))
    )
    esperados = esperados.with_columns(pl.lit(True).alias("pelo_historico"))
    so_pelo_voto = presentes.filter(pl.col("id_votacao").is_in(momentos["id"].implode())).join(
        esperados, on=["id_votacao", "id_deputado"], how="anti"
    )
    return pl.concat(
        [
            esperados.join(presentes, on=["id_votacao", "id_deputado"], how="left"),
            so_pelo_voto.with_columns(pl.lit(False).alias("pelo_historico")),
        ],
        how="diagonal",
    ).with_columns(pl.col("presente").fill_null(False))
