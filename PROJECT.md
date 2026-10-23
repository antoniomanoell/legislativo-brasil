# PROJECT.md — Dashboard do Congresso Nacional (1991 → hoje)

> **Leia este arquivo inteiro antes de escrever qualquer código.**
> Este documento é autocontido: foi escrito para ser executado por uma conta/instância do Claude Code que **não tem acesso** às conversas em que o projeto foi planejado. Todo o contexto necessário está aqui. Onde algo não pôde ser verificado durante o planejamento, está marcado com **[confirmar]** — trate como hipótese a verificar na fonte, nunca como fato.
>
> Dono do projeto: **Antônio** (engenheiro civil; programa em Python, Node.js e TypeScript de backend; **não** domina React/Next.js). Todo código deve ser legível e mantível por ele.
>
> Nome provisório: **Congresso em Números** [placeholder — Antônio ainda não definiu nome].

---

## 0. Regras de trabalho para o Claude Code

1. **Pare e pergunte ao Antônio** sempre que houver ambiguidade metodológica (classificação ideológica, definição de indicador, tratamento de lacuna, escolha de fonte). Não decida sozinho questões de método. Questões puramente técnicas (bibliotecas, estrutura de pastas) você decide e registra.
2. **Nunca invente** URLs, endpoints, códigos de tabela, IDs de partido, números ou datas. Se não encontrar, registre como pendência.
3. Mantenha três arquivos vivos na raiz do repositório:
   - `DECISIONS.md` — toda decisão metodológica ou técnica relevante, com data, alternativa descartada e motivo.
   - `SOURCES.md` — cada fonte usada: URL, data de acesso, licença/termos de uso, forma de citação exigida.
   - `PENDENCIAS.md` — tudo marcado [confirmar] e o que foi descoberto ao confirmar.
4. **Todo texto explicativo voltado ao público** (página de metodologia, tooltips, notas) é rascunho até Antônio revisar. Marque com `<!-- RASCUNHO: revisar com Antônio -->`.
5. Trabalhe por fases (seção 5). Ao fim de cada fase: testes passando, `DECISIONS.md` atualizado e um resumo curto do que foi feito e do que ficou pendente.
6. Commits pequenos e descritivos, em português.

---

## 1. Visão do produto

Site **público**, em **português**, que mostra como a Câmara dos Deputados (e, numa fase posterior, o Senado) esteve composta desde **1991** (49ª legislatura, a primeira eleita sob a Constituição de 1988):

- quem era cada parlamentar e qual seu partido em cada momento;
- quantos representantes cada partido tinha;
- a posição ideológica de cada partido, com **rigor acadêmico e fonte visível**;
- quais partidos compunham a base formal de cada governo;
- o histórico de votações nominais, com indicadores (governismo, coesão) e consulta do voto individual.

Elemento visual central: um **hemiciclo** (gráfico de parlamento) que remete ao plenário físico, com as cadeiras ordenadas por posição ideológica.

O site será **separado** do projeto irmão "mapa de indicadores socioeconômicos" do Antônio, mas deve **reutilizar sua identidade visual** (seção 9) e uma arquitetura compatível, porque no futuro os dois podem ser unificados num só site.

### 1.1 Princípios inegociáveis (produto público)

1. **Neutralidade editorial.** O site descreve, não opina. Nada de adjetivos sobre partidos ou governos, nada de seleção subjetiva de "votações importantes", nenhuma narrativa de "governo bom/ruim".
2. **Toda classificação tem fonte nomeada e visível** na própria interface (ex.: "Posição: centro-direita (6,2) — fonte: Bolognesi et al., 2022").
3. **Lacuna aparece como lacuna.** Nada de interpolar, chutar ou "completar" dados. Partido sem pontuação ideológica aparece como **"não classificado"**.
4. **Não emendar séries de métodos diferentes sem sinalizar.** Quando a fonte muda, a interface marca a quebra.
5. **Página de metodologia** completa faz parte do escopo de lançamento.

---

## 2. Decisões já tomadas por Antônio

