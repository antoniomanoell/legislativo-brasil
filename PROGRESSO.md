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

## Fase 1 — concluída (2026-10-23), aguardando revisão do Antônio

- [x] Etapa `eleitos` (TSE 1990–2026) → `data/processed/eleitos.parquet`
- [x] Tabela de partidos com ID estável (`data/manual/partidos*.csv`, `linhagens.csv`)
- [x] Etapa `fotos` (Câmara, 1º/fev 2003–2026) → `data/processed/fotos.parquet`
- [x] Etapa `ideologia` (BLS 49ª–56ª; Bolognesi 2022 57ª–58ª) → `data/processed/ideologia.parquet`
- [x] Etapa `publicar`: JSON para o site em `web/public/data/` (momentos, partidos, ideologia)
- [x] Início: hemiciclo + linha do tempo (eleitos × em exercício) + tabela acessível + estado na URL
- [x] Evolução: % de cadeiras por partido ao longo do tempo; por faixa só onde há rótulo (A7)
- [x] Partidos: página básica (linhagem, tamanho, pontuação por legislatura com fonte)
- [x] Metodologia: rascunho (`<!-- RASCUNHO: revisar com Antônio -->`)
- [x] Testes de fumaça (Playwright, desktop e celular) e CI
- [x] Resumo da fase para o Antônio (abaixo)

## Resumo da Fase 1

- **Pipeline:** `uv run congresso --fase 1` roda quatro etapas (eleitos, fotos, ideologia,
  publicar), cada uma com conferências que param o pipeline se algo não bate. 46 testes.
- **Site:** Início (hemiciclo, linha do tempo, eleitos × em exercício, tabela acessível, cadeiras
  por partido, estado na URL), Evolução (posição das bancadas em dois painéis separados pela quebra
  de método; tabela de cadeiras com "seguir linhagem"), Partidos (lista e ficha) e Metodologia
  (rascunho). 17 testes unitários e 16 de fumaça (computador e celular).
- **Revisão pendente do Antônio:** texto da Metodologia e textos curtos das páginas (ajuda "?",
  avisos de lacuna); nome do site (A10).
- **Dados a atualizar depois:** eleitos de 2026 após a diplomação (B15); foto de 1º/fev/2027 quando
  a Câmara publicar a 58ª legislatura; onda 10 da BLS quando for publicada (B9).
- **A investigar:** PDS 1990 (TSE 45 × 42) e PP 2010 (TSE 44 × 41) contra o Apêndice A.

## Próximo passo exato

Aguardar a revisão do Antônio. Depois: Fase 2 (governos e coalizões: IPEA até meados de 2020 e
curadoria a partir daí; decisão A18 sobre 52 × 43 gabinetes).
