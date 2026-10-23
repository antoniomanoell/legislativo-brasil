from datetime import date
from itertools import pairwise

import polars as pl
import pytest

from congresso.paths import MANUAIS
from congresso.transform.partidos import atribuir_partido, atribuir_partido_camara


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


def _mapa_camara():
    return pl.DataFrame(
        {
            "sigla_camara": ["PL", "PL", "PT"],
            "valido_desde": [None, "2019-02-09", None],
            "valido_ate": ["2006-12-18", None, None],
            "partido_id": ["pl", "pr", "pt"],
        },
        schema_overrides={"valido_desde": pl.String, "valido_ate": pl.String},
    )


def _fotos(*linhas):
    return pl.DataFrame(
        [{"data": date.fromisoformat(d), "sigla_partido": s} for d, s in linhas],
    )


def test_mesma_sigla_partidos_diferentes_conforme_a_data():
    r = atribuir_partido_camara(_fotos(("2005-02-01", "PL"), ("2020-02-01", "PL")), _mapa_camara())
    assert r["partido_id"].to_list() == ["pl", "pr"]


def test_sigla_fora_do_periodo_para():
    with pytest.raises(ValueError, match="sem partido único"):
        atribuir_partido_camara(_fotos(("2010-02-01", "PL")), _mapa_camara())


def test_sigla_desconhecida_para():
    with pytest.raises(ValueError, match="sem partido único"):
        atribuir_partido_camara(_fotos(("2010-02-01", "XYZ")), _mapa_camara())


def test_mapa_da_camara_nao_tem_periodos_sobrepostos():
    mapa = _ler("partidos_camara.csv").with_columns(
        pl.col("valido_desde").str.to_date().fill_null(date(1900, 1, 1)),
        pl.col("valido_ate").str.to_date().fill_null(date(2999, 12, 31)),
    )
    for sigla, grupo in mapa.group_by("sigla_camara"):
        periodos = sorted(grupo.select("valido_desde", "valido_ate").rows())
        for (_, fim), (inicio, _) in pairwise(periodos):
            assert fim < inicio, sigla
