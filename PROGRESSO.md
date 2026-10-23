# PROGRESSO.md — onde paramos

Arquivo para retomar o trabalho em outra sessão (o notebook pode desligar sem aviso). Atualizado e
commitado a cada passo. Contexto completo: `PROJECT.md`, `DECISIONS.md`, `PENDENCIAS.md`, `SOURCES.md`.

## Como rodar

```bash
cd pipeline && uv sync && uv run congresso --fase 1        # baixa (com cache em data/raw) e processa
cd web && npm install && npm run dev                      # site em http://localhost:5173
```

## Fase 0 — concluída (2026-10-23)

Fontes verificadas, relatório em `reports/fase0_viabilidade.md`, visual do mapa importado, CI.

## Fase 1 — em andamento

- [x] Etapa `eleitos` (TSE 1990–2026) → `data/processed/eleitos.parquet`
- [x] Tabela de partidos com ID estável (`data/manual/partidos*.csv`, `linhagens.csv`)
- [x] Etapa `fotos` (Câmara, 1º/fev 2003–2026) → `data/processed/fotos.parquet`
- [x] Etapa `ideologia` (BLS 49ª–56ª; Bolognesi 2022 57ª–58ª) → `data/processed/ideologia.parquet`
- [x] Etapa `publicar`: JSON para o site em `web/public/data/` (momentos, partidos, ideologia)
- [ ] Início: hemiciclo + linha do tempo (eleitos × em exercício) + tabela acessível + estado na URL
- [ ] Evolução: % de cadeiras por partido ao longo do tempo; por faixa só onde há rótulo (A7)
- [ ] Partidos: página básica (linhagem, tamanho, pontuação por legislatura com fonte)
- [ ] Metodologia: rascunho (`<!-- RASCUNHO: revisar com Antônio -->`)
- [ ] Testes de fumaça (Playwright, desktop e celular) e CI
- [ ] Resumo da fase para o Antônio

## Próximo passo exato

Página Início: `web/index.html` + `web/src/pages/inicio.ts` (hemiciclo, linha do tempo, tabela).
