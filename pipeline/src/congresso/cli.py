"""Linha de comando: `uv run congresso --fase N` roda o pipeline de uma fase (PROJECT.md, 5)."""

import argparse
import sys
from collections.abc import Callable

from congresso import etapas

# Etapas de cada fase, na ordem. A Fase 0 é só verificação de fontes (SOURCES.md).
FASES: dict[int, list[Callable[..., None]]] = {
    1: [etapas.eleitos, etapas.fotos, etapas.ideologia, etapas.publicar],
    2: [etapas.governos, etapas.publicar],
    3: [etapas.votacoes, etapas.publicar_votacoes],
    4: [etapas.eleitos_senado, etapas.fotos_senado],
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="congresso", description=__doc__)
    parser.add_argument("--fase", type=int, required=True, help="fase do PROJECT.md (1 a 5)")
    parser.add_argument(
        "--etapa", help="roda só esta etapa da fase (ex.: eleitos)", choices=_nomes_etapas()
    )
    parser.add_argument(
        "--atualizar", action="store_true", help="baixa de novo os arquivos já em data/raw"
    )
    args = parser.parse_args(argv)
    if args.fase not in FASES:
        print(f"Fase {args.fase} ainda não tem pipeline.", file=sys.stderr)
        return 2
    for etapa in FASES[args.fase]:
        if args.etapa and etapa.__name__ != args.etapa:
            continue
        try:
            etapa(atualizar=args.atualizar)
        except etapas.FalhaDeValidacao as erro:
            print(f"FALHA em {etapa.__name__}: {erro}", file=sys.stderr)
            return 1
    return 0


def _nomes_etapas() -> list[str]:
    return sorted({e.__name__ for lista in FASES.values() for e in lista})


if __name__ == "__main__":
    sys.exit(main())
