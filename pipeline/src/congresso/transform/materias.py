"""Detalhes oficiais das proposições votadas, para a página de cada votação: assuntos (indexação
feita pela própria Casa), temas (classificação do Senado), inteiro teor e norma gerada.

Nenhum resumo é escrito pelo projeto: só textos e classificações publicados pela Câmara e pelo
Senado (DECISIONS: "O que foi votado").
"""

import json
import re
from pathlib import Path

from congresso.transform.senado import URL_MATERIA
from congresso.transform.votacoes import URL_PROPOSICAO


def _limpar(texto: str | None) -> str | None:
    """Espaços normalizados, sem hífen invisível nem o "_" que a Câmara põe antes de grupos."""
    if not texto:
        return None
    texto = texto.replace("­", "").replace("_", "")
    texto = re.sub(r"\s*,\s*", ", ", texto)
    texto = re.sub(r"\s+", " ", texto).strip(" ,.")
    return texto or None


def detalhes_camara(pasta: Path, ids: list[str]) -> dict[str, dict]:
    """URL da proposição no portal → {assuntos, inteiro_teor}."""
    saida = {}
    for id_ in ids:
        arquivo = pasta / f"{id_}.json"
        if not arquivo.exists():
            continue
        d = json.loads(arquivo.read_text(encoding="utf-8"))
        saida[URL_PROPOSICAO + id_] = {
            "assuntos": _limpar(d.get("keywords")),
            "inteiro_teor": d.get("urlInteiroTeor") or None,
        }
    return saida


def _lista(x) -> list:
    return x if isinstance(x, list) else ([] if x is None else [x])


def detalhes_senado(pasta: Path, codigos: list[str]) -> dict[str, dict]:
    """URL da matéria no portal → {assuntos, temas, norma}."""
    saida = {}
    for cod in codigos:
        arquivo = pasta / f"{cod}.json"
        if not arquivo.exists():
            continue
        m = (json.loads(arquivo.read_text(encoding="utf-8")).get("DetalheMateria") or {}).get(
            "Materia"
        ) or {}
        basicos = m.get("DadosBasicosMateria") or {}
        temas = [
            c.get("DescricaoClasseHierarquica") or c.get("DescricaoClasse")
            for c in _lista((m.get("Classificacoes") or {}).get("Classificacao"))
        ]
        norma = (m.get("NormaGerada") or {}).get("IdentificacaoNorma") or {}
        saida[URL_MATERIA + cod] = {
            # Como publicada (o Senado grava a indexação em maiúsculas).
            "assuntos": _limpar(basicos.get("IndexacaoMateria")),
            "temas": [t for t in temas if t],
            "norma": {
                "rotulo": f"{norma.get('DescricaoTipoNorma', '')} nº {int(norma['NumeroNorma'])}"
                f"/{norma.get('AnoNorma', '')}",
                "url": norma.get("UrlNorma"),
            }
            if norma.get("NumeroNorma") and norma.get("UrlNorma")
            else None,
        }
    return saida