| # | Tema | Decisão |
|---|---|---|
| D1 | Público | Site publicado, aberto |
| D2 | Ordem de construção | **Câmara primeiro**; Senado numa fase posterior (mas o modelo de dados já nasce preparado para as duas Casas) |
| D3 | Início da série | **1991** (49ª legislatura). A 48ª (eleita em 1986, Constituinte) fica fora |
| D4 | Composição | **Duas visões:** (a) **eleitos** de cada eleição; (b) **foto anual em 1º de fevereiro**, contando os deputados **em exercício** nessa data (captura trocas de partido e suplentes) |
| D5 | Ideologia | **Pontuação contínua por partido e por legislatura**, com **rótulo derivado de faixas fixas**. Fonte principal: Power & Zucco (Brazilian Legislative Surveys); complementar: Bolognesi, Ribeiro, Codato (& Silva) |
| D6 | Rótulos | **Sete faixas acadêmicas:** extrema-esquerda, esquerda, centro-esquerda, centro, centro-direita, direita, extrema-direita (+ "não classificado") |
| D7 | Votações | **Ingerir todas as votações nominais**; calcular indicadores para todo o período disponível; permitir consulta do voto individual; destacar votações por **critério objetivo**, nunca por curadoria |
| D8 | Base de governo | Incluir camada de coalizão (partidos com ministério) para contrastar com ideologia e com o comportamento de voto |
| D9 | Hemiciclo | Cadeiras **ordenadas por pontuação ideológica** (esquerda → direita) |
| D10 | Design | Reutilizar a **identidade visual** do site do mapa (cores, fontes, componentes) |
| D11 | Site | Separado do mapa por enquanto; arquitetura compatível com fusão futura |

---

## 3. Contexto conceitual (necessário para não errar o produto)

### 3.1 Espectro ideológico ≠ base de governo

- **Espectro** = o que o partido defende; posição relativamente estável no eixo esquerda–direita, medida por surveys com parlamentares (Power & Zucco), surveys com especialistas (Bolognesi et al.) ou análise de programas.
- **Base de governo** = relação de troca com o Executivo (ministérios, cargos, emendas) em troca de votos. Pode ser ideologicamente heterogênea e muda em semanas.
- O Brasil funciona sob **presidencialismo de coalizão** (Abranches, 1988; Figueiredo & Limongi, 1998/1999): nenhum presidente desde 1988 teve maioria com o próprio partido ou só com seu campo ideológico. Ex.: os governos do PT tiveram maioria graças a PMDB, PP etc.; a base de FHC (PSDB, PFL, PMDB, PTB, PPB) era ideologicamente próxima dele.

### 3.2 Como se define "base" (quatro critérios que nem sempre concordam)

1. **Ministerial** — partido com ministro que o representa (critério acadêmico mais usado; Amorim Neto; Figueiredo & Limongi; série de gabinetes de Acir Almeida/IPEA).
2. **Declaratório** — decisão formal do partido (apoio, independência, oposição).
3. **Regimental** — líder do governo indicado pelo presidente; blocos; lideranças de maioria/minoria/oposição.
4. **Comportamental** — **taxa de governismo**: % de votos que seguem a orientação do líder do governo.

O site deve mostrar **(1) como "base formal"** e **(4) como "comportamento"**, lado a lado. Exemplo real que o site precisa conseguir revelar: no governo Lula 3, o União Brasil tinha ministérios e foi o partido com ministério menos fiel (~68% de governismo em 2023), enquanto o PSDB, sem cargos, acompanhou o governo em ~74% das votações (fonte: Poder360 e Congresso em Foco, 2023).

### 3.3 Por que NÃO inferir ideologia a partir das votações

No Brasil, a principal dimensão das votações nominais tende a ser **governo × oposição**, não esquerda × direita (Zucco & Lauderdale, 2011). Escalonar votos (W-NOMINATE etc.) mediria alinhamento ao governo, misturando espectro com base — exatamente a confusão que o site quer esclarecer. **Ideologia vem de surveys; votações alimentam governismo e coesão.** Não misturar.

### 3.4 A direita "envergonhada" (nota para a página de metodologia)

Nos anos 1980–90 políticos de direita evitavam se declarar assim (Rodrigues, 1987; Power). Parte do "crescimento da direita" pós-2018 é direita passando a se assumir. A página de metodologia deve mencionar isso como limitação de qualquer série ideológica longa.

---

## 4. Escopo funcional

### 4.1 Visões / páginas (MVP = Câmara)

1. **Início — Hemiciclo + linha do tempo**
   - Hemiciclo da Câmara num momento escolhido (slider: eleições e fotos anuais de 1º/fev).
   - Alternância "eleitos" × "em exercício (1º/fev)".
   - Cada cadeira = um deputado; cor = faixa ideológica do partido; agrupamento por partido.
   - Hover/toque: nome, partido naquele momento, UF, faixa e pontuação ideológica (com fonte).
   - Clique: abre o perfil do deputado.
   - Abaixo: resumo do momento (total por partido, por faixa ideológica, partidos na base formal do governo vigente).
   - **Alternativa acessível:** botão "ver como tabela" com os mesmos dados.
