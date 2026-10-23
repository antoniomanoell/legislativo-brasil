"""Fotos da Câmara em 1º de fevereiro de cada ano, de 2003 em diante (PROJECT.md, 7.2; D13).

Em exercício na data = o último evento do histórico da Câmara até o fim do dia 1º/fev, na
legislatura vigente, tem situação "Exercício". O partido é o desse mesmo evento. Contar o fim do
dia faz a foto de um ano de posse (2003, 2007, ...) mostrar a composição já empossada.
"""

import json
from datetime import date, datetime
from pathlib import Path

import polars as pl

EM_EXERCICIO = "Exercício"

# Registros artificiais que a API cria para todas as legislaturas, com data de 2023-02-01.
ARTIFICIAL = "Nome no início da legislatura"

# Início das legislaturas com histórico datado (API /legislaturas).
INICIO_LEGISLATURA = {
    52: date(2003, 2, 1),
    53: date(2007, 2, 1),
    54: date(2011, 2, 1),
    55: date(2015, 2, 1),
    56: date(2019, 2, 1),
    57: date(2023, 2, 1),
}


def legislatura_em(dia: date) -> int:
    vigentes = [leg for leg, ini in INICIO_LEGISLATURA.items() if ini <= dia]
    if not vigentes:
        raise ValueError(f"{dia} é anterior à 52ª legislatura: sem histórico datado")
    return max(vigentes)


def ler_eventos(pasta: Path) -> pl.DataFrame:
    """Eventos datados de todos os históricos baixados, sem os registros artificiais."""
    linhas = []
    for arquivo in sorted(pasta.glob("*.json")):
        id_dep = int(arquivo.stem)
        for r in json.loads(arquivo.read_text(encoding="utf-8")):
            if r["idLegislatura"] not in INICIO_LEGISLATURA:
                continue
            if (r.get("descricaoStatus") or "").startswith(ARTIFICIAL):
                continue
            linhas.append(
                {
                    "id_deputado": id_dep,
                    "legislatura": r["idLegislatura"],
                    "data_hora": datetime.fromisoformat(r["dataHora"]),
                    "nome": r["nomeEleitoral"] or r["nome"],
                    "sigla_partido": r["siglaPartido"],
                    "uf": r["siglaUf"],
                    "situacao": r["situacao"],
                    "condicao": r["condicaoEleitoral"],
                    "descricao": r["descricaoStatus"],
                }
            )
    return pl.DataFrame(linhas).with_row_index("ordem")


def _ultimo(eventos: pl.DataFrame) -> pl.DataFrame:
    # Eventos no mesmo instante: vale a ordem em que a API os lista (a última linha).
    return (
        eventos.sort("id_deputado", "data_hora", "ordem")
        .group_by("id_deputado", maintain_order=True)
        .last()
    )


def foto(eventos: pl.DataFrame, dia: date) -> pl.DataFrame:
    """Deputados em exercício no fim do dia `dia`, com o partido daquele momento.

    Troca de partido ou de nome não muda o exercício: a API registra essas trocas também para quem
    está fora do mandato, às vezes com data anterior ao início da legislatura e situação
    "Exercício" (ex.: id 74140, 31/03/2022, na 57ª). Por isso o exercício vem só dos demais
    eventos, a partir do início da legislatura, e o partido vem do último evento de qualquer tipo.
    """
    leg = legislatura_em(dia)
    limite = datetime.combine(dia, datetime.max.time())
    ate_o_dia = eventos.filter((pl.col("legislatura") == leg) & (pl.col("data_hora") <= limite))
    troca = pl.col("descricao").str.starts_with("Alteração de partido") | pl.col(
        "descricao"
    ).str.starts_with("Alteração de nome")
    inicio = datetime.combine(INICIO_LEGISLATURA[leg], datetime.min.time())
    situacao = _ultimo(ate_o_dia.filter(~troca & (pl.col("data_hora") >= inicio)))
    partido = _ultimo(ate_o_dia).select("id_deputado", "nome", "uf", "sigla_partido")
    return (
        situacao.filter(pl.col("situacao") == EM_EXERCICIO)
        .select("id_deputado", "condicao")
        .join(partido, on="id_deputado")
        .select(
            pl.lit(dia).alias("data"),
            pl.lit(leg).alias("legislatura"),
            "id_deputado",
            "nome",
            "uf",
            "sigla_partido",
            "condicao",
        )
        .sort("uf", "nome")
    )
