# DECISIONS.md

Registro das decisões metodológicas e técnicas do projeto (ver PROJECT.md, seção 0, regra 3).

Formato de cada entrada:

```
## AAAA-MM-DD — <título curto>
- **Decisão:** ...
- **Alternativa descartada:** ...
- **Motivo:** ...
- **Fonte:** <URL ou documento>
```

---

## 2026-10-23 — Posse presidencial em 5 de janeiro a partir de 2027
- **Decisão:** a tabela de governos (PROJECT.md, seção 7.5) encerra o mandato Lula 3 em 05/01/2027 e
  inicia o governo seguinte em 05/01/2027.
- **Alternativa descartada:** 31/12/2026 → 01/01/2027, como estava no rascunho original.
- **Motivo:** a EC 111/2021 alterou o art. 82 da Constituição (posse em 5 de janeiro), com aplicação a
  partir das eleições de 2026. Afeta a atribuição de base de governo por data; não afeta as fotos de 1º/fev.
- **Fonte:** Emenda Constitucional nº 111, de 28/09/2021, art. 4º (conferido no Planalto em
  2026-10-23; ver SOURCES.md).

## 2026-10-23 — Repositórios
- **Decisão:** este projeto vive em https://github.com/antoniomanoell/legislativo-brasil. A identidade
  visual será importada de https://github.com/antoniomanoell/mapa-brasil ("Indicadores BR").
- **Motivo:** indicado pelo Antônio; o `mapa-brasil` é o site do mapa citado na seção 9 do PROJECT.md.

## 2026-10-23 — Convenções de repositório herdadas do mapa
- **Decisão:** seguir as mesmas convenções do `mapa-brasil` — `.editorconfig` (LF, UTF-8, 2 espaços;
  4 em Python), pipeline Python gerenciado com `uv` + `ruff` + `pytest`, frontend Vite + TypeScript com
  Node 24, formato deste DECISIONS.md.
- **Motivo:** arquitetura compatível com fusão futura (D11) e um único conjunto de ferramentas para o
  Antônio manter.

## 2026-10-23 — Estrutura do pipeline como pacote `congresso`
- **Decisão:** o pipeline é o pacote `pipeline/src/congresso/` (subpastas `extract/`, `transform/`,
  `load/`, `validate/`), com testes em `pipeline/tests/` e a linha de comando `uv run congresso --fase N`.
- **Alternativa descartada:** `python -m pipeline.run --fase 1` e `tests/` na raiz, como no esboço da
  seção 8 do PROJECT.md.
- **Motivo:** é o layout do `mapa-brasil` (pacote em `src/`, CLI via `project.scripts`, `uv`). Mesmas
  subpastas e mesmo comportamento do esboço.

## 2026-10-23 — Visual do mapa copiado sem alterações
- **Decisão:** `style.css`, `tema.ts` e `ajuda.ts` do mapa entram em `web/src/design/` sem edição
  (`mapa.css`, `tema.ts`, `ajuda.ts`); o que é só deste site fica em `congresso.css`. Detalhes e
  commit de origem em `web/src/design/DESIGN.md`.
- **Alternativa descartada:** extrair só os tokens e reescrever os componentes.
- **Motivo:** visual idêntico por construção e fusão futura trivial; o CSS do mapa tem 5 KB gzip,
  dentro do orçamento de 500 KB.

## 2026-10-23 — Hemiciclo: geometria
- **Decisão:** fileiras = round(0,6·√N) (513 → 14, 503 → 13, 81 → 5); raio interno 0,4 do externo;
  cadeiras por fileira proporcionais ao raio, arredondadas pelo método dos maiores restos; cadeiras
  ordenadas por ângulo, da esquerda para a direita (`web/src/charts/hemiciclo.ts`, com testes).
- **Motivo:** algoritmo pedido na seção 8; os testes garantem total exato, ordem e ausência de
  sobreposição para 81, 503 e 513 cadeiras.

## 2026-10-23 — CI sem testes de navegador na Fase 0 (superada na Fase 1: o CI roda Playwright)
- **Decisão:** o CI roda lint, formatação, tipos, testes unitários e build (pipeline e web). Os testes
  de fumaça com Playwright, como no mapa, entram na Fase 1, quando houver páginas de verdade.
- **Motivo:** hoje só existe a página de amostra; instalar navegador no CI não testaria nada útil.

