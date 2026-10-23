import polars as pl
import pytest

from congresso.paths import MANUAIS
from congresso.transform.ideologia import conferir, de_bls, de_bolognesi, faixa


@pytest.mark.parametrize(
    ("valor", "esperada"),
    [
        (0.525, "extrema-esquerda"),
        (1.5, "extrema-esquerda"),
        (1.51, "esquerda"),
        (4.49, "centro-esquerda"),
        (4.5, "centro"),
        (5.51, "centro-direita"),
        (7.151, "direita"),  # PSD 2022: a média ponderada publicada dá direita
        (8.5, "direita"),
        (8.584, "extrema-direita"),
    ],
)
def test_faixas_pelos_cortes_publicados(valor, esperada):
    assert faixa(valor) == esperada


def _siglas():
    return pl.DataFrame(
        {
            "fonte_id": ["bls", "bls", "bls", "bolognesi"],
            "ano_medicao": [1993, 1993, 2021, 2022],
            "sigla_fonte": ["PP", "PP", "PT", "PSD"],
            "partido_id": ["pds", "ppr", "pt", "psd2011"],
            "observacao": ["linhagem", "", "", ""],
        },
        schema_overrides={"ano_medicao": pl.Int16},
    )


def test_bls_sem_rotulo_e_na_legislatura_da_onda():
    est = pl.DataFrame(
        {
            "year": [1993, 2021, 2021],
            "party.or.pres": ["PP", "PT", "BOLSONARO"],
            "ideo": [0.7, -0.69, 0.87],
            "ideo.se": [0.04, 0.03, 0.04],
        }
    )
    r = de_bls(est, _siglas()).sort("partido_id")
    assert r.select("legislatura", "partido_id", "pontuacao").rows() == [
        (49, "pds", 0.7),
        (49, "ppr", 0.7),
        (56, "pt", -0.69),
    ]
    assert r["faixa"].is_null().all()


def test_bolognesi_usa_media_ponderada_e_marca_a_58():
    tabela = pl.DataFrame(
        {
            "sigla_fonte": ["PSD"],
            "media_2022": [6.94],
            "media_ponderada": [7.151],
            "faixa_publicada": ["direita"],
            "n_validos": [443],
        }
    )
    r = de_bolognesi(tabela, _siglas()).sort("legislatura")
    assert r.select("legislatura", "pontuacao", "faixa").rows() == [
        (57, 7.151, "direita"),
        (58, 7.151, "direita"),
    ]
    assert r["nota"][1].startswith("medição de 2022")
    assert conferir(r) == []


def test_conferir_acusa_faixa_que_nao_bate_com_os_cortes():
    tabela = pl.DataFrame(
        {
            "sigla_fonte": ["PSD"],
            "media_2022": [6.94],
            "media_ponderada": [6.94],
            "faixa_publicada": ["direita"],
            "n_validos": [443],
        }
    )
    assert conferir(de_bolognesi(tabela, _siglas()))


def test_toda_sigla_de_bolognesi_mapeada_existe_na_tabela():
    tabela = pl.read_csv(MANUAIS / "bolognesi_2022.csv")
    siglas = pl.read_csv(MANUAIS / "ideologia_siglas.csv").filter(pl.col("fonte_id") == "bolognesi")
    assert set(siglas["sigla_fonte"]) <= set(tabela["sigla_fonte"])