2. **Evolução** — gráfico de área empilhada (ou barras) do % de cadeiras por faixa ideológica ao longo do tempo; segundo gráfico por partido (respeitando linhagens, seção 7.3).
3. **Partidos** — página por partido: linhagem (nomes anteriores, fusões), tamanho ao longo do tempo, pontuação ideológica por legislatura com fonte, participação em governos, governismo e coesão.
4. **Deputados** — busca; perfil com mandatos, histórico de filiação datado, votos nominais, governismo individual.
5. **Governos** — linha do tempo dos presidentes; para cada governo: partido do presidente, base formal (partidos com ministério) e % de cadeiras ao longo do mandato, versus governismo efetivo por partido.
6. **Votações** — lista filtrável (data, tipo de proposição, resultado, destaque objetivo); página da votação com placar por partido, orientações, hemiciclo colorido pelo voto.
7. **Metodologia** — fontes, critérios, faixas ideológicas, definição de indicadores, limitações, como citar.
8. **Sobre / Dados** — download dos dados tratados (CSV/Parquet) com licença e citação [confirmar licenças antes].

### 4.2 Estado na URL

Todo estado relevante (Casa, data/foto, modo eleitos×exercício, partido/deputado/votação selecionados) vai na URL, para links compartilháveis.

### 4.3 Fora do MVP

Senado (fase 4); comparação lado a lado de dois momentos; versão em inglês; atualização automática agendada (pipeline roda manualmente).

---

## 5. Fases de construção

### Fase 0 — Fundação e verificação (bloqueante)

1. **Importar a identidade visual do mapa** (seção 9). Sem isso, não comece frontend.
2. Verificar **todas** as fontes da seção 6: endpoints, cobertura temporal real, formatos, limites de requisição, **licenças e termos de redistribuição**. Atualizar `SOURCES.md` e `PENDENCIAS.md`.
3. Confirmar especificamente:
   - de que ano a API/arquivos da Câmara têm **votações nominais com voto individual** e **orientação do governo** estruturada;
   - o que o Banco de Dados Legislativos do **Cebrap** disponibiliza para download público (votações nominais da Câmara desde 1988; senadores 1988–2019 estava previsto) e sob quais termos;
   - disponibilidade e licença do dataset dos **Brazilian Legislative Surveys** (Power & Zucco) e das tabelas de Bolognesi et al.;
   - se o histórico de filiação partidária da API da Câmara cobre os anos 1990.
4. Esqueleto do repositório (seção 8), CI rodando testes.
5. **Entregar ao Antônio um relatório de viabilidade** antes de seguir: o que existe, o que não existe, o que exigirá curadoria manual.

### Fase 1 — Composição da Câmara + ideologia + hemiciclo

- Pipeline: legislaturas 49ª–58ª, deputados, mandatos/exercícios, filiações datadas, partidos e linhagens.
- Fotos: eleitos por eleição; em exercício em 1º/fev de cada ano.
- Tabela de ideologia partido × legislatura com fonte (seção 7.4).
- Frontend: Início (hemiciclo + slider + tabela acessível), Evolução, Partidos (versão básica), Metodologia (rascunho).
- Validação contra o Apêndice A.

### Fase 2 — Governos e coalizões

- Tabela de governos e de composição ministerial por partido (IPEA/Acir Almeida até meados de 2020; depois, curadoria documentada — seção 6.4).
- Página Governos; indicação da base formal no Início.

### Fase 3 — Votações da Câmara

- Ingestão de todas as votações nominais disponíveis (oficial + Cebrap para o período anterior, se licença permitir).
- Indicadores: governismo e coesão (seção 7.6); destaques objetivos (seção 7.7).
- Páginas Votações e Deputados completas; governismo na página Governos.

### Fase 4 — Senado

- Mesmo modelo com particularidades da seção 7.8.

### Fase 5 — Conteúdo e lançamento

- Revisão de todo texto com Antônio; página de metodologia final; acessibilidade e performance (seção 10); downloads de dados; deploy.

---

## 6. Fontes de dados

> Todas as URLs abaixo foram identificadas no planejamento, mas **endpoints, cobertura e licenças devem ser verificados na Fase 0**.

### 6.1 Composição e parlamentares

| Fonte | Uso | Observações |
|---|---|---|
| **Dados Abertos da Câmara** — https://dadosabertos.camara.leg.br (API REST v2, OpenAPI; também arquivos em lote) | legislaturas, deputados, histórico de status/filiação, partidos, blocos, votações | Verificar cobertura dos anos 1990 no histórico de filiação [confirmar] |
| **TSE — Portal de Dados Abertos / Repositório de dados eleitorais** — https://dadosabertos.tse.jus.br | eleitos por eleição (1994+ com microdados) | Para 1990 os microdados podem não existir; usar Câmara/fontes secundárias e documentar [confirmar] |
| **Dados Abertos do Senado** — https://dadosabertos.senado.leg.br (API em https://legis.senado.leg.br/dadosabertos) | Fase 4 | Lista votações nominais por ano a partir de 2003 |

### 6.2 Ideologia