## 2026-10-23 — "Eleito" = situação atual no TSE (A14)
- **Decisão:** a visão "eleitos" usa a situação atual de cada candidato nos arquivos do TSE
  (`consulta_cand_AAAA`; em 1990, `votacao_candidato_uf_1990`), com o `DT_GERACAO` registrado e cópia
  datada do arquivo guardada. A interface avisa que a composição reflete retotalizações e decisões
  judiciais posteriores (ex.: 7 cadeiras de 2022 trocadas após a decisão do STF sobre as sobras,
  aplicada a 2022 em 2025), mas não cassações de registro depois da diplomação (Deltan Dallagnol).
- **Alternativa descartada:** reconstruir o resultado da noite da eleição a partir de cópias antigas e
  notícias.
- **Motivo:** decidido pelo Antônio. É a fonte oficial, reproduzível e auditável.
- **Consequência:** o Apêndice A do PROJECT.md vira só conferência (tolerância ±2); divergências
  maiores são investigadas e explicadas.

## 2026-10-23 — Fotos de 1º/fev só a partir de 2003 (A15)
- **Decisão:** as fotos "em exercício em 1º/fev" começam em 2003. De 1991 a 2002, o site mostra apenas
  os eleitos de 1990, 1994 e 1998, e a lacuna das fotos aparece sinalizada na interface.
- **Alternativas descartadas:** pedir a filiação ao NIPE/Cebrap; curadoria manual de 12 anos de fotos.
- **Motivo:** decidido pelo Antônio. A Câmara só tem histórico datado de partido e exercício a partir
  da 52ª legislatura (2003); antes disso não há fonte aberta.

## 2026-10-23 — Rótulos ideológicos só onde a fonte os publica (A7)
- **Decisão:** não converter a escala da BLS para a de Bolognesi. Nas legislaturas medidas só pela BLS
  (49ª–55ª), o site mostra a pontuação BLS (−1 a +1, com erro-padrão), ordena o hemiciclo por ela e
  colore numa escala contínua com os mesmos dois matizes da paleta, **sem rótulo de faixa**. Onde há
  Bolognesi, mostra pontuação e rótulo publicados. A troca de método é marcada na interface. O gráfico
  de % de cadeiras por faixa só existe onde há rótulo; antes disso, a evolução usa a distribuição das
  pontuações.
- **Alternativa descartada:** conversão linear BLS → Bolognesi com os pares medidos pelas duas fontes.
- **Motivo:** decidido pelo Antônio após o teste: a conversão tem correlação alta (r = 0,96 e 0,98),
  mas erro típico de 0,50 a 0,66 ponto contra faixas de ~1,5 ponto; só 15 de 20 (2017×2018) e 13 de
  18 (2021×2022) partidos caem na mesma faixa; a inclinação muda entre os pares (4,28 e 4,70), o que
  tornaria a extrapolação até 1993 frágil. Altera a decisão D5.

## 2026-10-23 — Bolognesi 2022: rótulo da média ponderada, como publicado (A17)
- **Decisão:** usar a coluna "ideologia categórica" e a "média ponderada" da Tabela 1 de Bolognesi,
  Ribeiro, Codato & Silva (2025). A média simples de 2022 fica na página de metodologia.
- **Alternativa descartada:** aplicar os cortes à média simples (mudaria PSD, Republicanos, PSC e
  União de faixa, criando rótulos que os autores não publicaram).
- **Motivo:** decidido pelo Antônio; fidelidade à fonte nomeada.

## 2026-10-23 — Onda BLS de 1993 para a 49ª legislatura (A1)
- **Decisão:** seguir a correspondência dos autores (onda 1993 → 49ª). O PDC, ausente da onda de 1993,
  fica "não classificado". O PDS recebe a pontuação da linhagem PDS/PPR ("PP" na BLS), com nota visível.
- **Alternativa descartada:** usar a onda de 1990 (mede a 48ª).
- **Motivo:** decidido pelo Antônio; é o mapeamento do código de replicação de Zucco & Power.

## 2026-10-23 — 56ª legislatura: Bolognesi 2022 para partido ausente da BLS 2021 (A2)
- **Revogada** pela decisão "Uma só escala por legislatura" (mais abaixo): na 56ª só a BLS é usada.
- **Decisão:** Bolognesi 2022 (afeta Avante, Patriota, PV e Rede).
- **Alternativa descartada:** Bolognesi 2018.
- **Motivo:** decidido pelo Antônio; 2022 está a 1 ano da onda BLS de 2021, que mede o restante da
  legislatura, e já reflete as fusões do período.

## 2026-10-23 — Paleta A (roxo ↔ laranja) para as faixas (A9)
- **Decisão:** paleta A de `web/src/design/paletas.ts`, nos tons de cada tema; "não classificado" em
  hachura.
