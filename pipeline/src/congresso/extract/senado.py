"""Senado Federal — Dados Abertos Legislativos (SOURCES.md). Uso permitido citada a fonte.

Senadores por legislatura, mandatos (com os períodos de exercício e a causa de cada afastamento) e
filiações, um JSON por senador em data/raw/senado.
"""

import json
import time
from pathlib import Path

import httpx

from congresso.extract.http import CABECALHOS
from congresso.paths import BRUTOS

API = "https://legis.senado.leg.br/dadosabertos"
PASTA = BRUTOS / "senado"
LEGISLATURAS = tuple(range(49, 58))
PAUSA = 0.3


def _get(cliente: httpx.Client, url: str) -> dict:
    for tentativa in range(1, 5):
        try:
            r = cliente.get(url)
            r.raise_for_status()
            time.sleep(PAUSA)
            return r.json()
        except httpx.HTTPError:
            if tentativa == 4:
                raise
            time.sleep(5 * tentativa)
    raise RuntimeError(url)


def _cliente() -> httpx.Client:
    return httpx.Client(
        headers={**CABECALHOS, "Accept": "application/json"}, timeout=60, follow_redirects=True
    )


def _salvar(destino: Path, dados: dict) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")


def legislaturas(*, atualizar: bool = False) -> dict[int, Path]:
    caminhos = {}
    with _cliente() as c:
        for leg in LEGISLATURAS:
            destino = PASTA / "legislaturas" / f"{leg}.json"
            if atualizar or not destino.exists():
                _salvar(destino, _get(c, f"{API}/senador/lista/legislatura/{leg}"))
            caminhos[leg] = destino
    return caminhos


def codigos(caminhos: dict[int, Path]) -> list[str]:
    """Códigos de todos os senadores (titulares e suplentes) das legislaturas baixadas."""
    vistos: set[str] = set()
    for caminho in caminhos.values():
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        lista = dados["ListaParlamentarLegislatura"]["Parlamentares"]["Parlamentar"]
        for p in lista if isinstance(lista, list) else [lista]:
            vistos.add(p["IdentificacaoParlamentar"]["CodigoParlamentar"])
    return sorted(vistos, key=int)


def senadores(cods: list[str], *, atualizar: bool = False) -> Path:
    """Mandatos e filiações de cada senador (dois JSON por código)."""
    with _cliente() as c:
        for n, cod in enumerate(cods, 1):
            for recurso in ("mandatos", "filiacoes"):
                destino = PASTA / recurso / f"{cod}.json"
                if atualizar or not destino.exists():
                    _salvar(destino, _get(c, f"{API}/senador/{cod}/{recurso}"))
            if n % 100 == 0:
                print(f"  {n}/{len(cods)} senadores")
    return PASTA


def votacoes(ultimo_ano: int, *, atualizar: bool = False) -> Path:
    """Votações de plenário com o voto de cada senador (endpoint /votacao, um ano por consulta) e
    as orientações de liderança (/plenario/votacao/orientacaoBancada), um JSON por ano."""
    with _cliente() as c:
        for ano in range(1991, ultimo_ano + 1):
            for nome, url in (
                ("votacoes", f"{API}/votacao?dataInicio={ano}-01-01&dataFim={ano}-12-31"),
                ("orientacoes", f"{API}/plenario/votacao/orientacaoBancada/{ano}0101/{ano}1231"),
            ):
                destino = PASTA / nome / f"{ano}.json"
                if atualizar or ano == ultimo_ano or not destino.exists():
                    _salvar(destino, _get(c, url))
    return PASTA


def materias(codigos: list[str], *, atualizar: bool = False) -> Path:
    """Detalhe de cada matéria votada (classificação, indexação e norma gerada), um JSON por
    código."""
    with _cliente() as c:
        for n, cod in enumerate(codigos, 1):
            destino = PASTA / "materias" / f"{cod}.json"
            if atualizar or not destino.exists():
                _salvar(destino, _get(c, f"{API}/materia/{cod}"))
            if n % 200 == 0:
                print(f"  {n}/{len(codigos)} matérias")
    return PASTA / "materias"
