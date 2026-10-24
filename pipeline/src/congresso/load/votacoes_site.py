"""Votações para o site (web/public/data/votacoes), num formato compacto (DECISIONS: publicação).

- votacoes/ano-AAAA.json: lista de deputados que votaram no ano ([id, nome, uf]), lista de partidos
  e, por votação, os metadados, o voto de cada deputado como um caractere na ordem da lista
  (S=Sim, N=Não, A=Abstenção, O=Obstrução, 7=Artigo 17, .=sem voto) e o partido no momento do voto,
  também um caractere por deputado (índice em base 36 na lista de partidos; . = sem voto).
- votacoes/indice.json: todas as votações (sem os votos), para a lista filtrável.
- indicadores.json: governismo e coesão por partido (ano e governo), governismo e presença por
  deputado (legislatura e governo).
"""

import json
from pathlib import Path

import polars as pl

from congresso.transform.votacoes import governismo, rice

CODIGO = {"Sim": "S", "Não": "N", "Abstenção": "A", "Obstrução": "O", "Artigo 17": "7"}
BASE36 = "0123456789abcdefghijklmnopqrstuvwxyz"


def _gravar(caminho: Path, dados) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(dados, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    caminho.write_text(texto + "\n", encoding="utf-8")


def _meta(r: dict) -> dict:
    return {
        "id": r["id"],
        "data": r["data"],
        # O resultado descreve o que foi votado; a "abertura" repete o item da sessão e pode ser
        # enganosa (ex.: "Votação em segundo turno" num requerimento). Ela só entra se faltar o outro.
        "descricao": (r["descricao"] or r["descricao_abertura"] or "").strip(),
        "proposicoes": r["proposicoes"],
        "aprovada": r["aprovacao"] == "1",
        "orientacao_governo": r["orientacao_governo"],
        "placar": [r["n_Sim"], r["n_Não"], r["n_Abstenção"], r["n_Obstrução"]],
        "pec": r["destaque_pec"],
    }


def publicar_votacoes(votacoes: pl.DataFrame, votos: pl.DataFrame, destino: Path) -> int:
    """Grava os arquivos anuais e o índice; devolve o total de bytes gravados."""
    pasta = destino / "votacoes"
    indice = []
    votacoes = votacoes.with_columns(pl.col("data").str.slice(0, 4).cast(pl.Int32).alias("ano"))
    for (ano,), vs in votacoes.sort("data_hora").group_by("ano", maintain_order=True):
        do_ano = votos.filter(pl.col("id_votacao").is_in(vs["id"].implode()))
        deputados = (
            do_ano.group_by("id_deputado")
            .agg(pl.col("nome").last(), pl.col("uf").last())
            .sort("nome", "id_deputado")
        )
        posicao = {d: i for i, d in enumerate(deputados["id_deputado"])}
        partidos = sorted(do_ano["partido_id"].unique().to_list())
        if len(partidos) > len(BASE36):
            raise ValueError(f"{ano}: mais partidos que caracteres disponíveis")
        indice_partido = {p: BASE36[i] for i, p in enumerate(partidos)}
        por_votacao = {}
        for (id_v,), grupo in do_ano.group_by("id_votacao"):
            v = ["."] * len(posicao)
            p = ["."] * len(posicao)
            for d, voto, partido in grupo.select("id_deputado", "voto", "partido_id").iter_rows():
                i = posicao[d]
                v[i] = CODIGO.get(voto, ".")
                p[i] = indice_partido[partido]
            por_votacao[id_v] = {"v": "".join(v), "p": "".join(p)}
        lista = []
        for r in vs.iter_rows(named=True):
            m = _meta(r)
            indice.append(m)
            lista.append({**m, **por_votacao[r["id"]]})
        _gravar(
            pasta / f"ano-{ano}.json",
            {
                "deputados": deputados.select("id_deputado", "nome", "uf").rows(),
                "partidos": partidos,
                "votacoes": lista,
            },
        )
    _gravar(pasta / "indice.json", indice)
    return sum(f.stat().st_size for f in pasta.glob("*.json"))


def _arred(x: float | None, casas: int = 4) -> float | None:
    return None if x is None else round(x, casas)


def publicar_indicadores(
    votos: pl.DataFrame,
    votacoes: pl.DataFrame,
    presenca: pl.DataFrame,
    governos: pl.DataFrame,
    destino: Path,
) -> None:
    """indicadores.json: governismo (A8), coesão (A4) e presença por partido e deputado."""

    def governo_de(coluna: str) -> pl.Expr:
        expr = pl.lit(None, pl.String)
        for g in governos.iter_rows(named=True):
            expr = (
                pl.when((pl.col(coluna) >= g["inicio"]) & (pl.col(coluna) <= g["fim"]))
                .then(pl.lit(g["governo_id"]))
                .otherwise(expr)
            )
        return expr

    votos = votos.with_columns(governo_de("data").alias("governo"))
    datas = votacoes.select(
        "id",
        pl.col("data").str.to_date(),
        pl.col("data").str.slice(0, 4).cast(pl.Int32).alias("ano"),
    ).with_columns(governo_de("data").alias("governo"))
    r = rice(votos).join(datas, left_on="id_votacao", right_on="id")

    partidos: dict = {}
    for chave in ("ano", "governo"):
        g = governismo(votos, votacoes, ["partido_id", chave])
        c = r.group_by("partido_id", chave).agg(
            pl.col("rice").mean().alias("rice"), pl.len().alias("votacoes_rice")
        )
        for linha in g.join(c, on=["partido_id", chave], how="full", coalesce=True).iter_rows(
            named=True
        ):
            if linha[chave] is None:
                continue
            partidos.setdefault(linha["partido_id"], {}).setdefault(f"{chave}s", {})[
                str(linha[chave])
            ] = {
                "governismo": _arred(linha["governismo"]),
                "votos": linha["votos_considerados"],
                "votacoes_governo": linha["votacoes"],
                "rice": _arred(linha["rice"]),
                "votacoes_rice": linha["votacoes_rice"],
            }

    deputados: dict = {}
    ident = votos.group_by("id_deputado").agg(
        pl.col("nome").last(), pl.col("uf").last(), pl.col("data").min().alias("primeiro_voto")
    )
    filiacoes = (
        votos.sort("data")
        .group_by("id_deputado", "partido_id", maintain_order=True)
        .agg(pl.col("data").min().alias("de"), pl.col("data").max().alias("ate"))
    )
    for d in ident.iter_rows(named=True):
        deputados[str(d["id_deputado"])] = {"nome": d["nome"], "uf": d["uf"], "partidos": []}
    for f in filiacoes.sort("de").iter_rows(named=True):
        deputados[str(f["id_deputado"])]["partidos"].append(
            [f["partido_id"], f["de"].isoformat(), f["ate"].isoformat()]
        )
    for chave in ("legislatura", "governo"):
        g = governismo(votos, votacoes, ["id_deputado", chave])
        for linha in g.iter_rows(named=True):
            if linha[chave] is None:
                continue
            deputados[str(linha["id_deputado"])].setdefault(f"{chave}s", {})[str(linha[chave])] = {
                "governismo": _arred(linha["governismo"]),
                "votos": linha["votos_considerados"],
            }
    pres = (
        presenca.join(votos.select("id_votacao", "legislatura").unique(), on="id_votacao")
        .group_by("id_deputado", "legislatura")
        .agg(pl.col("presente").sum().alias("presente"), pl.len().alias("esperado"))
    )
    for linha in pres.iter_rows(named=True):
        alvo = deputados.get(str(linha["id_deputado"]))
        if alvo is None:
            continue
        item = alvo.setdefault("legislaturas", {}).setdefault(str(linha["legislatura"]), {})
        item["presenca"] = _arred(linha["presente"] / linha["esperado"])
        item["votacoes_esperadas"] = linha["esperado"]
    # PROJECT.md 10.1: governismo, coesão e presença entre 0 e 1.
    valores = [
        v
        for grupo in (*partidos.values(), *deputados.values())
        for periodos in grupo.values()
        if isinstance(periodos, dict)
        for item in periodos.values()
        for k, v in item.items()
        if k in ("governismo", "rice", "presenca") and v is not None
    ]
    fora = [v for v in valores if not 0 <= v <= 1]
    if fora:
        raise ValueError(f"Indicadores fora de [0, 1]: {fora[:5]}")
    _gravar(destino / "indicadores.json", {"partidos": partidos, "deputados": deputados})