- **Alternativas descartadas:** B (verde-azulado ↔ ocre) e C (magenta ↔ verde-azulado).
- **Motivo:** decidido pelo Antônio; única que passa em todas as checagens de daltonismo e contraste
  nos dois temas.

## 2026-10-23 — Sem dados do Cebrap (A16)
- **Decisão:** não pedir dados ao NIPE/Cebrap. Votos individuais a partir de 2001 e governismo a
  partir de 2003 (Câmara); 1991–2000 aparece como lacuna sinalizada.
- **Motivo:** decidido pelo Antônio. O banco está fora do ar e não tem licença de redistribuição.

## 2026-10-23 — Polars para transformar, Parquet para guardar
- **Decisão:** as transformações usam polars (como no `mapa-brasil`) e gravam Parquet em
  `data/processed/` (fora do git, regenerável). Downloads com httpx e cache em `data/raw/`.
- **Alternativa descartada:** DuckDB, citado na seção 8 do PROJECT.md.
- **Motivo:** mesma ferramenta do mapa, que o Antônio já mantém; o volume (até ~639 MB de votos em
  CSV) é tratável com polars. DuckDB pode entrar depois se alguma consulta pedir SQL.

## 2026-10-23 — Eleitos: conferência por UF e exceção de 1994
- **Decisão:** a etapa `eleitos` para o pipeline se o número de eleitos por UF diferir das vagas do
  TSE (`consulta_vagas`). Em 1994, cujo arquivo de vagas não traz deputado federal, confere o total de
  513 (LC 78/1993) e o limite de 8 a 70 por UF (CF, art. 45, § 1º). Contra o Apêndice A, só alerta
  (tolerância ±2) e grava `reports/eleitos_x_apendice_a.csv`.
- **Motivo:** conferência contra fonte oficial independente; o Apêndice A é compilação secundária.

## 2026-10-23 — Partidos: ID estável por entidade jurídica e mapeamento pelo número
- **Decisão:** cada partido tem um `partido_id` estável (`data/manual/partidos.csv`). Renomeação mantém
  o ID (`renomeacoes.csv`); fusão cria partido novo; incorporação mantém o ID do incorporador; ambos
  registrados como arestas em `linhagens.csv` (com processo do TSE quando posterior a 1995). Homônimos
  são partidos diferentes (ex.: `psd1987` × `psd2011`, `pcb1922` × o PCB de número 21, `pl` × `pr`,
  `pp1993` × `ppb`, `pst52` × `pst18`).
- Os eleitos recebem o partido pela tabela curada `partidos_tse.csv` (eleição, número → partido e sigla
  da época). Em cada eleição um número pertence a um só partido, mas o TSE reaproveita números entre
  partidos (17: PDC, PTRB, PSL; 25: PFL/DEM, PRD; 44: PRP, União; 30: PGT, Novo; 18: PST, Rede) e
  regrava siglas antigas com o nome atual (ex.: "PATRIOTA" no arquivo de 2014, quando era o PEN).
  O pipeline para se um eleito não tiver mapeamento ou se a sigla do arquivo mudar.
- **Alternativa descartada:** identificar o partido pela sigla do arquivo do TSE.
- **Motivo:** a sigla do TSE não é confiável no tempo; o número, por eleição, é.

## 2026-10-23 — Fotos de 1º/fev: regra de exercício e de partido
- **Decisão:** em exercício na data = o último evento do histórico da Câmara até o **fim do dia** 1º/fev,
  na legislatura vigente e a partir do início dela, tem situação "Exercício", desconsiderando eventos
  de troca de partido ou de nome. O partido é o do último evento de qualquer tipo até a data. Em anos
  de posse (2003, 2007, ...), o fim do dia faz a foto mostrar a composição já empossada (§7.2).
- **Motivo:** a API registra trocas de partido também para quem está fora do mandato, às vezes com
  data anterior à legislatura e situação "Exercício" (ex.: id 74140, 31/03/2022, na 57ª), o que punha
  40 deputados da BA em exercício para 39 vagas em 2023, 2024 e 2026.
- **Consequência:** algumas fotos têm menos de 513 em exercício (ex.: 486 em 2006), por licenças com
  suplente ainda não empossado, cassações e falecimentos; a diferença aparece como cadeira vaga
  (`reports/fotos_cadeiras.csv`). O filtro da própria API dá números próximos (497 em 2005, contra
  494 nossos).

## 2026-10-23 — Siglas da Câmara mapeadas como registradas
- **Decisão:** `data/manual/partidos_camara.csv` liga a sigla registrada pela Câmara ao partido, com
  período de validade quando a sigla é ambígua ("PL" até 2006 = PL antigo; de 2019 = ex-PR). O site
  mostra o que a Câmara registrou, mesmo com atraso (ex.: "PATRIOTA" em 1º/fev/2024, depois da fusão
  no PRD em 09/11/2023). "S.PART." vira o partido especial `sem_partido`.