| Fonte | Cobertura | Observações |
|---|---|---|
| **Power & Zucco — Brazilian Legislative Surveys (BLS)**. Artigo: Zucco & Power, "The Ideology of Brazilian Parties and Presidents: A Research Note on Coalitional Presidentialism Under Stress", *Latin American Politics and Society* (Cambridge). Suplemento com estimativas completas (Tabela C1): https://static.cambridge.org/content/id/urn:cambridge.org:id:article:S1531426X23000249/resource/name/S1531426X23000249sup001.pdf | Ondas em 1990, 1993, 1997, 2001, 2005, 2009, 2013, 2017, 2021 — **uma por legislatura** (48ª a 56ª) | Única série longa. Cobre os principais partidos, não todos. Dataset possivelmente no Harvard Dataverse [confirmar] |
| **Bolognesi, Ribeiro & Codato (2023)**, "Uma nova classificação ideológica dos partidos políticos brasileiros", *Dados* 66(2) — https://doi.org/10.1590/dados.2023.66.2.303 | 2018, todos os 35 partidos então registrados, escala 0–10 | Survey com especialistas |
| **Bolognesi, Ribeiro, Codato & Silva**, "O desaparecimento do centro ideológico no sistema partidário brasileiro: a classificação mais atualizada dos experts", *Opinião Pública* (Unicamp) — https://periodicos.sbu.unicamp.br/ojs/index.php/op/article/view/8682072 | 2018 e 2022, todos os partidos registrados (32 em 2022), escala 0–10, 477 respondentes | Fonte das **sete faixas** e de seus pontos de corte [confirmar cortes no artigo] |

### 6.3 Votações

| Fonte | Cobertura | Observações |
|---|---|---|
| **Câmara — Dados Abertos** (votações, votos, orientações) | Período recente; ano inicial de voto individual + orientação [confirmar] | Fonte primária quando disponível |
| **Cebrap — Banco de Dados Legislativos** (Figueiredo & Limongi) | Votações nominais de deputados desde 1988; senadores 1988–2019 (previsto) [confirmar] | Única fonte sólida para os anos 1990; verificar termos de redistribuição antes de publicar |
| **Senado — votações nominais** — https://www12.senado.leg.br/dados-abertos/legislativo/plenario/votacoes-nominais/info | 2003+ | Fase 4 |

### 6.4 Governos e coalizões

| Fonte | Cobertura | Observações |
|---|---|---|
| **IPEA — Atlas do Estado Brasileiro, "Gabinetes ministeriais no Brasil (1989-2020)"**, por Acir Almeida — https://www.ipea.gov.br/atlasestado/consulta/154 (com CSV para download) | 1989 até meados de 2020 | Critério ministerial; nota metodológica na própria página |
| Curadoria manual (Diário Oficial da União, Agência Câmara/Senado, imprensa) | meados de 2020 → hoje | Cada registro com link de fonte em `data/manual/coalizoes_pos2020.csv`; validar com Antônio |

### 6.5 Fontes jornalísticas (somente para validação, nunca como dado primário)

Poder360, Congresso em Foco, Agência Câmara, Agência Senado, DIAP. Úteis para conferir totais.

---

## 7. Regras metodológicas

### 7.1 Período e legislaturas

| Legislatura | Período | Cadeiras na Câmara |
|---|---|---|
| 49ª | 1991–1995 | 503 [confirmar: fonte indica que passou de 495 para 503 com a criação de AP e RR como estados] |
| 50ª | 1995–1999 | 513 |
| 51ª | 1999–2003 | 513 |
| 52ª | 2003–2007 | 513 |
| 53ª | 2007–2011 | 513 |
| 54ª | 2011–2015 | 513 |
| 55ª | 2015–2019 | 513 |
| 56ª | 2019–2023 | 513 |
| 57ª | 2023–2027 | 513 |
| 58ª | 2027–2031 | 513 (eleita em 4/out/2026; posse em 1º/fev/2027) |

### 7.2 Composição

- **Eleitos:** resultado oficial de cada eleição, pelo partido de eleição.
- **Em exercício em 1º/fev de cada ano:** quem estava efetivamente no exercício do mandato nessa data (titular ou suplente), pelo partido de filiação nessa data.
  - Se 1º/fev cair antes da posse de uma nova legislatura no mesmo dia, considerar a composição **após** a posse [registrar em DECISIONS].
- **Invariante:** em cada foto, o total de cadeiras ocupadas ≤ total de cadeiras da legislatura; vagas eventualmente desocupadas aparecem como "vaga".
- **Validação cruzada:** o partido registrado em cada voto nominal (dados de votação) deve bater com o histórico de filiação na data do voto. Divergências vão para um relatório `reports/divergencias_filiacao.csv`.

### 7.3 Partidos, linhagens e federações

- Cada partido tem um **ID estável interno** independente da sigla.
- Tabela de **linhagem** registra renomeações, fusões e incorporações com data. Gráficos de série temporal oferecem a opção "seguir linhagem".
- **Homônimos são partidos diferentes:** o PSD de 1987–2003 (incorporado ao PTB) ≠ o PSD fundado em 2011. O PP de 1993–1995 ≠ o PP/Progressistas de 2003 em diante (que descende do PPB).
- **Federações** (a partir de 2022) são registradas à parte; a composição é sempre por **partido**, com a federação como atributo.
- Lista inicial de linhagens no Apêndice B — **todas as datas e eventos devem ser confirmados no TSE**.

