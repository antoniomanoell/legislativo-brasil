import polars as pl
import pytest

from congresso.transform.votacoes import governismo, ler_ano, rice


def _gravar(caminho, linhas):
    caminho.write_text("\n".join(";".join(linha) for linha in linhas), encoding="utf-8")
    return caminho


@pytest.fixture
def arquivos(tmp_path):
    v = _gravar(
        tmp_path / "votacoes.csv",
        [
            [
                "id",
                "dataHoraRegistro",
                "data",
                "siglaOrgao",
                "descricao",
                "ultimaAberturaVotacao_descricao",
                "aprovacao",
            ],
            [
                "1-1",
                "2016-10-10T20:00",
                "2016-10-10",
                "PLEN",
                "Aprovada a PEC em primeiro turno",
                "Votação, em primeiro turno, da PEC",
                "1",
            ],
            ["1-2", "2016-10-10T21:00", "2016-10-10", "PLEN", "Aprovado o requerimento", "", "1"],
            ["2-1", "2016-10-11T10:00", "2016-10-11", "CCJC", "Comissão", "", "1"],
        ],
    )
    vt = _gravar(
        tmp_path / "votos.csv",
        [
            [
                "idVotacao",
                "dataHoraVoto",
                "voto",
                "deputado_id",
                "deputado_nome",
                "deputado_siglaPartido",
                "deputado_siglaUf",
            ],
            ["1-1", "2016-10-10T20:01", "Sim", "1", "Ana", "PT", "SP"],
            ["1-1", "2016-10-10T20:01", "Não", "2", "Beto", "PT", "SP"],
            ["1-1", "2016-10-10T20:01", "Obstrução", "3", "Caio", "PSOL", "RJ"],
            ["1-1", "2016-10-10T20:01", "Artigo 17", "4", "Dora", "PMDB", "RJ"],
            ["2-1", "2016-10-11T10:01", "Sim", "1", "Ana", "PT", "SP"],
        ],
    )
    p = _gravar(
        tmp_path / "props.csv",
        [
            [
                "idVotacao",
                "proposicao_id",
                "proposicao_ementa",
                "proposicao_siglaTipo",
                "proposicao_numero",
                "proposicao_ano",
            ],
            ["1-1", "2088351", " Altera o ADCT. ", "PEC", "241", "2016"],
        ],
    )
    o = _gravar(
        tmp_path / "orient.csv",
        [
            ["idVotacao", "siglaBancada", "orientacao"],
            ["1-1", "Governo", "Sim"],
            ["1-1", "PT", "Não"],
        ],
    )
    return v, vt, p, o


def test_so_plenario_com_voto_individual(arquivos):
    votacoes, votos = ler_ano(*arquivos)
    assert votacoes["id"].to_list() == ["1-1"]  # 1-2 não tem votos; 2-1 é de comissão
    assert votacoes.row(0, named=True)["proposicoes"] == ["PEC 241/2016"]
    assert votacoes.row(0, named=True)["materias"] == [
        {
            "rotulo": "PEC 241/2016",
            "ementa": "Altera o ADCT.",
            "url": "https://www.camara.leg.br/propostas-legislativas/2088351",
        }
    ]
    assert votacoes.row(0, named=True)["orientacao_governo"] == "Sim"
    assert votos.height == 4


def test_governismo_conta_obstrucao_contra_e_ignora_artigo_17(arquivos):
    votacoes, votos = ler_ano(*arquivos)
    g = governismo(votos, votacoes, ["id_deputado"]).sort("id_deputado")
    assert g.select("id_deputado", "com_governo", "votos_considerados").rows() == [
        (1, 1, 1),
        (2, 0, 1),
        (3, 0, 1),
    ]