- **Motivo:** fidelidade à fonte da composição; o atraso é da Câmara, não do projeto.

## 2026-10-23 — Uma só escala por legislatura; ausentes da BLS ficam "não classificado"
- **Decisão:** nas legislaturas 49ª–56ª só a BLS é usada. Partido que a BLS não mediu fica "não
  classificado", inclusive na 55ª e na 56ª. A decisão A2 (Bolognesi 2022 para ausentes na 56ª) e a
  regra 7.4.2 deixam de ter efeito; Bolognesi 2018 não é usado.
- **Alternativas descartadas:** Bolognesi na legislatura inteira (contraria 7.4.1); Bolognesi só nos
  ausentes (duas escalas no mesmo hemiciclo, que não se ordenam sem conversão — rejeitada em A7).
- **Motivo:** decidido pelo Antônio ("o mais honesto e rigoroso"). Afeta de 3% a 4% das cadeiras.

## 2026-10-23 — Herança de pontuação só pela linhagem definida pelos autores da BLS
- **Decisão:** um partido recebe a pontuação de outra sigla da BLS só quando os autores definem as duas
  como a mesma linhagem (apêndice do dataset): PDS ← "PP" (1993); PCB ← "CID" (1993; "o PPS foi uma
  rebatização do histórico PCB"); PPR ← "PP" (1997, eleitos de 1994); PL eleito em 2006 ← "PL" (2009;
  os autores tratam PL e PR como uma linhagem). PTR e PST ficam "não classificado": o PP de 1993 é
  partido novo, nascido de fusão; o mesmo vale para o PP de 1993 diante da onda de 1997.
- **Alternativa descartada:** herdar de qualquer sucessor (fusões incluídas).
- **Motivo:** decidido pelo Antônio ("o mais honesto e rigoroso"); generaliza A1. Cada herança está
  em `data/manual/ideologia_siglas.csv`, com nota que o site exibe.

