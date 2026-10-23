"""TSE — Portal de Dados Abertos (SOURCES.md). Licença CC-BY; os arquivos de candidatos mostram a
situação atual de cada candidato e são regerados continuamente (DECISIONS: "Eleito" = TSE)."""

from pathlib import Path

from congresso.extract.http import baixar
from congresso.paths import BRUTOS

CDN = "https://cdn.tse.jus.br/estatistica/sead/odsele"
PASTA = BRUTOS / "tse"

# Eleições gerais da série (PROJECT.md, D3). 1990 só tem a votação por candidato, sem cabeçalho.
ANOS = (1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022, 2026)


def candidatos(ano: int, *, atualizar: bool = False) -> Path:
    """Zip com os candidatos da eleição: `votacao_candidato_uf` em 1990, `consulta_cand` depois."""
    if ano == 1990:
        nome = "votacao_candidato_uf_1990.zip"
        url = f"{CDN}/votacao_candidato_uf/{nome}"
    else:
        nome = f"consulta_cand_{ano}.zip"
        url = f"{CDN}/consulta_cand/{nome}"
    return baixar(url, PASTA / nome, atualizar=atualizar)


def vagas(ano: int, *, atualizar: bool = False) -> Path:
    """Zip com as vagas por cargo e UF."""
    nome = f"consulta_vagas_{ano}.zip"
    return baixar(f"{CDN}/consulta_vagas/{nome}", PASTA / nome, atualizar=atualizar)
