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
URL_PROPOSICAO = "https://www.camara.leg.br/propostas-legislativas/"


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
        .sort("rotulo")
        .group_by("idVotacao")
        .agg(
            pl.col("rotulo").unique().sort().alias("proposicoes"),
            pl.col("proposicao_siglaTipo").unique().alias("tipos"),
            # O que está sendo votado: ementa e página de cada proposição no portal da Câmara.
            pl.struct(
                pl.col("rotulo"),
                pl.col("proposicao_ementa").str.strip_chars().alias("ementa"),
                (URL_PROPOSICAO + pl.col("proposicao_id")).alias("url"),
            )
            .unique(maintain_order=True)
            .alias("materias"),
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
            # Inteiros com sinal: com contagens sem sinal, Sim − Não "dá a volta" quando Não > Sim.
            (pl.col("voto") == "Sim").sum().cast(pl.Int64).alias("sim"),
            (pl.col("voto") == "Não").sum().cast(pl.Int64).alias("nao"),
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


# Destaque objetivo de PEC (PROJECT.md 7.7; DECISIONS A5): votação de PEC em 1º ou 2º turno que
# não é destaque, requerimento, recurso nem admissibilidade. O texto usado é o do RESULTADO
# (`descricao`, ex.: "Aprovada, em segundo turno, a Proposta..."): o da abertura repete o item da
# sessão enquanto se votam requerimentos (ex.: PEC 6/2019, 06/08/2019). "Emenda" não exclui: a
# palavra está em "proposta de emenda à Constituição".
TURNO = r"(primeiro|segundo|1[ºo°]|2[ºo°]) turno"
NAO_MERITO = r"destaque|dtq|dvs|requerimento|recurso|admissibilidade|turno [úu]nico"
# Senado (A5): votação em separado de emenda, destaque ou requerimento começa pelo nome do objeto
# ("Emenda nº 1 - CCJ à PEC 1, de 2003 (1º Turno)"); substitutivo à PEC é o texto de mérito e fica.
NAO_MERITO_SENADO = r"^\s*(emendas?|requerimentos?|destaques?|dtq)\b"


def destaques_pec(votacoes: pl.DataFrame, excecoes: pl.DataFrame) -> pl.DataFrame:
    """Ids das votações de mérito de PEC; `excecoes` (id, acao) é a revisão manual."""
    texto = (
        pl.coalesce(pl.col("descricao").replace("", None), pl.col("descricao_abertura"))
        .fill_null("")
        .str.to_lowercase()
        # "ressalvados os destaques" é a fórmula da votação de mérito, não um destaque.
        .str.replace_all(r"ressalvad[oa]s?,? (os |as |o |a )?(destaques?|emendas?)", "")
    )
    regra = votacoes.filter(
        pl.col("tipos").list.contains("PEC")
        & texto.str.contains(TURNO)
        & ~texto.str.contains(NAO_MERITO)
    ).select("id")
    incluir = excecoes.filter(pl.col("acao") == "incluir").select("id")
    excluir = excecoes.filter(pl.col("acao") == "excluir")["id"]
    return pl.concat([regra, incluir]).unique().filter(~pl.col("id").is_in(excluir.implode()))


def destaque_pec_senado() -> pl.Expr:
    """Votação de mérito de PEC no Senado: matéria PEC, turno na descrição e não ser votação em
    separado de emenda, destaque ou requerimento (A5)."""
    texto = pl.col("descricao").fill_null("").str.to_lowercase()
    # Emenda substitutiva troca o texto inteiro da PEC: é a votação de mérito, como o substitutivo.
    substitutivo = texto.str.contains("substitut")
    return (
        (pl.col("sigla_materia") == "PEC")
        & texto.str.contains(TURNO)
        & (~texto.str.contains(NAO_MERITO_SENADO) | substitutivo)
    )