def test_rice_so_com_sim_e_nao():
    votos = pl.DataFrame(
        {
            "id_votacao": ["1"] * 9,
            "partido_id": ["pt", "pt", "pt", "pt", "psol", "pl", "pl", "pl", "pl"],
            "voto": ["Sim", "Sim", "Sim", "Não", "Abstenção", "Não", "Não", "Não", "Sim"],
        }
    )
    r = rice(votos).sort("partido_id")
    # Mais Não que Sim (pl) também dá 0,5; o Rice fica sempre entre 0 e 1.
    assert r.select("partido_id", "rice").rows() == [("pl", 0.5), ("pt", 0.5)]


def test_presenca_usa_os_periodos_de_exercicio():
    from datetime import datetime

    from congresso.transform.votacoes import presenca

    votacoes = pl.DataFrame(
        {"id": ["a", "b"], "data_hora": ["2008-01-05T10:00", "2008-01-20T10:00"]}
    )
    intervalos = pl.DataFrame(
        {
            "id_deputado": [2, 3],
            "legislatura": [53, 53],
            "inicio": [datetime(2007, 2, 1), datetime(2008, 1, 11)],
            "fim": [datetime(2008, 1, 10), datetime(2011, 1, 31)],
        }
    )
    votos = pl.DataFrame({"id_votacao": ["a", "b"], "id_deputado": [2, 9], "voto": ["Sim", "Não"]})
    p = presenca(votos, votacoes, intervalos).sort("id_votacao", "id_deputado")
    assert p.select("id_votacao", "id_deputado", "presente", "pelo_historico").rows() == [
        ("a", 2, True, True),
        ("b", 3, False, True),
        ("b", 9, True, False),  # votou sem constar do histórico: conta como presente
    ]


def test_destaques_pec():
    from congresso.transform.votacoes import destaques_pec

    votacoes = pl.DataFrame(
        {
            "id": ["a", "b", "c", "d", "e", "f", "g"],
            "tipos": [["PEC"], ["PEC"], ["PEC"], ["PEC"], ["PL"], ["PEC"], ["PEC"]],
            "descricao_abertura": [
                "Votação em segundo turno.",
                "Votação em segundo turno.",
                "Votação, em turno único, do parecer de admissibilidade",
                "Votação, em primeiro turno, da Emenda Aglutinativa nº 2.",
                "Votação em primeiro turno.",
                "Votação, em globo, da admissibilidade dos destaques simples.",
                "Votação em primeiro turno.",
            ],
            "descricao": [
                "Aprovada, em segundo turno, a PEC. Sim: 400",
                "Rejeitado o Requerimento. Sim: 12; não: 349",  # abertura enganosa
                "",
                "",
                "Aprovado, em primeiro turno, o PL",
                "Aprovada, em segundo turno, a Proposta nº 6, ressalvados os destaques. Sim: 370",
                "Aprovado, em primeiro turno, o Substitutivo",
            ],
        }
    )
    excecoes = pl.DataFrame({"id": ["g"], "acao": ["excluir"]})
    assert sorted(destaques_pec(votacoes, excecoes)["id"]) == ["a", "d", "f"]


def test_destaque_pec_senado_exclui_emenda_em_separado_e_mantem_substitutivo():
    from congresso.transform.votacoes import destaque_pec_senado

    v = pl.DataFrame(
        {
            "sigla_materia": ["PEC", "PEC", "PEC", "PEC", "PLS"],
            "descricao": [
                "PEC nº 18, de 2002 (1º turno), ressalvados os destaques.",
                "Emenda nº 1 - CCJ à PEC 1, de 2003 (1º Turno).",
                "Emenda nº 10 - CCJ (Substitutivo) à PEC nº 34, de 2019 (1º Turno)",
                "Requerimento de destaque à PEC 5, de 2010 (2º turno)",
                "Projeto de Lei do Senado nº 1 (1º turno)",
            ],
        }
    )
    assert v.select(destaque_pec_senado())["sigla_materia"].to_list() == [
        True,
        False,
        True,
        False,
        False,
    ]
