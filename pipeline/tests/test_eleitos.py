import zipfile

import polars as pl
import pytest

from congresso.transform.eleitos import COLUNAS_1990, ler_1990, ler_consulta_cand, ler_vagas
from congresso.validate.eleitos import conferir_limites, conferir_referencia, conferir_vagas

CABECALHO = [
    "DT_GERACAO",
    "HH_GERACAO",
    "ANO_ELEICAO",
    "NR_TURNO",
    "SG_UF",
    "DS_CARGO",
    "SQ_CANDIDATO",
    "NR_CANDIDATO",
    "NM_CANDIDATO",
    "NM_URNA_CANDIDATO",
    "NR_CPF_CANDIDATO",
    "DS_SITUACAO_CANDIDATURA",
    "NR_PARTIDO",
    "SG_PARTIDO",
    "SG_FEDERACAO",
    "DS_SIT_TOT_TURNO",
]


def _csv(linhas: list[list[str]]) -> bytes:
    return "\n".join(";".join(f'"{c}"' for c in linha) for linha in linhas).encode("latin-1")


def _cand(uf, nr, nome, partido, sit, cand="DEFERIDO", cargo="DEPUTADO FEDERAL", fed="#NULO#"):
    return [
        "23/10/2026",
        "12:30:18",
        "2026",
        "1",
        uf,
        cargo,
        f"9{nr}",
        nr,
        nome,
        nome.split()[0],
        "12345678900",
        cand,
        nr[:2],
        partido,
        fed,
        sit,
    ]


@pytest.fixture
def zip_2026(tmp_path):
    caminho = tmp_path / "consulta_cand_2026.zip"
    linhas = [
        CABECALHO,
        _cand("SP", "2201", "ANA ELEITA", "PL", "ELEITO POR QP"),
        _cand("SP", "1301", "BETO MEDIA", "PT", "ELEITO POR MÉDIA", fed="FE BRASIL"),
        _cand("SP", "4501", "CAIO SUPLENTE", "PSDB", "SUPLENTE"),
        _cand("SP", "4502", "DORA NAO", "PSDB", "NÃO ELEITO"),
        _cand("SP", "40", "EVA GOVERNADORA", "PSB", "ELEITO", cargo="GOVERNADOR"),
    ]
    with zipfile.ZipFile(caminho, "w") as z:
        z.writestr("consulta_cand_2026_BRASIL.csv", _csv(linhas))
    return caminho


def test_consulta_cand_so_eleitos_a_deputado_federal(zip_2026):
    df = ler_consulta_cand(zip_2026, 2026)
    assert df["nome"].to_list() == ["BETO MEDIA", "ANA ELEITA"]
    assert df["sigla_federacao"].to_list() == ["FE BRASIL", None]
    assert df["tse_gerado_em"][0] == "23/10/2026 12:30:18"


def test_consulta_cand_nao_guarda_dados_pessoais(zip_2026):
    assert not {"cpf", "NR_CPF_CANDIDATO"} & set(ler_consulta_cand(zip_2026, 2026).columns)


def test_substituto_com_mesmo_numero_fica(tmp_path):
    caminho = tmp_path / "consulta_cand_1998.zip"
    linhas = [
        CABECALHO,
        _cand("PR", "4515", "TITULAR QUE RENUNCIOU", "PSDB", "ELEITO", cand="RENÚNCIA"),
        _cand("PR", "4515", "SUBSTITUTO", "PSDB", "ELEITO"),
    ]
    with zipfile.ZipFile(caminho, "w") as z:
        z.writestr("consulta_cand_1998_BRASIL.csv", _csv(linhas))
    assert ler_consulta_cand(caminho, 1998)["nome"].to_list() == ["SUBSTITUTO"]


def test_duplicata_sem_explicacao_para_o_pipeline(tmp_path):
    caminho = tmp_path / "consulta_cand_2002.zip"
    linhas = [
        CABECALHO,
        _cand("RJ", "1111", "UM", "PT", "ELEITO"),
        _cand("RJ", "1111", "DOIS", "PT", "ELEITO"),
    ]
    with zipfile.ZipFile(caminho, "w") as z:
        z.writestr("consulta_cand_2002_BRASIL.csv", _csv(linhas))
    with pytest.raises(ValueError, match="duplicado"):
        ler_consulta_cand(caminho, 2002)


