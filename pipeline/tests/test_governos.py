from datetime import date

import polars as pl
import pytest

from congresso.paths import MANUAIS
from congresso.transform.governos import base_formal, gabinete_em, ler_gabinetes


def _gabinetes():
    return ler_gabinetes(
        pl.DataFrame(
            {
                "gabinete": ["Lula 1-1", "Lula 1-2", "Bolsonaro-2", "Bolsonaro-4"],
                "inicio": ["2003-01", "2004-01", "2019-11", "2021-02-12"],
                "evento": ["A", "B", "B", "B"],
                "partido_ids": ["pt;pl", "pt;pl;pmdb", None, "prb"],
                "fonte": ["x"] * 4,
            }
        )
    )


def test_gabinete_vigente():
    g = _gabinetes()
    assert gabinete_em(g, date(2003, 2, 1))["gabinete"] == "Lula 1-1"
    assert gabinete_em(g, date(2004, 2, 1))["gabinete"] == "Lula 1-2"
    assert gabinete_em(g, date(2002, 2, 1)) is None


def test_gabinete_sem_partidos():
    assert gabinete_em(_gabinetes(), date(2020, 2, 1))["partidos"] == []


def test_data_exata_resolve_o_mesmo_mes():
    g = _gabinetes()
    assert gabinete_em(g, date(2021, 2, 1))["gabinete"] == "Bolsonaro-2"
    assert gabinete_em(g, date(2021, 2, 12))["gabinete"] == "Bolsonaro-4"


def test_mes_sem_dia_e_ambiguo():
    g = ler_gabinetes(
        pl.DataFrame(
            {
                "gabinete": ["A", "B"],
                "inicio": ["2010-01", "2010-02"],
                "evento": ["A", "B"],
                "partido_ids": ["pt", "pt"],
                "fonte": ["x", "x"],
            }
        )
    )
    with pytest.raises(ValueError, match="mesmo mês"):
        gabinete_em(g, date(2010, 2, 1))


def test_base_formal_conta_as_cadeiras_dos_partidos_com_ministerio():
    cadeiras = pl.DataFrame({"partido_id": ["pt"] * 90 + ["pmdb"] * 80 + ["psdb"] * 70})
    b = base_formal(cadeiras, _gabinetes(), date(2004, 2, 1))
    assert (b["gabinete"], b["cadeiras_base"], b["ocupadas"]) == ("Lula 1-2", 170, 240)


def test_gabinetes_do_ipea_coerentes():
    g = ler_gabinetes(pl.read_csv(MANUAIS / "gabinetes_ipea.csv"))
    assert g.height == 43
    assert g["inicio"].is_sorted()
    partidos = set(pl.read_csv(MANUAIS / "partidos.csv")["partido_id"])
    assert set(g["partidos"].explode().drop_nulls()) <= partidos


def test_curadoria_pos2020_coerente():
    g = ler_gabinetes(pl.read_csv(MANUAIS / "gabinetes_pos2020.csv"))
    partidos = set(pl.read_csv(MANUAIS / "partidos.csv")["partido_id"])
    assert set(g["partidos"].explode().drop_nulls()) <= partidos
    assert not g["so_mes"].any(), "a curadoria precisa de data exata"
    ipea = ler_gabinetes(pl.read_csv(MANUAIS / "gabinetes_ipea.csv"))
    assert g["inicio"].min() > ipea["inicio"].max()
