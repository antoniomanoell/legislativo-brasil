import json
from datetime import date

import pytest

from congresso.transform.fotos import foto, legislatura_em, ler_eventos


def _ev(data_hora, leg, partido, situacao, descricao="", uf="PR", nome="FULANO"):
    return {
        "dataHora": data_hora,
        "idLegislatura": leg,
        "nome": nome,
        "nomeEleitoral": nome,
        "siglaPartido": partido,
        "siglaUf": uf,
        "situacao": situacao,
        "condicaoEleitoral": "Titular",
        "descricaoStatus": descricao,
    }


@pytest.fixture
def pasta(tmp_path):
    historicos = {
        # Titular que troca de partido em 2007 (PFL → DEM) e cumpre o mandato.
        1: [
            _ev("2007-02-01T00:00", 53, "PFL", "Exercício", "Entrada - Posse"),
            _ev("2007-04-23T00:00", 53, "DEM", "Exercício", "Alteração de partido"),
            _ev("2011-01-31T23:59", 53, "DEM", "FIM_MANDATO", "Saída - Término da Legislatura"),
            _ev("2023-02-01T00:00", 53, "DEM", None, "Nome no início da legislatura / Partido"),
        ],
        # Titular que se licencia em 2008 para ser secretário de Estado.
        2: [
            _ev("2007-02-01T00:00", 53, "PT", "Exercício", "Entrada - Posse", nome="BELTRANO"),
            _ev("2008-01-10T00:00", 53, "PT", "Licença", "Secretário de Estado", nome="BELTRANO"),
        ],
        # Suplente que assume no lugar do licenciado.
        3: [
            _ev("2008-01-11T00:00", 53, "PT", "Exercício", "Posse de Suplente", nome="CICLANO"),
        ],
        # Convocado que ainda não tomou posse.
        4: [_ev("2008-01-30T00:00", 53, "PSB", "CONVOCADO", "Convocação", nome="DORA")],
    }
    for i, eventos in historicos.items():
        (tmp_path / f"{i}.json").write_text(json.dumps(eventos), encoding="utf-8")
    return tmp_path


def test_ignora_registros_artificiais(pasta):
    eventos = ler_eventos(pasta)
    assert not eventos["descricao"].str.starts_with("Nome no início").any()


def test_foto_no_dia_da_posse_mostra_os_empossados(pasta):
    f = foto(ler_eventos(pasta), date(2007, 2, 1))
    assert f.select("id_deputado", "sigla_partido").sort("id_deputado").rows() == [
        (1, "PFL"),
        (2, "PT"),
    ]


def test_foto_usa_o_partido_da_data_e_troca_licenciado_por_suplente(pasta):
    f = foto(ler_eventos(pasta), date(2008, 2, 1))
    assert f.select("id_deputado", "sigla_partido").sort("id_deputado").rows() == [
        (1, "DEM"),
        (3, "PT"),
    ]


def test_legislatura_vigente():
    assert legislatura_em(date(2007, 2, 1)) == 53
    assert legislatura_em(date(2007, 1, 31)) == 52
    with pytest.raises(ValueError):
        legislatura_em(date(2002, 2, 1))