### 7.4 Ideologia

**Unidade:** pontuação por **partido × legislatura**, com `fonte`, `ano_da_medicao`, `escala_original`, `n` (se disponível).

**Regra de atribuição:**

1. Legislaturas 49ª a 56ª: usar a onda BLS (Power & Zucco) realizada **durante aquela legislatura** (1993→49ª, 1997→50ª, 2001→51ª, 2005→52ª, 2009→53ª, 2013→54ª, 2017→55ª, 2021→56ª).
2. Partido ausente na onda BLS correspondente: usar Bolognesi et al. **somente se** houver medição próxima (2018 para a 55ª/56ª; 2022 para a 56ª/57ª); caso contrário, **"não classificado"**.
3. Legislaturas 57ª e 58ª: Bolognesi et al. 2022, ou nova onda BLS se existir [confirmar]. Para a 58ª, sinalizar "medição de 2022 aplicada a legislatura iniciada em 2027".
4. Nunca interpolar entre ondas. Nunca herdar pontuação de outro partido da linhagem sem regra aprovada pelo Antônio.

**Faixas (sete) — PONTO QUE EXIGE APROVAÇÃO DO ANTÔNIO ANTES DO LANÇAMENTO:**

- As sete faixas e seus pontos de corte vêm de Bolognesi et al., aplicáveis à **escala 0–10 deles** [confirmar cortes exatos no artigo].
- As pontuações BLS (Power & Zucco) estão em **outra escala e outro método** (survey com parlamentares). **Não aplique os cortes de Bolognesi diretamente às pontuações BLS.**
- Tarefa: usando os partidos medidos por ambos em datas próximas (BLS 2017/2021 × Bolognesi 2018/2022), estimar e documentar uma correspondência (crosswalk) entre as escalas. Apresentar ao Antônio: método, ajuste, partidos fora da correspondência e o efeito nos rótulos. **Só depois** gerar rótulos para 1991–2018.
- A interface mostra sempre: rótulo, pontuação na escala original e fonte. Quando a fonte muda entre legislaturas, marcar a quebra nos gráficos.

**Ordem no hemiciclo:** partidos ordenados pela pontuação (esquerda → direita); dentro do partido, deputados em ordem alfabética. Partidos **"não classificados"** ficam **fora da ordenação**, num bloco separado e claramente rotulado (ex.: fileira à parte), para não sugerir uma posição ideológica.

### 7.5 Governos

| Presidente | Partido | Período |
|---|---|---|
| Fernando Collor | PRN | 15/03/1990 – 01/10/1992 (afastado em 02/10/1992; renunciou em 29/12/1992) |
| Itamar Franco | sem partido durante o mandato | 02/10/1992 – 31/12/1994 |
| Fernando Henrique Cardoso | PSDB | 01/01/1995 – 31/12/2002 |
| Luiz Inácio Lula da Silva | PT | 01/01/2003 – 31/12/2010 |
| Dilma Rousseff | PT | 01/01/2011 – 12/05/2016 (afastada); impeachment em 31/08/2016 |
| Michel Temer | PMDB/MDB | 12/05/2016 (interino) – 31/12/2018 |
| Jair Bolsonaro | PSL → sem partido → PL | 01/01/2019 – 31/12/2022 |
| Luiz Inácio Lula da Silva | PT | 01/01/2023 – 05/01/2027 |
| A definir | — | a partir de 05/01/2027 [preencher após o resultado oficial] |

Todas as datas [confirmar]. A série do site começa em 1991; o governo Collor entra a partir de fevereiro de 1991.

A EC 111/2021 moveu a posse presidencial para **5 de janeiro**, a partir da eleição de 2026; por isso o mandato iniciado em 2023 termina em 05/01/2027.

**Base formal:** partidos com ministério que os representa, por período (critério IPEA/Acir Almeida). Exibir como % de cadeiras na foto correspondente.

Valores de referência do IPEA para validação (% da Câmara): FHC 1 — 35,5% (aliança eleitoral) → 56% (+PMDB) → 77% (+PPB, mai/1996); FHC 2 — 75% → 45,5% (saída do PFL, mar/2002); Lula 1 — 48,5% → 62,5% → 68%; Lula 2 — 70%; Dilma 1 — 72,5% → 78,5% → 62,5%; Dilma 2 — 59,5% → 64% → 41% (mar/2016); Temer — 65,5%; Bolsonaro — 16,5% (início). Esses valores usam a composição da época calculada pelo IPEA; diferenças pequenas em relação ao nosso cálculo são esperadas e devem ser explicadas em `DECISIONS.md`.

