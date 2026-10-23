# Congresso em Números

Composição da Câmara dos Deputados (e, depois, do Senado) de 1991 até hoje: parlamentares, partidos,
posição ideológica com fonte acadêmica, base de governo e votações nominais. Nome provisório.

A especificação completa está em [PROJECT.md](PROJECT.md). Decisões em [DECISIONS.md](DECISIONS.md),
fontes em [SOURCES.md](SOURCES.md) e pendências em [PENDENCIAS.md](PENDENCIAS.md).

## Estrutura

- `pipeline/`: pipeline Python que busca, transforma e valida os dados.
- `data/`: `raw/` (cache local, fora do git), `manual/` (CSVs curados, cada linha com fonte),
  `processed/` (Parquet).
- `web/`: site estático (Vite + TypeScript, sem framework). Visual importado do
  [Indicadores BR](https://github.com/antoniomanoell/mapa-brasil): ver
  [web/src/design/DESIGN.md](web/src/design/DESIGN.md).

## Pipeline

Requer [uv](https://docs.astral.sh/uv/).

```bash
cd pipeline
uv sync
uv run congresso --fase 1
uv run pytest
uv run ruff check . && uv run ruff format --check .
```

## Web

Requer Node 24.

```bash
cd web
npm install
npm run dev                         # amostra de estilo em /estilo.html
npm test
npm run lint && npm run format:check && npm run typecheck
```
