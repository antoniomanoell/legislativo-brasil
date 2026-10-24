# PENDENCIAS.md

Tudo marcado [confirmar] no PROJECT.md e as questões que aguardam decisão do Antônio. Ao resolver,
registrar o que foi descoberto, a data e a fonte, e mover a decisão para `DECISIONS.md`.
Contexto completo de cada item em `reports/fase0_viabilidade.md`.

## A. Decisões do Antônio

| # | Questão | Contexto (verificado em 2026-10-23) | Status |
|---|---|---|---|
| A1 | Qual onda BLS vale para a 49ª (eleitos 1990, fotos de 1991 e 1992)? | A onda de 1993 (regra 7.4) tem PRN, PDS/PPR (como "PP") e o PP de 1993, mas **não tem o PDC**, fundido no PPR em 1993. A onda de 1990, mais próxima dos eleitos de 1990, tem o PDC, mas mede a 48ª (assim mapeiam os próprios autores). | **decidida: onda 1993; PDC não classificado** |
| A2 | Na 56ª, qual Bolognesi tem prioridade (2018 ou 2022) para partido ausente da BLS 2021? | Ausentes da BLS 2021 com bancada: Avante, Patriota, PV, Rede. | **decidida: Bolognesi 2022** |
| A3 | Voto "Artigo 17" (presidente da sessão) no governismo e na presença | Aparece como valor de voto nos dados da Câmara. Proposta: excluir do denominador e da presença. | **decidida: excluir "Artigo 17"** |
| A4 | Abstenção e obstrução contam como "votantes" no Índice de Rice? | | **decidida: Rice com Sim e Não** |
| A5 | Como identificar votação de mérito de PEC em 1º/2º turno | Não há campo estruturado. A PEC é identificável (`proposicoesAfetadas`), o turno e o mérito só pelo texto ("em primeiro turno", ausência de "Requerimento", "destaque"). Proposta: regra de texto + revisão manual da lista, registrada em DECISIONS. | **decidida: regra de texto + revisão manual** |
| A6 | Impeachments (1992 e 2016) | **Nenhum dos dois tem voto individual nos Dados Abertos**; só o placar (2016: Sim 367, Não 137, Abst. 7, Ausências 2). Opções: (a) mostrar só o placar oficial; (b) transcrever o voto nominal do Diário da Câmara, como curadoria documentada. | **decidida: voto nominal transcrito do Diário da Câmara** |
| A7 | Crosswalk BLS × Bolognesi e cortes das sete faixas | Escalas diferentes: BLS de −1 a +1 (estimada); Bolognesi de 0 a 10 (média de experts). Pares disponíveis: 20 (BLS 2017 × B. 2018) e 18 (BLS 2021 × B. 2022). Cortes literais confirmados (PROJECT.md §6.2). | **decidida: sem conversão; rótulo só onde a fonte publica** |
| A8 | Abstenção/obstrução (e falta) no governismo | Opções documentadas: (A) Basômetro/Poder360 — abstenção e obstrução contra, ausência fora; (B) Congresso em Foco — abstenção, obstrução e falta contra; (C) obstrução a favor quando o governo orienta "Não"; (D) só Sim/Não no denominador; (E) qualquer das anteriores restrita a votações de mérito com disputa ≥ 20% (DIAP). | **decidida: opção A (abstenção e obstrução contra; ausência fora)** |
| A9 | Paleta das faixas ideológicas | Três candidatas em `web/estilo.html`; a A (roxo ↔ laranja) passa em todas as checagens. | **decidida: paleta A** |
| A10 | Nome do site e domínio | | aberta |
| A11 | Hospedagem (o mapa usa Vercel) | | aberta |
| A12 | Licença dos dados derivados | Câmara: domínio público com citação. TSE: CC-BY. BLS e Bolognesi: CC0. **IPEA: proíbe uso comercial.** **Cebrap: sem licença de redistribuição.** | aberta |
| A13 | Curadoria das coalizões pós-meados de 2020 | O IPEA para em meados de 2020; não há atualização acadêmica. | **decidida: critério literal da NT 53, até 30/03/2026** |
| A14 | O que é "eleito"? | O TSE mostra a situação **atual** (ex.: as 7 cadeiras de 2022 trocadas por decisão do STF em 2025), mas não registra cassações depois da diplomação (Deltan segue "eleito"). Opções: (a) situação atual do TSE, com nota; (b) resultado original, reconstruído de cópias datadas e notícias. | **decidida (2026-10-23): (a) situação atual do TSE** |
| A15 | Fotos de 1º/fev de 1991 a 2002 | A Câmara **não tem** filiação datada nem exercício datado antes de 2003. Opções: (a) pedir a filiação ao NIPE/Cebrap (só sob pedido, site fora do ar); (b) curadoria manual; (c) lançar com fotos só a partir de 2003 e, antes disso, apenas os eleitos (1990, 1994, 1998), com a lacuna sinalizada. | **decidida (2026-10-23): (c)** |
| A16 | Votações de 1991 a 2000 (e 2001–2002 sem orientação) | Só o Cebrap tem, mas o site está fora do ar e não há licença de redistribuição. Opções: (a) escrever ao NIPE/Cebrap pedindo autorização; (b) lançar com votações a partir de 2003 (governismo) e 2001 (votos), com a lacuna visível. | **decidida: sem Cebrap; lacuna 1991–2000** |
| A17 | Rótulos de Bolognesi 2022: média ponderada (como publicado) ou média bruta? | Aplicando os cortes à média bruta mudam 4 partidos: PSD (direita → centro-direita), Republicanos, PSC e União (extrema-direita → direita). | **decidida: média ponderada publicada** |
| A18 | Gabinetes do IPEA: 52 (CSV) ou 43 (Nota Técnica 53)? | O CSV não tem datas; a NT tem o mês de início de cada gabinete e outra divisão. | **decidida: Nota Técnica 53** |