### 7.6 Indicadores de votação

**Escopo:** votações nominais em plenário.

**Taxa de governismo (partido ou deputado):**

- Considerar apenas votações em que o governo orientou **Sim** ou **Não**.
- Numerador: votos iguais à orientação do governo.
- Denominador: votos Sim + Não + Abstenção + Obstrução do parlamentar/partido naquela votação.
- **[decisão do Antônio]** Como tratar "Obstrução" quando a orientação é "Não", e "Abstenção" em geral. Apresentar as opções usadas na literatura e no DIAP/Poder360/Congresso em Foco e pedir a escolha; registrar em `DECISIONS.md`.
- Ausências não entram no denominador; exibir a taxa de presença à parte.

**Coesão partidária:** Índice de Rice por votação = |%Sim − %Não| entre os votantes do partido; média por período. Registrar a escolha e a alternativa considerada (ex.: Agreement Index de Hix, Noury & Roland).

**Período sem orientação do governo estruturada:** se o Cebrap tiver orientação do líder do governo, usar com nota de fonte; se não, **não calcular governismo** para esse período (mostrar lacuna).

### 7.7 Destaque objetivo de votações

Uma votação é destacada se, e somente se, se enquadrar em critério objetivo:

1. Proposta de Emenda à Constituição (PEC) — votações de mérito em 1º e 2º turno;
2. Autorização para instauração de processo de impeachment (1992; 2016);
3. Votação de vetos, **se** os dados da sessão do Congresso trouxerem o voto nominal dos deputados [confirmar].

Nenhuma outra seleção manual. A lista de critérios aparece na página de metodologia.

### 7.8 Senado (Fase 4)

- 81 cadeiras; mandatos de 8 anos; renovação alternada de 1/3 e 2/3; mandatos atravessam duas legislaturas; suplentes frequentes.
- A "foto de 1º/fev" se aplica igualmente; "eleitos" mostra apenas os eleitos naquela eleição (1/3 ou 2/3), com o restante como "mandato em curso".

---

## 8. Arquitetura técnica

Mantém a mesma filosofia do projeto do mapa: **site estático, sem backend**, com pipeline em Python gerando arquivos pré-processados.

```
legislativo-brasil/
├── PROJECT.md  DECISIONS.md  SOURCES.md  PENDENCIAS.md
├── pipeline/                 # Python 3.12+
│   ├── extract/              # um módulo por fonte (camara.py, tse.py, cebrap.py, ipea.py, ideologia.py)
│   ├── transform/            # normalização, linhagens, fotos, indicadores
│   ├── load/                 # gera saídas para o site
│   ├── validate/             # checagens (seção 10.1)
│   └── run.py                # CLI: python -m pipeline.run --fase 1
├── data/
│   ├── raw/                  # cache bruto (fora do git se grande)
│   ├── manual/               # CSVs curados à mão, cada linha com fonte
│   └── processed/            # Parquet (DuckDB para transformar)
├── web/                      # Vite + TypeScript, sem framework de UI
│   ├── src/
│   │   ├── design/           # tokens e componentes importados do mapa (seção 9)
│   │   ├── charts/           # hemiciclo, área empilhada, etc. (D3 modular)
│   │   └── pages/
│   └── public/data/          # JSON gerado pelo pipeline
└── tests/
```

- **Pipeline:** Python; DuckDB + Parquet para transformação; requests com cache local e respeito a limites das APIs; execução **manual** (sem agendamento).
- **Frontend:** Vite + TypeScript **puro**, sem React/Vue/Svelte (Antônio precisa conseguir manter). Gráficos com módulos do D3. Roteamento simples por URL.
- **Volume de votações:** milhões de votos individuais. Não servir num JSON único. Opções a avaliar e registrar em `DECISIONS.md`: (a) um JSON por votação + um por deputado + agregados por partido/período; (b) Parquet consultado no navegador com DuckDB-WASM sob demanda. Escolher a mais simples que cumpra o orçamento de performance (seção 10).
- **Hemiciclo:** implementação própria em TypeScript/SVG. Algoritmo de "parliament diagram": distribuir N cadeiras em k fileiras semicirculares concêntricas, proporcional ao comprimento de cada arco, preenchendo por ângulo da esquerda para a direita. Deve aceitar N variável (503, 513, 81). Incluir nota visível: **"a posição das cadeiras é representativa; não corresponde ao assento real no plenário"**. (Até onde se apurou no planejamento, os deputados não têm lugar fixo no Plenário Ulysses Guimarães; para o Senado não foi confirmado — [confirmar] e ajustar o texto.)
- **Hospedagem:** estática (Cloudflare Pages, Netlify ou GitHub Pages) [decidir com Antônio na Fase 5].

---

## 9. Identidade visual (importar do projeto do mapa)

