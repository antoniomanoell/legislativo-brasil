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
            ["idVotacao", "proposicao_siglaTipo", "proposicao_numero", "proposicao_ano"],
            ["1-1", "PEC", "241", "2016"],
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
            "id_votacao": ["1"] * 5,
            "partido_id": ["pt", "pt", "pt", "pt", "psol"],
            "voto": ["Sim", "Sim", "Sim", "Não", "Abstenção"],
        }
    )
    r = rice(votos)
    assert r.select("partido_id", "rice").rows() == [("pt", 0.5)]
