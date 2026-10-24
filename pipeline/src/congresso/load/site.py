"""Arquivos JSON que o site consome (web/public/data), gerados de data/processed e data/manual.

- catalogo.json: momentos disponíveis (eleitos de cada eleição; fotos de 1º/fev), legislaturas e
  fontes, com a data de geração.
- momentos/<id>.json: uma linha por cadeira ocupada naquele momento.
- partidos.json: partidos com sigla, nome, renomeações e linhagens.
- ideologia.json: pontuação por legislatura e partido, com fonte, escala e faixa (quando publicada).
- agregados.json: cadeiras por partido em cada momento (gráfico de evolução).
"""

import json
from datetime import UTC, date, datetime
from pathlib import Path

import polars as pl

# Legislatura de cada eleição e período (API da Câmara; 58ª conforme PROJECT.md, 7.1).
LEGISLATURAS = {
    49: (1990, "1991-02-01", "1995-01-31"),
    50: (1994, "1995-02-01", "1999-01-31"),
    51: (1998, "1999-02-01", "2003-01-31"),
    52: (2002, "2003-02-01", "2007-01-31"),
    53: (2006, "2007-02-01", "2011-01-31"),
    54: (2010, "2011-02-01", "2015-01-31"),
    55: (2014, "2015-02-01", "2019-01-31"),
    56: (2018, "2019-02-01", "2023-01-31"),
    57: (2022, "2023-02-01", "2027-01-31"),
    58: (2026, "2027-02-01", "2031-01-31"),
}
LEGISLATURA_DA_ELEICAO = {eleicao: leg for leg, (eleicao, _, _) in LEGISLATURAS.items()}

FONTES = {
    "tse": {
        "nome": "Tribunal Superior Eleitoral — Portal de Dados Abertos",
        "url": "https://dadosabertos.tse.jus.br",
        "licenca": "CC-BY",
    },
    "camara": {
        "nome": "Câmara dos Deputados — Dados Abertos",
        "url": "https://dadosabertos.camara.leg.br",
        "licenca": "domínio público, citada a fonte",
    },
    "bls": {
        "nome": "Zucco & Power, Brazilian Legislative Surveys",
        "citacao": "Zucco, C.; Power, T. J. (2024). Latin American Politics and Society, 66(1).",
        "url": "https://doi.org/10.7910/DVN/6KVTUV",
        "licenca": "CC0",
    },
    "bolognesi": {
        "nome": "Bolognesi, Ribeiro, Codato & Silva",
        "citacao": "Bolognesi, B. et al. (2025). Opinião Pública, 31, e31120.",
        "url": "https://doi.org/10.1590/1807-0191202531120",
        "licenca": "CC-BY 4.0 (artigo); CC0 (dados)",
    },
}