## B. Itens [confirmar] do PROJECT.md

| # | Item | Descoberto em 2026-10-23 | Status |
|---|---|---|---|
| B1 | Filiação dos anos 1990 na API da Câmara | **Não cobre.** Eventos datados só a partir da 52ª (2003). Para a 49ª–51ª há um registro artificial por legislatura, que às vezes contradiz a listagem (ex.: Arnaldo Faria de Sá: PPR no histórico, PRN na listagem). | resolvido: não existe → A15 |
| B2 | Microdados do TSE para 1990 | Existe `votacao_candidato_uf_1990.zip` (TXT sem cabeçalho, 503 eleitos). Falta conferir o layout no Leia-me.pdf. | parcial |
| B3 | Dataset BLS e licença | Harvard Dataverse, CC0 (DOI 10.7910/DVN/6KVTUV). | resolvido |
| B4 | Cortes das sete faixas | Literais nos dois artigos de Bolognesi (§6.2). | resolvido → A17 |
| B5 | Ano inicial de voto individual + orientação do governo | Votos: dez/2001 (volumosos a partir de 2003). Orientação do Governo: 2003. | resolvido |
| B6 | Cebrap: o que é público e termos | Site fora do ar; sem licença de redistribuição; Senado nunca publicado. | resolvido → A16 |
| B7 | 49ª com 503 cadeiras | 503 eleitos no TSE em 1990. | resolvido |
| B8 | Datas dos governos e EC 111/2021 | Todas confirmadas em fonte oficial, exceto as trocas de partido de Bolsonaro (só imprensa) e o partido de Itamar no mandato (só IPEA). EC 111 confirmada: posse em 05/01/2027. | parcial |
| B9 | Nova onda BLS após 2021? | A onda 10 foi aplicada em 2025, mas não está publicada. | aberta: acompanhar |
| B10 | Votos nominais de deputados em vetos | Existem na API do Senado pelo menos desde mar/2016, sem o id da Câmara (casar por nome, partido e UF). Ano inicial exato não confirmado. | parcial |
| B11 | Lugar fixo no plenário | Câmara: só a primeira fila (líderes). Senado: não confirmado (página oficial deu 403). | parcial |
| B12 | Linhagens do Apêndice B | De 1995 em diante: todas confirmadas no TSE, com 5 datas corrigidas e 4 eventos acrescentados. Antes de 1995 (PPR, PP de 1993, PCB → PPS, registros do PRONA e do PSD de 1987): sem fonte no TSE. | parcial |
| B13 | Registro do Missão | 04/11/2025. | resolvido |
| B14 | Federações | Cinco, com datas (Apêndice B). | resolvido |
| B15 | Bancadas de 2026 | Os 10 partidos do Apêndice A batem com o TSE. Ainda não é definitivo: 9 eleitos com registro em recurso ou pendente, 178 candidatos com votos "anulado sub judice", diplomação não ocorrida. | aberta: reprocessar após a diplomação |
| B16 | Presidente eleito em 2026 | 2º turno em 25/10/2026: Lula (PT) × Flávio Bolsonaro (PL). | aberta |

## C. Pendências técnicas (sem decisão de método)

- 58ª legislatura: não existe na API da Câmara; criar em `data/manual/` a partir do TSE.
- Filtro `/deputados` em 1º/fev/2005 devolve 497 (de 513): investigar antes da Fase 1.
- Rótulo da orientação do Governo: normalizar "GOV." e "Governo".
- TSE 1998: deduplicar substitutos que dividem o número com o titular.
- Senado: votações de 2015–2016 incompletas ou com datas erradas; validar ano a ano na Fase 4.
- Eleitos (2026-10-23): duas bancadas fora da tolerância de ±2 contra o Apêndice A — **1990 PDS** (TSE 45,
  Apêndice 42) e **2010 PP** (TSE 44, Apêndice 41). Vale o TSE (A14); falta explicar a diferença.
- O TSE grava siglas de formas diferentes conforme o ano ("PCdoB", "PC DO B", "PC do B", "PCDOB") e
  reescreve siglas antigas com o nome atual (ex.: "PATRIOTA" no arquivo de 2014, quando o partido era
  o PEN). A tabela de partidos tem de mapear sigla do arquivo → partido na data da eleição.
- O arquivo de vagas de 1994 do TSE não tem deputado federal; nesse ano a conferência usa só o total
  (513) e os limites constitucionais por UF.
- Curadoria de gabinetes depois de 30/03/2026: verificar com fonte (desincompatibilizações de abril,
  PSD após lançar candidato, permanência de Luciana Santos/PCdoB) antes da foto de 1º/fev/2027.
- Datas de nomeação/exoneração de 2020–2026 sem conferência no DOU (in.gov.br indisponível na
  pesquisa): Flávia Arruda, exonerações de dez/2022, saídas de Dino e Juscelino; ver
  `data/manual/ministros_pos2020.csv`.
- Fontes da curadoria fora da lista inicial (SBT News, Correio Braziliense, Congresso em Foco, Jornal
  de Brasília, Diário de Pernambuco, site do Republicanos): marcadas no CSV.
- Impeachment 1992: BEBETTO HADDAD sem id da Câmara (candidato provável: Alberto Haddad, 73695, SP;
  não forçado); Gilvam Borges impresso como PMDB, mas PRN na API; grafias lidas na impressão
  matricial a conferir (ALDIR/ALOIR CABRAL, ROMEL/RONEL ANISIO). A transcrição de 1992 foi feita uma
  vez; votos e UFs estão travados pelos totais, mas um erro de grafia de nome ou partido é possível.