## 2026-10-23 — Paleta vermelho (esquerda) ↔ azul (direita), em vez de roxo ↔ laranja (revê A9)
- **Decisão:** as faixas usam vermelho nas posições à esquerda e azul nas posições à direita, com cinza
  no centro (claro: #901e1c #ce5950 #ff988d #dbdbdb #80beff #3d84db #004d9f; escuro: #ffbbb1 #e77f75
  #ad524a #424242 #3d73b6 #67a4f1 #a8d8ff). Na BLS, a escala contínua usa os mesmos tons.
- **Alternativa descartada:** paleta A (roxo ↔ laranja), escolhida antes para evitar cores de marca.
- **Motivo:** decidido pelo Antônio: é a convenção mais reconhecível (vermelho = esquerda) e a leitura
  fica imediata. Passa em todas as checagens de daltonismo e contraste nos dois temas (pior par
  vizinho ΔE 11,8 no claro e 12,1 no escuro; meta ≥ 8). Risco aceito: alguns partidos usam vermelho
  ou azul na própria marca; por isso a identidade do partido continua vindo de sigla e separadores,
  e a legenda deixa claro que a cor é a posição, não o partido. Altera a orientação da seção 9 do
  PROJECT.md ("evitar cores de marca partidária").

## 2026-10-23 — Fonte da posição: uma vez por contexto
- **Decisão:** a fonte da posição ideológica aparece uma vez em cada contexto — na legenda do
  hemiciclo, numa linha acima de cada tabela e no título de cada painel da Evolução —, e não em cada
  dica ou linha. Na ficha do partido, onde a fonte muda de uma legislatura para outra, ela continua
  como coluna.
- **Motivo:** pedido do Antônio; a repetição poluía o texto. O princípio 1.1.2 (fonte nomeada e
  visível) continua atendido: a fonte está sempre na mesma tela que a classificação.

## 2026-10-23 — Gabinetes do IPEA: a Nota Técnica 53, não o CSV (A18)
- **Decisão:** a base formal de governo até meados de 2020 vem do Quadro 2 da Nota Técnica Diest
  nº 53 (Almeida, 2021; DOI 10.38116/ntdiest53): 43 gabinetes, com mês de início e partidos com
  ministério, transcrito em `data/manual/` com página de origem.
- **Alternativa descartada:** o CSV do Atlas do Estado (52 gabinetes, sem datas, siglas atuais).
- **Motivo:** decidido pelo Antônio ("o mais honesto e rigoroso"). Só a NT tem datas, que são
  indispensáveis para saber a base em cada momento, e só ela descreve o método. O CSV diverge da NT
  e não documenta a diferença.

## 2026-10-23 — Base formal = partidos com ministro; os % do IPEA citados no §7.5 medem outra coisa
- **Decisão:** a "base formal" do site é a soma das cadeiras dos partidos com ministro no gabinete
  vigente (critério da Nota Técnica 53). Os percentuais do §7.5 do PROJECT.md servem só como
  referência, sem exigência de igualdade: no texto do Atlas eles medem a aliança eleitoral ou a base
  aliada, que inclui partidos sem ministério (Dilma 1: 72,5% somando PSC, PRB e "partidos de menor
  expressão"; Bolsonaro: 16,5% somando o apoio formal do PR). Onde os conceitos coincidem, os números
  batem (Lula 1: 48,3% × 48,5%; Lula 2: 69,4% × 70%). A comparação fica em
  `reports/base_inicio_gabinetes.csv`.
- Gabinetes iniciados em janeiro de ano de posse da Câmara são conferidos com a composição de 1º/fev
  (a legislatura que vai conviver com eles), não com a que está saindo.
- A série do IPEA cobre de mar/1985 a dez/2020 (Nota Técnica 53). Depois disso a base vem só da
  curadoria (`data/manual/gabinetes_pos2020.csv`); sem ela, o site mostra "sem dados", sem estender
  o último gabinete do IPEA.
- **Motivo:** fidelidade ao critério declarado (PROJECT.md 3.2: base formal = critério ministerial).

## 2026-10-23 — Curadoria de gabinetes de 2021 a mar/2026: critério literal da NT 53 (A13)
- **Decisão:** nos casos duvidosos, vale o critério literal da Nota Técnica 53 — o ministro é
  partidário se o partido (a) apoia o governo e (b) o indicou ou (c) o reconhece como representante,
  com evidência. Resultado: não contam União Brasil (presidente do partido: "a gente não faz parte do
  governo Lula", 29/12/2022; mesmo tratamento do IPEA ao DEM em 2019), PP e Republicanos em 2023
  (partidos negaram o vínculo), Waldez Góes (PDT não o reconhece), Marina Silva (sem declaração
  localizada da Rede) e o PDT a partir de 06/05/2025 (declarou-se independente). Eventos de "mudança
  relevante de ministro" só com declaração de lideranças sobre o impacto (fica só set/2023).
- A curadoria cobre até 30/03/2026: as mudanças de abril de 2026 (desincompatibilizações, PSD com
  candidato próprio, permanência de Luciana Santos) não afetam nenhuma foto de 1º/fev e ficam para
  verificar com fonte. Ministro a ministro em `data/manual/ministros_pos2020.csv`, com a classificação
  e o motivo; gabinetes em `data/manual/gabinetes_pos2020.csv`.
- **Alternativa descartada:** contar todo partido com filiado no ministério (daria 51% das cadeiras
  para Lula 3 em 1º/fev/2023 e 70% em 1º/fev/2024, contra 39% e 40% pelo critério; recalculado em
  2026-10-24 — o valor anterior aqui, "cerca de 59%", não se reproduz com os dados).
- **Motivo:** decidido pelo Antônio ("o mais honesto e rigoroso"); é o critério declarado pela fonte
  da série até 2020, aplicado sem exceções. O site mostra, gabinete a gabinete, quem não foi contado
  e por quê.

## 2026-10-23 — Indicadores de votação (A3, A4, A5, A8) e impeachments (A6)
- **Governismo (A8):** só votações nominais de plenário em que o governo orientou "Sim" ou "Não".
  Numerador: votos iguais à orientação. Denominador: Sim + Não + Abstenção + Obstrução (abstenção e
  obstrução contam como não seguir a orientação, como no Basômetro/Estadão e no Poder360). Ausência
  fica fora e vira uma taxa de presença à parte. Alternativas descartadas: contar a falta contra
  (Congresso em Foco); obstrução a favor quando o governo orienta "Não"; só Sim/Não no denominador.
- **"Artigo 17" (A3):** registro do presidente da sessão; sai do governismo, da coesão e da presença.
- **Coesão (A4):** Índice de Rice por votação e partido = |%Sim − %Não| entre os votos Sim e Não do
  partido (definição original); média por período. Alternativa descartada: Agreement Index (Hix,
  Noury & Roland).
- **PEC em destaque (A5):** votação de PEC (proposição afetada do tipo PEC) cuja descrição indica
  primeiro ou segundo turno e não é requerimento, destaque ou emenda; a lista resultante é revista
  à mão e gravada em data/manual com a regra e as exceções.
- **Impeachments (A6):** voto de cada deputado transcrito do Diário da Câmara (29/09/1992 e
  17/04/2016), como curadoria documentada, conferido com o placar oficial. Alternativa descartada:
  só o placar.
- **Motivo:** decidido pelo Antônio (1 a 4 conforme a recomendação; impeachment com voto nominal).

## 2026-10-23 — Votações: publicação compacta por ano (§8, volume)
- **Decisão:** um JSON por ano (`web/public/data/votacoes/ano-AAAA.json`) com a lista de deputados
  do ano e, por votação, o voto de cada um como um caractere na ordem da lista e o partido no momento
  do voto também como um caractere (índice na lista de partidos do ano); mais um índice sem votos e
  `indicadores.json` com os agregados. Total: 9,6 MB de votações (~400 KB por ano) e 874 KB de
  indicadores; a página carrega só o ano que precisa.
- **Alternativas descartadas:** um JSON por votação (≈160 MB); Parquet + DuckDB-WASM no navegador
  (dependência pesada sem ganho para este volume).
- **Motivo:** a opção mais simples que cumpre o orçamento de performance (§10.2) sem servidor.

## 2026-10-23 — Presença: quem votou conta como em exercício
- **Decisão:** o "esperado" de cada votação são os deputados em exercício segundo o histórico da
  Câmara **ou** que votaram nela; quem votou sem constar do histórico em exercício (10.182 votos, de
  1,9 milhão) vai para `reports/votos_fora_do_historico.csv`. "Artigo 17" não conta como presença.
- **Motivo:** o voto prova o exercício; o histórico tem lacunas. Sem isso, a presença passaria de
  100% para alguns deputados.

## 2026-10-23 — Destaque de PEC: regra aplicada ao texto do resultado (refina A5)
- **Decisão:** a regra de PEC em 1º/2º turno usa o texto do **resultado** da votação (campo
  `descricao`, ex.: "Aprovada, em segundo turno, a Proposta..."), não o da abertura, que repete o
  item da sessão enquanto se votam requerimentos (ex.: PEC 6/2019, 06/08/2019: "Votação em segundo
  turno" num requerimento rejeitado por 12 × 349). Excluem-se requerimento, destaque, DTQ, DVS,
  recurso, admissibilidade e turno único; a fórmula "ressalvado(s) o(s) destaque(s)" é removida antes,
  por ser típica da própria votação de mérito. Resultado: 202 votações de 120 PECs; nenhuma votação
  "aprovada em 1º/2º turno" de PEC fica de fora, e a única rejeitada (PEC 135/2019, 1º turno) é de
  mérito. O site também passa a mostrar o texto do resultado, não o da abertura.
- **Motivo:** a primeira versão marcava requerimentos como mérito e deixava de fora a votação de
  mérito da reforma da Previdência; conferido nos dados da PEC 6/2019 votação a votação.

## 2026-10-23 — Impeachments: voto nominal transcrito do Diário oficial (aplica A6)
- **Decisão:** as duas votações de autorização de impeachment entram com o voto de cada deputado,
  transcrito de fonte primária: 1992 do Diário do Congresso Nacional, Seção I, nº 161, de 30/09/1992
  (tabela nominal, pp. 22121–22127; o PDF é imagem, transcrito visualmente linha a linha); 2016 do
  Diário da Câmara dos Deputados nº 056, de 18/04/2016 (registro da chamada oral, pp. 57–118, com texto
  extraível). Os totais batem exatamente com o placar proclamado (1992: 441 Sim, 38 Não, 1 abstenção,
  23 ausentes; 2016: 367, 137, 7, 2), e o pipeline para se a transcrição deixar de bater. Nomes e
  partidos ficam como impressos no documento; o partido em branco no Diário de 1992 (5 casos) aparece
  como "não informado", sem completar com outra fonte. As votações entram como destaque (§7.7,
  critério 2) e ficam fora do governismo (não há orientação do Governo registrada nelas).
- **Conferências:** 1992 — contagem por UF fecha com as bancadas; os 38 votos "Não" e a abstenção
  coincidem nome a nome com a lista do Congresso em Foco. 2016 — cada um dos 513 nomes da lista de
  presença do Diário casa com exatamente um voto; placar por UF igual ao publicado pela imprensa.
- **Motivo:** decidido pelo Antônio (impeachment com o voto de cada deputado).

## 2026-10-23 — Senado: fotos de 1º/fev só nos anos em que a fonte oficial fecha 81 cadeiras
- **Decisão:** a foto do Senado em 1º/fev é publicada só quando os períodos de exercício da API do
  Senado (`/senador/{código}/mandatos`) reconstroem exatamente 81 senadores, 3 por UF. Nos demais anos
  a foto fica como lacuna sinalizada, com o motivo. O partido vem das filiações datadas
  (`/senador/{código}/filiacoes`); sem filiação datada que cubra a data, "não informado".
- **Motivo:** decidido pelo Antônio ("o mais honesto e rigoroso"). Verificado em 2026-10-23: os
  mandatos iniciados na 48ª legislatura (eleitos em 1986) não têm exercício registrado (1991–1994
  dão 27 senadores); vários suplentes que exerceram não têm exercício registrado (anos com 79 ou 80);
  em 2025 há exercícios sobrepostos (84). Fecham: 1999–2003, 2011–2012, 2019–2020, 2022–2024 e 2026.
- **Alternativas descartadas:** mostrar todos os anos com "sem registro" (2025 exigiria escolher sem
  fonte); completar com votos próximos da data (prazo arbitrário).
- O partido gravado nos votos do Senado é a sigla atual do senador (ex.: "MDB" para Sarney em 2003),
  e por isso não é usado como partido na data.

## 2026-10-23 — Senado: votações, governismo e presença
- **Presença (decidido pelo Antônio):** votou (Sim, Não, Abstenção, Obstrução) ÷ todos os senadores
  listados na votação, menos licenças (LS, LP, LG, LA, LAP) e ausências a serviço do Senado (AP,
  MIS, REP, MERC). "Não compareceu" (NCom) e "presente, não registrou voto" (P-NRV) contam como não
  votou. "Presidente (art. 51 RISF)" sai, como o "Artigo 17" da Câmara. Códigos de significado não
  confirmado (P-OD, NA) ficam fora do numerador e do denominador.
- **Governismo:** mesma regra da Câmara (A8), só nas votações com orientação "Sim" ou "Não" da
  liderança do Governo (`/plenario/votacao/orientacaoBancada`), que só existe a partir de 2019 e
  numa parte das votações; antes disso, lacuna (§7.6).
- **Votações secretas** (voto "Votou") ficam fora de governismo, coesão e presença.
- **Partido no voto:** pela filiação datada do senador na data da votação (o partido gravado no voto é
  a sigla atual); sem filiação datada, "não informado".
- **Anos incompletos na fonte:** 2015 e 2016 têm 15 e 10 votações abertas (contra 50–130 nos anos
  vizinhos), e 2016 traz matérias de 1998–1999 com data de 2016 (Fase 0); aparecem com aviso.

## 2026-10-23 — Senado: votações com lista de votantes incompatível com os mandatos ficam de fora
- **Decisão:** sai a votação em que 10 ou mais senadores listados não tinham mandato (titular ou
  suplente) na data. Nos dados de 2026-10-23 a distribuição é bimodal — 0 a 3 por votação (lacunas do
  cadastro de mandatos) ou 40 ou mais (data ou lista errada na fonte) —, então o corte não decide
  nenhum caso duvidoso. Saem 25 votações (15 de 2015, 4 de 2016, 4 de 2002 e 2 de 2017), listadas em
  `reports/votacoes_senado_excluidas.csv`.
- **Motivo:** mostrar uma votação com a lista de votantes de outra época seria publicar dado errado;
  a lista fica disponível para conferência.


## 2026-10-23 — Senado eleito: contagem por UF pela regra constitucional, não pelo arquivo de vagas
- **Decisão:** de 1994 em diante, os eleitos por UF são conferidos com a CF, art. 46 (1 ou 2 por UF,
  alternadamente); em 1990, com o arquivo de vagas do TSE (AP e RR elegeram três).
- **Motivo:** o arquivo `consulta_vagas_2018` do TSE registra 1 vaga de senador em MT, mas foram
  eleitos 2 (como nas outras 26 UFs, renovação de 2/3). Erro do arquivo de vagas, registrado em
  PENDENCIAS.md.

## 2026-10-24 — "O que foi votado": só textos e classificações oficiais, sem resumo do projeto
- **Decisão (recomendação aceita pelo Antônio):** cada votação mostra, por proposição, a ementa, o
  link para a página oficial e, quando a Casa publica: indexação (palavras-chave), temas
  (classificação do Senado), inteiro teor (Câmara) e norma gerada (Senado). Fontes:
  `/proposicoes/{id}` (Câmara) e `/materia/{código}` (Senado). Indexação do Senado fica como
  publicada, em maiúsculas.
- **Alternativas descartadas por ora:** resumo em linguagem simples gerado por IA para todas as
  votações (milhares de textos sem revisão possível; risco de erro e de enquadramento num site que
  se diz neutro); resumo revisado só para os destaques (PEC e impeachment) fica como opção futura.

## 2026-10-24 — Nome, hospedagem e dados
- **Nome (Antônio):** Congresso em Números.
- **Hospedagem (Antônio):** Vercel, como o mapa.
- **Dados (Antônio):** sem página "Sobre / Dados" com download dos dados tratados (PROJECT.md 4.1.8 sai
  do escopo). A página "Sobre" fica com fontes, licenças de cada fonte e como citar. Os JSON que o
  site carrega continuam acessíveis tecnicamente a quem abrir as ferramentas do navegador (é um site
  estático); não há link nem convite para baixá-los.

## 2026-10-24 — Congresso a partir de 2027 (composição prevista da 58ª legislatura)
- **Pedido do Antônio:** mostrar como fica o Congresso a partir de 2027 com o resultado do 1º turno.
- **Câmara:** os 513 eleitos de 2026 (TSE, situação atual — A14), pelo partido da eleição.
- **Senado:** os 54 eleitos de 2026 mais as 27 cadeiras com mandato até 31/01/2031 (eleitas em 2022).
  Em cada uma das 27 fica **quem a ocupa na data dos dados do Senado** (registros de exercício), com
  o partido da filiação registrada nessa data. Isso já cobre suplentes efetivados (MA: renúncia de
  Flávio Dino) e mostra com nota o suplente em exercício por afastamento temporário (PI). Se o
  ocupante foi **eleito governador no 1º turno** (TSE 2026: Cleitinho/MG, Sergio Moro/PR), entra o
  1º suplente; quem **disputa o 2º turno** (Alan Rick/AC, Professora Dorinha/TO) fica, com nota.
  Suplente sem filiação no Senado fica "não informado", com o partido pelo qual foi suplente em 2022
  na nota (o PSC de 2022 foi incorporado ao Podemos; não se presume filiação atual).
- **Fica de fora (avisado na página):** trocas de partido até a posse, mudanças até a diplomação,
  resultado do 2º turno. Reprocessar depois de 25/10/2026 e da diplomação.
- **Mais rigoroso que as alternativas:** usar o titular eleito em 2022 ignoraria a renúncia de Dino;
  usar o partido da eleição de 2022 nas 27 cadeiras ignoraria trocas registradas pelo Senado.

## 2026-10-24 — Destaque de PEC no Senado segue a A5 (revisão da Metodologia)
- **Decisão:** no Senado, destaque = matéria PEC com 1º ou 2º turno na descrição, **exceto** votação em
  separado de emenda, destaque ou requerimento (descrição que começa por esses nomes); emenda
  substitutiva e substitutivo ficam (são o texto de mérito). Casos que a regra não resolve vão para
  `data/manual/destaques_pec_excecoes.csv` com o motivo: SF-3900 ("Substituriva" na fonte) e
  SF-2754/SF-2755 (Emenda 240-CCJ à PEC 29/2000, texto de mérito dividido).
- **Antes:** toda PEC com turno na descrição (414 votações), contrariando a A5. **Depois:** 400.
- **Motivo:** decidido pelo Antônio ("o mais honesto e rigoroso"); aplica a A5 já decidida.

## 2026-10-24 — Posição ideológica dos presidentes (BLS)
- **Pedido do Antônio:** mostrar no hemiciclo quem era o presidente e a posição ideológica dele.
- **Fonte:** as estimativas de presidentes da BLS (Zucco & Power, `bls9_estimates_partiespresidents`),
  na escala −1 a +1. Só existem nas ondas de 2013 (Sarney, Collor, Itamar, FHC, Lula, Dilma), 2017 (os
  mesmos e Temer) e 2021 (só Bolsonaro).
- **Regra:** a onda feita durante o mandato; senão, a primeira posterior; senão, a mais recente anterior.
  Resultado: Dilma 1 (2013), Temer (2017) e Bolsonaro (2021) durante; Collor, Itamar, FHC 1–2, Lula 1–2
  (2013) e Dilma 2 (2017) depois; Lula 3 com a de 2017, antes do mandato.
- **Decidido pelo Antônio:** mostrar as avaliações retrospectivas com a ressalva (ano e "depois do
  mandato") e, para Lula 3, a de 2017 com a ressalva "antes deste mandato" ("os presidentes precisam ter
  notas"). Alternativa descartada: lacuna para Lula 3.
- **Exibição:** linha "Presidente" no Início (na foto, o presidente na data; nos eleitos, o do início da
  legislatura) e na página Governos. Sem marca no hemiciclo: a nota do presidente é, em geral, de outra
  onda que a usada no arco, e a partir de 2023 o arco usa outra escala.