def test_1990_sem_cabecalho(tmp_path):
    def linha(uf, nr, nome, cargo, sit, partido):
        valores = dict.fromkeys(COLUNAS_1990, "#NULO#")
        valores.update(
            DATA_GERACAO="24/4/2014",
            HORA_GERACAO="19:52:11",
            ANO_ELEICAO="1990",
            NUM_TURNO="1",
            SIGLA_UF=uf,
            NUMERO_CAND=nr,
            SQ_CANDIDATO="-3",
            NOME_CANDIDATO=nome,
            DESCRICAO_CARGO=cargo,
            DESC_SIT_CAND_TOT=sit,
            NUMERO_PARTIDO=nr[:2],
            SIGLA_PARTIDO=partido,
        )
        return [valores[c] for c in COLUNAS_1990]

    caminho = tmp_path / "votacao_candidato_uf_1990.zip"
    with zipfile.ZipFile(caminho, "w") as z:
        z.writestr(
            "VOTACAO_CANDIDATO_UF_1990/VOTACAO_CANDIDATO_UF_1990_AC.txt",
            _csv(
                [
                    linha("AC", "1501", "FULANO", "DEPUTADO FEDERAL", "ELEITO", "PMDB"),
                    linha("AC", "1502", "SICRANO", "DEPUTADO FEDERAL", "SUPLENTE", "PMDB"),
                    linha("AC", "11", "BELTRANO", "GOVERNADOR", "ELEITO", "PDS"),
                ]
            ),
        )
        z.writestr("VOTACAO_CANDIDATO_UF_1990/Leia-me.pdf", b"")
    df = ler_1990(caminho)
    assert df.select("ano", "uf", "nome", "sigla_partido").rows() == [
        (1990, "AC", "FULANO", "PMDB")
    ]


def test_vagas_aceita_os_dois_nomes_de_coluna(tmp_path):
    caminho = tmp_path / "consulta_vagas_2010.zip"
    with zipfile.ZipFile(caminho, "w") as z:
        z.writestr(
            "consulta_vagas_2010_BRASIL.csv",
            _csv(
                [
                    ["SG_UF", "DS_CARGO", "QT_VAGAS"],
                    ["AC", "Deputado Federal", "8"],
                    ["AC", "Senador", "1"],
                ]
            ),
        )
    assert ler_vagas(caminho, 2010).rows() == [(2010, "AC", 8)]


def _eleitos(ano, por_uf):
    linhas = [
        {"ano": ano, "uf": uf, "sigla_partido": p}
        for uf, partidos in por_uf.items()
        for p in partidos
    ]
    return pl.DataFrame(
        linhas, schema={"ano": pl.Int16, "uf": pl.String, "sigla_partido": pl.String}
    )


def test_conferir_vagas():
    eleitos = _eleitos(2026, {"AC": ["PL"] * 8, "AL": ["PT"] * 8})
    vagas = pl.DataFrame(
        {"ano": [2026, 2026], "uf": ["AC", "AL"], "vagas": [8, 9]},
        schema={"ano": pl.Int16, "uf": pl.String, "vagas": pl.Int32},
    )
    assert conferir_vagas(eleitos, vagas) == ["2026 AL: 8 eleitos para 9 vagas"]


def test_conferir_limites():
    eleitos = _eleitos(1994, {"AC": ["PL"] * 7, "SP": ["PT"] * 70})
    assert conferir_limites(eleitos, 1994, total=77) == [
        "1994 AC: 7 eleitos, fora do limite de 8 a 70"
    ]


def test_conferir_referencia_marca_tolerancia():
    eleitos = _eleitos(2010, {"SP": ["PP"] * 44 + ["PT"] * 10})
    referencia = pl.DataFrame(
        {"ano": [2010, 2010], "sigla_partido": ["PP", "PT"], "cadeiras": [41, 10]},
        schema={"ano": pl.Int16, "sigla_partido": pl.String, "cadeiras": pl.Int64},
    )
    r = conferir_referencia(eleitos, referencia)
    assert r.select("sigla_partido", "diferenca", "fora_da_tolerancia").rows() == [("PP", 3, True)]
