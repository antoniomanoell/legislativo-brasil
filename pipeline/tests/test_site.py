import json
from datetime import date

import polars as pl

from congresso.load.site import publicar


def test_publicar_gera_catalogo_momentos_e_agregados(tmp_path):
    eleitos = pl.DataFrame(
        {
            "ano": [2022, 2022],
            "nome": ["ANA MARIA", "BETO"],
            "nome_urna": ["ANA", None],
            "uf": ["SP", "AC"],
            "partido_id": ["pt", "pr"],
            "sigla_na_eleicao": ["PT", "PL"],
            "tse_gerado_em": ["23/10/2026 12:30:18"] * 2,
        }
    )
    fotos = pl.DataFrame(
        {
            "data": [date(2023, 2, 1)],
            "legislatura": [57],
            "nome": ["ANA"],
            "uf": ["SP"],
            "partido_id": ["pt"],
            "sigla_partido": ["PT"],
        }
    )
    ideologia = pl.DataFrame(
        {
            "legislatura": [57],
            "partido_id": ["pt"],
            "pontuacao": [2.761],
            "erro_padrao": [None],
            "n": [501],
            "faixa": ["esquerda"],
            "fonte_id": ["bolognesi"],
            "ano_medicao": [2022],
            "sigla_fonte": ["PT"],
            "escala": ["0 a 10"],
            "nota": [None],
        }
    )
    partidos = pl.DataFrame(
        {
            "partido_id": ["pt", "pr"],
            "sigla": ["PT", "PL"],
            "nome": ["PT", "PL"],
            "observacao": ["", ""],
        }
    )
    renomeacoes = pl.DataFrame(
        {
            "partido_id": ["pr"],
            "sigla_anterior": ["PR"],
            "sigla_nova": ["PL"],
            "data": ["2019-02-09"],
        }
    )
    linhagens = pl.DataFrame(
        schema={
            "de_partido_id": pl.String,
            "para_partido_id": pl.String,
            "tipo": pl.String,
            "data": pl.String,
            "confirmado_no_tse": pl.String,
        }
    )
    catalogo = publicar(eleitos, fotos, ideologia, partidos, renomeacoes, linhagens, tmp_path)

    assert [m["id"] for m in catalogo["momentos"]] == ["eleitos-2022", "2023-02-01"]
    assert catalogo["momentos"][1]["cadeiras"] == 2  # vagas da legislatura = eleitos da eleição
    eleitos_json = json.loads((tmp_path / "momentos" / "eleitos-2022.json").read_text("utf-8"))
    assert eleitos_json[0] == {"nome": "BETO", "uf": "AC", "partido": "pr", "sigla": "PL"}
    assert eleitos_json[1]["nome"] == "ANA"  # nome de urna quando houver
    agregados = json.loads((tmp_path / "agregados.json").read_text("utf-8"))
    assert agregados["eleitos-2022"] == {"pr": 1, "pt": 1}
    ideo = json.loads((tmp_path / "ideologia.json").read_text("utf-8"))
    assert ideo["57"]["pt"]["faixa"] == "esquerda"
    partidos_json = json.loads((tmp_path / "partidos.json").read_text("utf-8"))
    assert partidos_json["pr"]["renomeacoes"][0]["sigla_nova"] == "PL"


def test_publicar_votacoes_formato_compacto(tmp_path):
    from congresso.load.votacoes_site import publicar_votacoes

    votacoes = pl.DataFrame(
        {
            "id": ["1-1"],
            "data": ["2016-10-10"],
            "data_hora": ["2016-10-10T20:00"],
            "descricao": ["Aprovada"],
            "descricao_abertura": ["Votação em primeiro turno."],
            "proposicoes": [["PEC 241/2016"]],
            "aprovacao": ["1"],
            "orientacao_governo": ["Sim"],
            "n_Sim": [1],
            "n_Não": [1],
            "n_Abstenção": [0],
            "n_Obstrução": [0],
            "destaque_pec": [True],
        }
    )
    votos = pl.DataFrame(
        {
            "id_votacao": ["1-1", "1-1", "1-1"],
            "id_deputado": [10, 20, 30],
            "nome": ["Ana", "Beto", "Caio"],
            "uf": ["SP", "RJ", "MG"],
            "voto": ["Sim", "Não", "Artigo 17"],
            "partido_id": ["pt", "psdb", "pmdb"],
        }
    )
    publicar_votacoes(votacoes, votos, tmp_path)
    ano = json.loads((tmp_path / "votacoes" / "ano-2016.json").read_text("utf-8"))
    assert ano["deputados"] == [[10, "Ana", "SP"], [20, "Beto", "RJ"], [30, "Caio", "MG"]]
    assert ano["partidos"] == ["pmdb", "psdb", "pt"]
    v = ano["votacoes"][0]
    assert (v["v"], v["p"]) == ("SN7", "210")
    assert v["pec"] is True and v["placar"] == [1, 1, 0, 0]
    indice = json.loads((tmp_path / "votacoes" / "indice.json").read_text("utf-8"))
    assert "v" not in indice[0]


def test_resultado_vazio_na_fonte_fica_sem_resultado():
    from congresso.load.votacoes_site import _meta

    base = {
        "id": "1-1",
        "data": "2016-10-10",
        "descricao": "Mantido o dispositivo.",
        "descricao_abertura": None,
        "proposicoes": [],
        "orientacao_governo": None,
        "n_Sim": 300,
        "n_Não": 100,
        "n_Abstenção": 0,
        "n_Obstrução": 0,
        "destaque_pec": False,
    }
    assert _meta({**base, "aprovacao": ""})["aprovada"] is None
    assert _meta({**base, "aprovacao": None})["aprovada"] is None
    assert _meta({**base, "aprovacao": "0"})["aprovada"] is False