Antônio investiu esforço para deixar o design do site do mapa bom, e quer **o mesmo visual** aqui. **Este documento não contém os tokens de design**, porque o projeto do mapa não estava acessível durante o planejamento.

**Primeira tarefa da Fase 0:**

1. Peça ao Antônio acesso ao repositório (ou pasta) do site do mapa de indicadores socioeconômicos — **versão atual**, não as iniciais.
   - **Localizado (2026-10-23):** https://github.com/antoniomanoell/mapa-brasil (site "Indicadores BR", publicado em indicadores-br.vercel.app). O repositório deste projeto é https://github.com/antoniomanoell/legislativo-brasil.
2. Extraia para `web/src/design/`:
   - tokens de cor (incluindo modo escuro, se houver), tipografia (famílias, pesos, escala), espaçamentos, raios, sombras, breakpoints;
   - componentes reutilizáveis (cabeçalho, rodapé, slider temporal, cards, tooltips, botões, painel lateral, legendas);
   - padrões de layout e de interação (como o mapa abre detalhes, como mostra fontes e notas).
3. Documente em `web/src/design/DESIGN.md` o que foi importado e de qual arquivo/commit do mapa veio.
4. Mostre ao Antônio uma página de amostra (style guide) com os componentes importados **antes** de construir as páginas.

**Cores das faixas ideológicas — [decisão do Antônio]:**

- Requisitos: escala divergente de 7 tons + cinza para "não classificado"; acessível a daltônicos; contraste adequado nos tons do design do mapa.
- **Evitar cores de marca partidária** (muitos partidos usam vermelho/azul/verde, o que confunde e pode parecer alinhamento). Cor = faixa ideológica; identidade do partido = rótulo e separadores.
- Apresentar 2–3 paletas candidatas compatíveis com a identidade do mapa e deixar Antônio escolher.

---

## 10. Qualidade

### 10.1 Validações automáticas do pipeline

- Soma de cadeiras por foto = total de cadeiras da legislatura (descontadas vagas registradas).
- Totais de eleitos por partido conferem com o Apêndice A (tolerância de ±2 por partido, porque as fontes divergem; divergências maiores geram alerta e investigação).
- Todo deputado em exercício tem exatamente um partido na data da foto.
- Toda pontuação ideológica tem fonte, ano e escala.
- Todo registro manual tem URL de fonte.
- Governismo e coesão entre 0 e 1; votações sem orientação excluídas do governismo.

### 10.2 Frontend

- Lighthouse ≥ 90 em performance e acessibilidade.
- Carga inicial < 500 KB (sem contar dados sob demanda).
- Hemiciclo navegável por teclado; tabela alternativa para leitores de tela.
- Responsivo: funcionar bem em celular (o hemiciclo precisa de interação por toque e zoom).

---

## 11. Pendências que exigem decisão do Antônio

1. Correspondência (crosswalk) entre as escalas BLS e Bolognesi e os cortes das sete faixas (seção 7.4).
2. Tratamento de abstenção/obstrução no governismo (seção 7.6).
3. Paleta de cores das faixas (seção 9).
4. Nome do site e domínio.
5. Hospedagem.
6. Licença dos dados derivados publicados (após verificar licenças das fontes).
7. Curadoria das coalizões de meados de 2020 em diante (validar a tabela manual).
8. Questões de método levantadas na revisão de 2026-10-23 (onda BLS da 49ª, prioridade Bolognesi na 56ª, voto "Art. 17", votantes no Rice, PEC "de mérito", impeachment de 1992) — detalhadas em `PENDENCIAS.md`.

---

## Apêndice A — Bancadas eleitas na Câmara (referência para validação)

> Compilado de fontes secundárias (IFES ElectionGuide, Georgetown PDBA, Wikipedia, Poder360, Congresso em Foco, Câmara). **Use somente para validar** o pipeline; os números oficiais vêm das fontes primárias. Fontes divergem em ±1–2 cadeiras (ex.: 1994 PFL 89/90/92; 2002 PMDB 74/75/76; 2014 PT 68/69/70).

