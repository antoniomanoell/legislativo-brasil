"""Linha de comando: `uv run congresso --fase N` roda o pipeline de uma fase (PROJECT.md, 5)."""

import argparse
import sys

# Fases com pipeline implementado. A Fase 0 é só verificação de fontes (SOURCES.md).
FASES: dict[int, str] = {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="congresso", description=__doc__)
    parser.add_argument("--fase", type=int, required=True, help="fase do PROJECT.md (1 a 5)")
    args = parser.parse_args(argv)
    if args.fase not in FASES:
        print(f"Fase {args.fase} ainda não tem pipeline.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