def _gravar(caminho: Path, dados) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(dados, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    caminho.write_text(texto + "\n", encoding="utf-8")


def _deputados(df: pl.DataFrame) -> list[dict]:
    return df.select("nome", "uf", "partido", "sigla").sort("uf", "nome").to_dicts()


def publicar(
    eleitos: pl.DataFrame,
    fotos: pl.DataFrame,
    ideologia: pl.DataFrame,
    partidos: pl.DataFrame,
    renomeacoes: pl.DataFrame,
    linhagens: pl.DataFrame,
    destino: Path,
) -> dict:
    """Grava os JSON em `destino` e devolve o catálogo."""
    momentos = []
    agregados = {}

    for (ano,), grupo in eleitos.group_by("ano", maintain_order=True):
        ident = f"eleitos-{ano}"
        leg = LEGISLATURA_DA_ELEICAO[ano]
        linhas = grupo.select(
            pl.coalesce("nome_urna", "nome").alias("nome"),
            "uf",
            pl.col("partido_id").alias("partido"),
            pl.col("sigla_na_eleicao").alias("sigla"),
        )
        gerado = grupo["tse_gerado_em"].unique().sort().to_list()
        momentos.append(
            {
                "id": ident,
                "tipo": "eleitos",
                "ano": ano,
                "legislatura": leg,
                "rotulo": f"Eleitos em {ano}",
                "cadeiras": grupo.height,
                "ocupadas": grupo.height,
                "fonte": "tse",
                "fonte_gerada_em": gerado,
            }
        )
        _gravar(destino / "momentos" / f"{ident}.json", _deputados(linhas))
        agregados[ident] = dict(linhas.group_by("partido").len().sort("partido").iter_rows())

    total_por_leg = (
        eleitos.group_by("ano")
        .len()
        .with_columns(pl.col("ano").replace_strict(LEGISLATURA_DA_ELEICAO).alias("legislatura"))
    )
    cadeiras_leg = dict(total_por_leg.select("legislatura", "len").iter_rows())
    for (dia,), grupo in fotos.sort("data").group_by("data", maintain_order=True):
        ident = dia.isoformat()
        leg = int(grupo["legislatura"][0])
        linhas = grupo.select(
            "nome",
            "uf",
            pl.col("partido_id").alias("partido"),
            pl.col("sigla_partido").alias("sigla"),
        )
        momentos.append(
            {
                "id": ident,
                "tipo": "exercicio",
                "ano": dia.year,
                "data": ident,
                "legislatura": leg,
                "rotulo": f"Em exercício em 1º/fev/{dia.year}",
                "cadeiras": cadeiras_leg[leg],
                "ocupadas": grupo.height,
                "fonte": "camara",
            }
        )
        _gravar(destino / "momentos" / f"{ident}.json", _deputados(linhas))
        agregados[ident] = dict(linhas.group_by("partido").len().sort("partido").iter_rows())

    pontos = {}
    for r in ideologia.iter_rows(named=True):
        pontos.setdefault(str(r["legislatura"]), {})[r["partido_id"]] = {
            k: r[k]
            for k in (
                "pontuacao",
                "erro_padrao",
                "n",
                "faixa",
                "fonte_id",
                "ano_medicao",
                "sigla_fonte",
                "escala",
                "nota",
            )
        }

    lista_partidos = {}
    for r in partidos.iter_rows(named=True):
        lista_partidos[r["partido_id"]] = {
            "sigla": r["sigla"],
            "nome": r["nome"],
            "observacao": r["observacao"],
            "renomeacoes": renomeacoes.filter(pl.col("partido_id") == r["partido_id"])
            .select("sigla_anterior", "sigla_nova", "data")
            .to_dicts(),
            "origem": linhagens.filter(pl.col("para_partido_id") == r["partido_id"])
            .select(pl.col("de_partido_id").alias("partido"), "tipo", "data", "confirmado_no_tse")
            .to_dicts(),
            "destino": linhagens.filter(pl.col("de_partido_id") == r["partido_id"])
            .select(pl.col("para_partido_id").alias("partido"), "tipo", "data", "confirmado_no_tse")
            .to_dicts(),
        }

    catalogo = {
        "gerado_em": datetime.now(UTC).strftime("%Y-%m-%d"),
        "momentos": sorted(
            momentos, key=lambda m: m.get("data") or f"{m['ano']}-10", reverse=False
        ),
        "legislaturas": {
            str(leg): {"eleicao": e, "inicio": i, "fim": f}
            for leg, (e, i, f) in LEGISLATURAS.items()
        },
        "fontes": FONTES,
    }
    _gravar(destino / "catalogo.json", catalogo)
    _gravar(destino / "partidos.json", lista_partidos)
    _gravar(destino / "ideologia.json", pontos)
    _gravar(destino / "agregados.json", agregados)
    return catalogo


def publicar_governos(
    governos: pl.DataFrame,
    gabinetes: pl.DataFrame,
    base: pl.DataFrame,
    inicio_gabinetes: pl.DataFrame,
    fim_cobertura: str,
    destino: Path,
) -> None:
    """governos.json: presidentes, gabinetes com partidos e base no início, e base em cada foto."""
    no_inicio = {r["gabinete"]: r for r in inicio_gabinetes.iter_rows(named=True)}

    # O governo de cada gabinete vem do nome dado pela fonte ("Temer-1", "FHC 2-3"), não da data:
    # o IPEA só dá o mês, e "mai/2016" começa antes do afastamento de Dilma (12/05/2016).
    prefixos = dict(governos.select("prefixo_gabinete", "governo_id").iter_rows())

    def governo_de_gabinete(nome: str) -> str | None:
        for prefixo, governo in prefixos.items():
            if nome.startswith((f"{prefixo}-", f"{prefixo} ")):
                return governo
        return None

    lista_gabinetes = []
    for g in gabinetes.iter_rows(named=True):
        conf = no_inicio.get(g["gabinete"])
        lista_gabinetes.append(
            {
                "gabinete": g["gabinete"],
                "inicio": g["inicio"].isoformat()[: 7 if g["so_mes"] else 10],
                "evento": g["evento"],
                "partidos": g["partidos"],
                "governo": governo_de_gabinete(g["gabinete"]),
                "fonte": g["fonte"],
                "observacao": g["observacao"],
                "base_no_inicio": None
                if conf is None
                else {
                    "data": str(conf["data_calculo"]),
                    "cadeiras": conf["cadeiras_base"],
                    "em_exercicio": conf["em_exercicio"],
                },
            }
        )
    dados = {
        "cobertura_ate": fim_cobertura,
        "governos": [
            {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in r.items()}
            for r in governos.drop("fonte", "prefixo_gabinete").iter_rows(named=True)
        ],
        "gabinetes": lista_gabinetes,
        "base_por_momento": {
            r["momento"]: {
                "gabinete": r["gabinete"],
                "partidos": r["partidos"],
                "cadeiras_base": r["cadeiras_base"],
                "ocupadas": r["ocupadas"],
                "governo": r["governo_id"],
            }
            for r in base.iter_rows(named=True)
        },
    }
    _gravar(destino / "governos.json", dados)


def publicar_senado(
    eleitos: pl.DataFrame,
    fotos: pl.DataFrame,
    lacunas: pl.DataFrame,
    bases: dict[str, dict],
    destino: Path,
) -> dict:
    """catalogo-senado.json, momentos/senado-*.json e agregados-senado.json (§7.8).

    Eleitos: só os eleitos naquela eleição (1/3 ou 2/3); o restante aparece como "mandato em curso".
    Fotos de 1º/fev: só os anos que fecham 81 cadeiras (DECISIONS); os demais vão em `lacunas`.
    """
    momentos, agregados = [], {}
    for (ano,), grupo in eleitos.group_by("ano", maintain_order=True):
        ident = f"senado-eleitos-{ano}"
        linhas = grupo.select(
            pl.coalesce("nome_urna", "nome").alias("nome"),
            "uf",
            pl.col("partido_id").alias("partido"),
            pl.col("sigla_na_eleicao").alias("sigla"),
        )
        momentos.append(
            {
                "id": ident,
                "tipo": "eleitos",
                "ano": ano,
                "legislatura": LEGISLATURA_DA_ELEICAO[ano],
                "rotulo": f"Eleitos para o Senado em {ano}",
                "cadeiras": 81,
                "ocupadas": grupo.height,
                "em_curso": 81 - grupo.height,
                "fonte": "tse",
            }
        )
        _gravar(destino / "momentos" / f"{ident}.json", _deputados(linhas))
        agregados[ident] = dict(linhas.group_by("partido").len().sort("partido").iter_rows())
    for (dia,), grupo in fotos.sort("data").group_by("data", maintain_order=True):
        ident = f"senado-{dia.isoformat()}"
        linhas = grupo.select(
            "nome", "uf", pl.col("partido_id").alias("partido"), pl.col("sigla").fill_null("")
        )
        momentos.append(
            {
                "id": ident,
                "tipo": "exercicio",
                "ano": dia.year,
                "data": dia.isoformat(),
                "legislatura": int(grupo["legislatura"][0]),
                "rotulo": f"Em exercício em 1º/fev/{dia.year}",
                "cadeiras": 81,
                "ocupadas": grupo.height,
                "fonte": "senado",
                "base": bases.get(dia.isoformat()),
            }
        )
        _gravar(destino / "momentos" / f"{ident}.json", _deputados(linhas))
        agregados[ident] = dict(linhas.group_by("partido").len().sort("partido").iter_rows())
    catalogo = {
        "casa": "senado",
        "momentos": sorted(momentos, key=lambda m: m.get("data") or f"{m['ano']}-10"),
        "lacunas": [
            {"data": r["data"].isoformat(), "motivo": r["motivo"]}
            for r in lacunas.iter_rows(named=True)
        ],
    }
    _gravar(destino / "catalogo-senado.json", catalogo)
    _gravar(destino / "agregados-senado.json", agregados)
    return catalogo


def publicar_2027(
    camara: pl.DataFrame, senado: pl.DataFrame, posicao_em: date, destino: Path
) -> None:
    """congresso-2027.json: composição prevista a partir de 1º/fev/2027 (58ª legislatura).

    `camara`: nome, uf, partido, sigla. `senado`: os mesmos campos mais `origem` ("eleito_2026" ou
    "mandato_ate_2031") e `nota` (suplente, governador eleito ou no 2º turno)."""
    if camara.height != 513:
        raise ValueError(f"Câmara 2027: {camara.height} cadeiras, esperado 513")
    por_uf = senado.group_by("uf").len()
    if senado.height != 81 or por_uf["len"].to_list() != [3] * por_uf.height:
        raise ValueError(f"Senado 2027: {senado.height} cadeiras, esperado 81 com 3 por UF")
    _gravar(
        destino / "congresso-2027.json",
        {
            "legislatura": 58,
            "posicao_em": posicao_em.isoformat(),
            "camara": _deputados(camara),
            "senado": senado.select("nome", "uf", "partido", "sigla", "origem", "nota")
            .sort("uf", "origem", "nome")
            .to_dicts(),
        },
    )