| Eleição | Maiores bancadas eleitas |
|---|---|
| 1990 (503) | PMDB 108, PFL 83, PDT 46, PDS 42, PRN 40, PSDB 38, PTB 38, PT 35, PDC 22, PL 16 |
| 1994 | PMDB 107, PFL 89, PSDB 62, PPR 52, PT 49, PP 36, PDT 34, PTB 31, PSB 15, PL 13 |
| 1998 | PFL 105, PSDB 99, PMDB 83, PPB 60, PT 58, PTB 31, PDT 25 |
| 2002 | PT 91, PFL 84, PMDB 75, PSDB 70, PPB 49, PL 26, PTB 26, PSB 22, PDT 21, PPS 15, PCdoB 12 |
| 2006 | PMDB 89, PT 83, PSDB 65, PFL 65, PP 41, PSB 27, PDT 24, PR 23, PTB 22, PPS 21 |
| 2010 | PT 88, PMDB 79, PSDB 53, DEM 43, PP 41, PR 41, PSB 34, PDT 28 |
| 2014 | PT 70, PMDB 66, PSDB 54, PP 38, PSD 37, PR 34, PSB 34, PTB 25, PRB 21, DEM 21 |
| 2018 | PT 56, PSL 52, PP 37, MDB 34, PSD 34, PR 33, PSB 32, PRB 30, DEM 29, PSDB 29, PDT 28 |
| 2022 | PL 99, PT 68 (federação 80), União 59, PP 47, MDB 42, PSD 42, Republicanos 41, PDT 17, PSB 14, PSDB 13, PSOL 12, Podemos 12 |
| 2026 | PL 121, PT 70 (federação 88), União 46, PSD 43, PP 41, Republicanos 41, MDB 36, Podemos 27, PSB 15, Novo 10 — **provisório**: compilado poucos dias após a eleição de 4/out/2026; conferir com o resultado consolidado do TSE (retotalizações podem alterar) |

Composição estimada por blocos (classificação clássica, sem fonte nomeada — para comparação qualitativa interna apenas, **nunca exibir no site**): a esquerda nunca passou de ~38% da Câmara (pico em 2010); a direita superou 50% em 1990, 2018, 2022 e 2026.

## Apêndice B — Linhagens partidárias (lista inicial, TODAS [confirmar] no TSE)

- PMDB → MDB (2017)
- PFL → DEM (2007) → União Brasil (2022, fusão DEM + PSL)
- PSL → União Brasil (2022)
- PDS + PDC → PPR (1993) → PPB (1995, fusão PPR + PP) → PP (2003) → Progressistas (2017)
- PST + PTR → PP (1993) → PPB (1995)
- PGT e PST incorporados ao PL (2003)
- PL → PR (2006, fusão PL + PRONA) → PL (2019); PRONA existiu de 1989 a 2006
- PRB → Republicanos (2019)
- PCB → PPS (1992) → Cidadania (2019) — o PCB tinha deputados na 49ª legislatura
- PTdoB → Avante (2017)
- PTN → Podemos (2017); PHS incorporado ao Podemos (2019); PSC incorporado ao Podemos (2023)
- PEN → Patriota (2017); PRP incorporado ao Patriota (2019); Patriota + PTB → PRD (2023)
- PSDC → DC (2017)
- PPL incorporado ao PCdoB (2019)
- PROS incorporado ao Solidariedade (2023) (sigla SD; não houve renomeação)
- PAN incorporado ao PTB (2007)
- PRN → PTC (2000) → Agir (2022)
- PSD (1987) incorporado ao PTB (2003) — **não confundir** com PSD (2011)
- Missão — partido recente com 1 deputado eleito em 2026 [confirmar data de registro]
- Federações (a partir de 2022): PT–PCdoB–PV (Brasil da Esperança); PSDB–Cidadania; PSOL–Rede; PP–União Brasil (União Progressista); PRD–Solidariedade (Renovação Solidária) [confirmar datas e composição]

## Apêndice C — Referências

- Abranches, S. (1988). Presidencialismo de coalizão: o dilema institucional brasileiro. *Dados*, 31(1).
- Figueiredo, A. & Limongi, F. (1999). *Executivo e Legislativo na nova ordem constitucional*. FGV.
- Amorim Neto, O. (2000). Gabinetes presidenciais, ciclos eleitorais e disciplina legislativa no Brasil. *Dados*, 43(3).
- Zucco, C. & Power, T. J. — *The Ideology of Brazilian Parties and Presidents: A Research Note on Coalitional Presidentialism Under Stress*. *Latin American Politics and Society* (Cambridge).
- Power, T. J. & Zucco, C. (2009). Estimating Ideology of Brazilian Legislative Parties, 1990–2005. *Latin American Research Review*.
- Zucco, C. & Lauderdale, B. (2011). Distinguishing between Influences on Brazilian Legislative Behavior. *Legislative Studies Quarterly*, 36(3).
- Bolognesi, B., Ribeiro, E. & Codato, A. (2023). Uma nova classificação ideológica dos partidos políticos brasileiros. *Dados*, 66(2).
- Bolognesi, B., Ribeiro, E., Codato, A. & Silva, B. F. O desaparecimento do centro ideológico no sistema partidário brasileiro. *Opinião Pública* (Unicamp).
- Rodrigues, L. M. (1987). *Quem é quem na Constituinte*. OESP/Maltese.
- Almeida, A. Gabinetes ministeriais no Brasil (1989–2020). IPEA, Atlas do Estado Brasileiro.
- Hix, S., Noury, A. & Roland, G. (2005). Power to the Parties: Cohesion and Competition in the European Parliament. *British Journal of Political Science* (Agreement Index).
