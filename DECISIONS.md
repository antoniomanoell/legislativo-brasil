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
  judiciais posteriores (ex.: 7 cadeiras de 2022 trocadas por decisão do STF em 2025).
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

