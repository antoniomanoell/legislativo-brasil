from datetime import date

import polars as pl
import pytest

from congresso.paths import MANUAIS
from congresso.transform.senado import conferir, em_exercicio, partido_na_data
from congresso.ufs import UFS_27


def _exercicios(n_por_uf=3, extra=None):
    linhas = [
        {
            "codigo": f"{uf}{i}",
            "nome": f"S {uf}{i}",
            "uf": uf,
            "inicio": date(2019, 2, 1),
            "fim": None,
        }
        for uf in UFS_27
        for i in range(n_por_uf)
    ]
    return pl.DataFrame(linhas + (extra or []))


def test_foto_que_fecha():
    assert conferir(em_exercicio(_exercicios(), date(2020, 2, 1))) is None


def test_foto_com_suplente_sem_registro_vira_lacuna():
    ex = _exercicios().filter(pl.col("codigo") != "GO0")
    assert "80 senadores" in conferir(em_exercicio(ex, date(2020, 2, 1)))


def test_foto_com_sobreposicao_vira_lacuna():
    extra = [
        {"codigo": "MTx", "nome": "Suplente", "uf": "MT", "inicio": date(2019, 6, 1), "fim": None}
    ]
    motivo = conferir(em_exercicio(_exercicios(extra=extra), date(2020, 2, 1)))
    assert motivo and "82" in motivo


def test_partido_na_data_por_filiacao_datada():
    foto = pl.DataFrame({"codigo": ["1", "2", "3"], "nome": ["A", "B", "C"], "uf": ["SP"] * 3})
    filiacoes = pl.DataFrame(
        {
            "codigo": ["1", "1", "2"],
            "sigla": ["PT", "MDB", "PL"],
            "inicio": [date(2011, 1, 27), date(2015, 9, 25), date(2010, 1, 1)],
            "fim": [date(2015, 5, 5), None, None],
        }
    )
    mapa = pl.read_csv(MANUAIS / "partidos_senado.csv", infer_schema=False)
    r = partido_na_data(foto, filiacoes, mapa, date(2013, 2, 1)).sort("codigo")
    # "PL" em 2013 é o PR, gravado pela API com a sigla atual.
    assert r["partido_id"].to_list() == ["pt", "pr", "nao_informado"]
    r = partido_na_data(foto, filiacoes, mapa, date(2016, 2, 1)).sort("codigo")
    assert r["partido_id"].to_list()[0] == "pmdb"


def test_sigla_desconhecida_para():
    foto = pl.DataFrame({"codigo": ["1"], "nome": ["A"], "uf": ["SP"]})
    filiacoes = pl.DataFrame(
        {"codigo": ["1"], "sigla": ["XYZ"], "inicio": [date(2010, 1, 1)], "fim": [None]},
        schema_overrides={"fim": pl.Date},
    )
    mapa = pl.read_csv(MANUAIS / "partidos_senado.csv", infer_schema=False)
    with pytest.raises(ValueError, match="XYZ"):
        partido_na_data(foto, filiacoes, mapa, date(2013, 2, 1))
