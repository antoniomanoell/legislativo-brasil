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

## Fase 2 — concluída (2026-10-23)

- [x] Transcrever o Quadro 2 da NT 53 (IPEA) → `data/manual/gabinetes_ipea.csv`, com página
- [x] Tabela de governos (§7.5, datas confirmadas) → `data/manual/governos.csv`
- [x] Curadoria pós-meados de 2020 (até 30/03/2026; casos de julgamento aguardam validação do Antônio) → `data/manual/coalizoes_pos2020.csv` (cada linha com fonte; validar com o Antônio)
- [x] Etapa `governos` no pipeline (só IPEA até dez/2020; falta incluir a curadoria pós-2020): base formal em cada momento (% de cadeiras), conferida com os valores do IPEA (§7.5)
- [x] Web: página Governos e indicação da base formal no Início (com IPEA; falta a curadoria pós-2020)
- [x] Testes, CI e resumo para o Antônio

## Fase 3 — concluída (2026-10-23)

- [x] Extração: arquivos em lote da Câmara (votacoes, votacoesVotos, votacoesOrientacoes,
      votacoesProposicoes) 2001–2026, com cache em data/raw/camara/votacoes
- [x] Transformação: votações nominais de plenário, votos, orientação do Governo normalizada
      ("GOV." e "Governo"), partido do voto mapeado para partido_id
- [x] Impeachments 1992 e 2016: voto nominal transcrito do Diário → data/manual/impeachment_*.csv, conferido com o placar
- [x] Indicadores: governismo e presença (deputado e partido, por ano/legislatura/gabinete) e
      coesão (Rice), conforme DECISIONS (A3, A4, A8)
- [x] Destaques: PEC em 1º/2º turno (202 votações de 120 PECs) e impeachments 1992 e 2016 (transcritos do Diário)
- [x] Validação cruzada: partido no voto × filiação na data (reports/divergencias_filiacao.csv)
- [x] Publicar: arquivos anuais compactos + índice + indicadores.json (DECISIONS)
- [x] Web: páginas Votações e Deputados; governismo na página Governos
- [x] Testes, CI e resumo para o Antônio

## Fase 4 — concluída (Senado)

- [x] Verificar as fontes do Senado na prática: senadores por legislatura, mandatos e exercícios
      datados, filiações, votações (ListaVotacoes{ANO}.xml) e qualidade ano a ano
- [x] Eleitos de senador (TSE, 1990–2026): 1/3 ou 2/3 por eleição; restante como "mandato em curso" (§7.8)
- [x] Fotos de 1º/fev do Senado (13 válidas): só anos que fecham 81 com 3 por UF (DECISIONS)
- [x] Partido de cada senador na data: filiações datadas da API (siglas atuais → partido_id)
- [x] Votações nominais do Senado (1.756 abertas), governismo (2019+), coesão, presença (DECISIONS)
- [x] Web: seletor Câmara × Senado no Início (com base formal), Evolução, Votações e Parlamentares
      (ex-Deputados, com perfis de senadores). Partidos e Governos seguem só com a Câmara.
- [x] Seção Senado na Metodologia (rascunho), testes e2e do Senado, CI e resumo para o Antônio

## Fase 5 — em andamento (conteúdo e lançamento)

- [x] Decisões: nome "Congresso em Números", hospedagem Vercel, sem download dos dados tratados
- [x] Página Sobre (fontes, licenças, como citar)
- [x] Auditoria Lighthouse: desempenho ≥ 90 e acessibilidade 100 em todas as páginas (celular e
      computador); CLS corrigido; carga inicial ~100 KB de código + dados sob demanda
- [x] Página "2027": composição prevista da 58ª legislatura (etapa `congresso_2027`, fase 4)
- [ ] Revisão dos textos com o Antônio (Metodologia e Sobre ainda marcadas como rascunho)
- [ ] Antes do deploy: tirar `noindex` e criar robots.txt; preencher o endereço em "Como citar"
- [ ] Deploy na Vercel (conectar o repositório: passo do Antônio)
- [ ] Depois do 2º turno (25/10): `uv run congresso --fase 4 --etapa congresso_2027` (AC e TO) e
      governo de 2027; depois da diplomação: eleitos definitivos

## Próximo passo exato

Revisar com o Antônio os textos de Metodologia e Sobre; depois preparar o deploy na Vercel.
