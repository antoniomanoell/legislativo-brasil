import json
from datetime import date

import pytest

from congresso.transform.congresso_2027 import (
    afastamento_definitivo,
    cadeiras_ate_2031,
    normalizar,
)
from congresso.ufs import UFS_27


def test_normalizar_casa_nomes_do_senado_e_do_tse():
    assert normalizar(" José  Renan Vasconcelos ") == normalizar("JOSE RENAN VASCONCELOS")


def test_renuncia_e_definitiva_afastamento_nao():
    assert afastamento_definitivo("Renúncia")
    assert not afastamento_definitivo("Afastamento do exercício")
    assert not afastamento_definitivo(None)


def _mandato(uf, suplente, exercicios):
    return {
        "UfParlamentar": uf,
        "DescricaoParticipacao": "Titular",
        "SegundaLegislaturaDoMandato": {"DataFim": "2031-01-31"},
        "Suplentes": {
            "Suplente": [
                {
                    "DescricaoParticipacao": "1º Suplente",
                    "CodigoParlamentar": suplente,
                    "NomeParlamentar": f"Sup {uf}",
                }
            ]
        },
        "Exercicios": {"Exercicio": exercicios},
    }


def _gravar(pasta, codigo, nome, mandato):
    (pasta / "mandatos" / f"{codigo}.json").write_text(
        json.dumps(
            {
                "MandatoParlamentar": {
                    "Parlamentar": {"Nome": nome, "Mandatos": {"Mandato": mandato}}
                }
            }
        ),
        encoding="utf-8",
    )


@pytest.fixture
def pasta(tmp_path):
    (tmp_path / "mandatos").mkdir()
    for uf in UFS_27:
        ex = [{"DataInicio": "2023-02-01"}]
        if uf == "MA":  # titular renunciou; o suplente assumiu
            ex = [
                {
                    "DataInicio": "2023-02-01",
                    "DataFim": "2024-02-20",
                    "DescricaoCausaAfastamento": "Renúncia",
                }
            ]
            _gravar(
                tmp_path,
                "S-MA",
                "Sup MA",
                {
                    "UfParlamentar": "MA",
                    "DescricaoParticipacao": "1º Suplente",
                    "SegundaLegislaturaDoMandato": {"DataFim": "2031-01-31"},
                    "Exercicios": {"Exercicio": [{"DataInicio": "2024-02-21"}]},
                },
            )
        _gravar(tmp_path, f"T-{uf}", f"Titular {uf}", _mandato(uf, f"S-{uf}", ex))
    return tmp_path


def test_ocupante_da_cadeira_ate_2031(pasta):
    c = cadeiras_ate_2031(pasta, date(2026, 10, 24))
    assert c.height == 27
    ma = c.filter(c["uf"] == "MA").row(0, named=True)
    assert ma["ocupante_codigo"] == "S-MA" and ma["causa_afastamento_titular"] == "Renúncia"
    sp = c.filter(c["uf"] == "SP").row(0, named=True)
    assert sp["ocupante_codigo"] == "T-SP" and sp["primeiro_suplente_codigo"] == "S-SP"


def test_uf_sem_ocupante_para(pasta):
    (pasta / "mandatos" / "T-AC.json").unlink()
    with pytest.raises(ValueError, match="um titular por UF"):
        cadeiras_ate_2031(pasta, date(2026, 10, 24))
