"""Câmara dos Deputados — Dados Abertos, API v2 (SOURCES.md). Domínio público, citada a fonte.

O histórico datado de partido e exercício só existe a partir da 52ª legislatura (2003); por isso as
fotos de 1º/fev começam em 2003 (DECISIONS, A15).
"""

import json
import time
from pathlib import Path

import httpx

from congresso.extract.http import CABECALHOS
from congresso.paths import BRUTOS

API = "https://dadosabertos.camara.leg.br/api/v2"
PASTA = BRUTOS / "camara"
LEGISLATURAS_COM_HISTORICO = (52, 53, 54, 55, 56, 57)
PAUSA = 0.25  # segundos entre requisições: a API não documenta limite, mas pede retry-after: 30


def _get(cliente: httpx.Client, url: str, params: dict | None = None) -> dict:
    for tentativa in range(1, 4):
        r = cliente.get(url, params=params)
        if r.status_code in (429, 503) and tentativa < 3:
            time.sleep(int(r.headers.get("retry-after", "30")))
            continue
        r.raise_for_status()
        time.sleep(PAUSA)
        return r.json()
    raise RuntimeError(f"Falha ao consultar {url}")


def _cliente() -> httpx.Client:
    return httpx.Client(
        headers={**CABECALHOS, "Accept": "application/json"}, timeout=60, follow_redirects=True
    )


def deputados_da_legislatura(leg: int, *, atualizar: bool = False) -> Path:
    """Lista de quem exerceu mandato na legislatura (todas as páginas), em JSON."""
    destino = PASTA / "deputados" / f"legislatura_{leg}.json"
    if destino.exists() and not atualizar:
        return destino
    dados, pagina = [], 1
    with _cliente() as c:
        while True:
            resposta = _get(
                c,
                f"{API}/deputados",
                {"idLegislatura": leg, "itens": 100, "pagina": pagina, "ordenarPor": "id"},
            )
            dados += resposta["dados"]
            if not any(link["rel"] == "next" for link in resposta.get("links", [])):
                break
            pagina += 1
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    return destino


def historicos(ids: list[int], *, atualizar: bool = False) -> Path:
    """Baixa `/deputados/{id}/historico` de cada deputado (um JSON por id) e devolve a pasta."""
    pasta = PASTA / "historico"
    pasta.mkdir(parents=True, exist_ok=True)
    faltam = [i for i in ids if atualizar or not (pasta / f"{i}.json").exists()]
    if faltam:
        print(f"  baixando o histórico de {len(faltam)} deputados (pausa de {PAUSA}s entre cada)")
    with _cliente() as c:
        for n, i in enumerate(faltam, 1):
            dados = _get(c, f"{API}/deputados/{i}/historico")["dados"]
            (pasta / f"{i}.json").write_text(
                json.dumps(dados, ensure_ascii=False), encoding="utf-8"
            )
            if n % 200 == 0:
                print(f"    {n}/{len(faltam)}")
    return pasta
