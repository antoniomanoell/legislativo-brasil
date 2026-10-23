import polars as pl
import pytest

from congresso.paths import MANUAIS
from congresso.transform.partidos import atribuir_partido


def _ler(nome):
    return pl.read_csv(MANUAIS / nome, infer_schema=False)


def test_tabelas_curadas_sao_coerentes():
    partidos = set(_ler("partidos.csv")["partido_id"])
    assert len(partidos) == _ler("partidos.csv").height, "partido_id repetido"
    assert set(_ler("partidos_tse.csv")["partido_id"]) <= partidos
    linhagens = _ler("linhagens.csv")
    assert set(linhagens["de_partido_id"]) | set(linhagens["para_partido_id"]) <= partidos
    assert set(_ler("renomeacoes.csv")["partido_id"]) <= partidos


def test_um_partido_por_numero_em_cada_eleicao():
    mapa = _ler("partidos_tse.csv")
    assert mapa.select("ano", "nr_partido").is_unique().all()


@pytest.mark.parametrize(
    "arquivo",
    [
        "partidos.csv",
        "partidos_tse.csv",
        "linhagens.csv",
        "renomeacoes.csv",
        "bancadas_referencia.csv",
    ],
)
def test_todo_registro_manual_tem_fonte(arquivo):
    # PROJECT.md, 10.1: todo registro manual tem fonte.
    assert _ler(arquivo)["fonte"].str.strip_chars().str.len_chars().min() > 0


def _mapa():
    return pl.DataFrame(
        {
            "ano": [2014, 2014],
            "nr_partido": ["51", "13"],
            "sigla_tse": ["PATRIOTA", "PT"],
            "partido_id": ["pen", "pt"],
            "sigla_na_eleicao": ["PEN", "PT"],
        },
        schema_overrides={"ano": pl.Int16},
    )


def _eleitos(nr, sigla):
    return pl.DataFrame(
        {"ano": [2014], "nr_partido": [nr], "sigla_partido": [sigla]},
        schema_overrides={"ano": pl.Int16},
    )


def test_sigla_da_epoca_corrige_regravacao_do_tse():
    r = atribuir_partido(_eleitos("51", "PATRIOTA"), _mapa())
    assert r.select("partido_id", "sigla_na_eleicao").row(0) == ("pen", "PEN")


def test_numero_sem_partido_para():
    with pytest.raises(ValueError, match="sem partido"):
        atribuir_partido(_eleitos("99", "XYZ"), _mapa())


def test_sigla_do_tse_mudou_para():
    with pytest.raises(ValueError, match="mudou"):
        atribuir_partido(_eleitos("13", "PTX"), _mapa())
