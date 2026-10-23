"""Caminhos do repositório, a partir da raiz (o pipeline roda de qualquer pasta)."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
DADOS = RAIZ / "data"
BRUTOS = DADOS / "raw"
MANUAIS = DADOS / "manual"
PROCESSADOS = DADOS / "processed"
PUBLICADOS = RAIZ / "web" / "public" / "data"
RELATORIOS = RAIZ / "reports"
