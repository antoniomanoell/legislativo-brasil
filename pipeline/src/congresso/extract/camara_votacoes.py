"""Votações da Câmara: arquivos em lote dos Dados Abertos (SOURCES.md), um CSV por conjunto e ano.

Voto individual existe de dez/2001 em diante; orientação do Governo, de 2003 em diante (DECISIONS,
sem dados do Cebrap para 1991–2000). Os arquivos são regerados diariamente; o do ano corrente muda.
"""

from pathlib import Path

from congresso.extract.http import baixar
from congresso.paths import BRUTOS

BASE = "https://dadosabertos.camara.leg.br/arquivos"
PASTA = BRUTOS / "camara" / "votacoes"
CONJUNTOS = ("votacoes", "votacoesVotos", "votacoesOrientacoes", "votacoesProposicoes")
PRIMEIRO_ANO = 2001


def arquivo(conjunto: str, ano: int, *, atualizar: bool = False) -> Path:
    nome = f"{conjunto}-{ano}.csv"
    return baixar(f"{BASE}/{conjunto}/csv/{nome}", PASTA / nome, atualizar=atualizar)


def todos(ultimo_ano: int, *, atualizar: bool = False) -> dict[tuple[str, int], Path]:
    """Baixa (ou reaproveita do cache) todos os conjuntos de PRIMEIRO_ANO a `ultimo_ano`. O ano
    corrente é sempre baixado de novo, porque ainda recebe votações."""
    caminhos = {}
    for ano in range(PRIMEIRO_ANO, ultimo_ano + 1):
        for conjunto in CONJUNTOS:
            if conjunto == "votacoesOrientacoes" and ano < 2003:
                continue  # não existe (404) antes de 2003
            caminhos[(conjunto, ano)] = arquivo(
                conjunto, ano, atualizar=atualizar or ano == ultimo_ano
            )
    return caminhos
