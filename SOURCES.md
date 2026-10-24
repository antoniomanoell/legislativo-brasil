# SOURCES.md — fontes

Registro de cada fonte: URL, data de acesso, licença/termos de uso e forma de citação (PROJECT.md,
seção 0, regra 3). Todas as entradas abaixo foram conferidas diretamente na origem em **2026-10-23**
(Fase 0), salvo indicação em contrário. Limitações e consequências para o projeto estão em
`reports/fase0_viabilidade.md`.

---

## Câmara dos Deputados — Dados Abertos

**API v2** — https://dadosabertos.camara.leg.br/api/v2 (OpenAPI: `/api/v2/api-docs`, versão 0.4.346)
**Arquivos em lote** — https://dadosabertos.camara.leg.br/swagger/arquivos.html; padrão
`http://dadosabertos.camara.leg.br/arquivos/{conjunto}/{formato}/{conjunto}-{ano}.{formato}`
(csv `;` UTF-8 com BOM, xlsx, ods, json, xml; sem Parquet; regerados diariamente).

- **Licença:** sem licença nomeada. Termos gerais do portal, item 2: "Todas as informações publicadas
  no Portal da Câmara são de domínio público, gratuitas e podem ser reproduzidas desde que citada a
  fonte 'Câmara dos Deputados' e a autoria da informação, quando houver."
  (https://www2.camara.leg.br/termo-de-uso-e-politica-de-privacidade/termos-gerais). Uso comercial
  permitido (https://dadosabertos.camara.leg.br/faq/faq-home.html).
- **Citação:** "Fonte: Câmara dos Deputados — Dados Abertos (dadosabertos.camara.leg.br), acesso em
  [data]."
- **Limites:** listagens com 100 itens por página (`/deputados` aceitou 1.000); `/votacoes` com
  intervalo de no máximo 3 meses, no mesmo ano; cabeçalho `retry-after: 30`; sem limite numérico
  documentado. Para votos e orientações, usar os arquivos em lote.

| Conjunto | Cobertura verificada | Observações |
|---|---|---|
| `legislaturas` | 49ª (01/02/1991) a 57ª (até 31/01/2027) | 58ª ainda não existe |
| `deputados?idLegislatura=N` | 49ª–57ª, quem exerceu mandato (titulares e suplentes) | 49ª: 613 IDs; 58ª: 0 |
| `deputados/{id}/historico` | eventos datados só **a partir da 52ª (2003)** | 49ª–51ª: um registro artificial por legislatura ("partido no início da legislatura", `dataHora` 2023-02-01) |
| `votacoes-AAAA` | 1991+ | plenário com placar só a partir de 2001 |
| `votacoesVotos-AAAA` | **2001–2026** (2001: 1 votação; volumoso a partir de 2003) | ~639 MB no total; ausentes não listados; valores Sim, Não, Obstrução, Abstenção, Artigo 17 |
| `votacoesOrientacoes-AAAA` | **2003–2026** | Governo como "GOV." (2003–2019, 2022) ou "Governo" (2020–2021 misto, 2023+) |
| `votacoesObjetos`, `votacoesProposicoes` | — | identificam PEC; não há campo de turno nem de mérito |

**Plenário Ulysses Guimarães (Visita Virtual)** —
https://www.camara.leg.br/internet/visitaVirtual/portugues/edificioPrincipal/plenario/plenarioConteudo.html
— "o plenário permite que os deputados votem a partir de qualquer um dos assentos. Os únicos lugares
marcados são as primeiras cadeiras voltadas para o vão central, destinadas aos líderes dos partidos."
Citação: "Câmara dos Deputados, Visita Virtual — Plenário Ulysses Guimarães."

---

## TSE — Portal de Dados Abertos

https://dadosabertos.tse.jus.br (substitui o antigo Repositório de Dados Eleitorais). API CKAN:
`https://dadosabertos.tse.jus.br/api/3/action/package_show?id=candidatos-AAAA`.

- **Licença:** metadado CKAN `license_id: cc-by` ("Creative Commons Attribution", sem versão).
  Política de Dados Abertos: Portaria TSE nº 93/2021. FAQ: uso livre "limitando-se a creditar a
  autoria ou a fonte" (https://dadosabertos.tse.jus.br/pages/perguntasfrequentes).
- **Citação:** o TSE não prescreve forma. Usar "Fonte: Tribunal Superior Eleitoral — Portal de Dados
  Abertos, conjunto [nome], acesso em [data]."
- **Aviso do próprio TSE** (https://dadosabertos.tse.jus.br/about): "Estão incompletos os dados de
  candidatos e de resultados das eleições de 1994 a 1998."
- **Atenção:** `consulta_cand_AAAA` é regerado continuamente e mostra a situação **atual** de cada
  candidato (registrar `DT_GERACAO` e guardar cópia datada).

| Arquivo (`https://cdn.tse.jus.br/estatistica/sead/odsele/...`) | Uso | Observações |
|---|---|---|
| `votacao_candidato_uf/votacao_candidato_uf_1990.zip` | eleitos de 1990 | TXT sem cabeçalho, latin-1; layout no Leia-me.pdf; 503 eleitos |
| `consulta_cand/consulta_cand_AAAA.zip` (1994–2026) | eleitos por partido | CSV `;` latin-1; `DS_SIT_TOT_TURNO`; em 1998, deduplicar substitutos por UF + número |
| `consulta_cand_complementar/consulta_cand_complementar_2026.zip` | situação jurídica 2026 | julgamento, recurso, diplomação |
| `consulta_vagas/consulta_vagas_AAAA.zip` | vagas por UF | |

**Partidos registrados** — https://www.tse.jus.br/partidos/partidos-registrados-no-tse (fusões,
incorporações e mudanças de nome a partir da Lei 9.096/1995, com processo e data; bloqueia
requisições automáticas sem cabeçalhos de navegador).
**Federações** — https://www.tse.jus.br/partidos/federacoes-registradas-no-tse/federacoes-partidarias-registradas-no-tse

---

## Ideologia

| Fonte | URL | Licença | Citação (ABNT) |
|---|---|---|---|
| Artigo BLS | https://doi.org/10.1017/lap.2023.24 | CC-BY 4.0 | ZUCCO, Cesar; POWER, Timothy J. The Ideology of Brazilian Parties and Presidents: A Research Note on Coalitional Presidentialism Under Stress. **Latin American Politics and Society**, v. 66, n. 1, p. 178-188, 2024. DOI: 10.1017/lap.2023.24. |
| Estimativas BLS por partido e onda | https://doi.org/10.7910/DVN/6KVTUV (arquivo `bls9_estimates_partiespresidents_long.tab`) | CC0 1.0 | ZUCCO, Cesar; POWER, Timothy J. **Replication Data for: The Ideology of Brazilian Parties and Presidents: A Research Note on Coalitional Presidentialism Under Stress**. Harvard Dataverse, V1, 2023. DOI: 10.7910/DVN/6KVTUV. |
| Microdados BLS (formulário antes do download) | https://doi.org/10.7910/DVN/WM9IZ8 | CC0 1.0, com proibição de reidentificar respondentes | ZUCCO, Cesar *et al.* **Brazilian Legislative Surveys (Waves 1-9, 1990-2021)**. Harvard Dataverse, V1, 2023. DOI: 10.7910/DVN/WM9IZ8. |
| Bolognesi et al. 2018 | https://doi.org/10.1590/dados.2023.66.2.303 (errata: …303e) | CC-BY 4.0 | BOLOGNESI, Bruno; RIBEIRO, Ednaldo; CODATO, Adriano. Uma nova classificação ideológica dos partidos políticos brasileiros. **Dados**, Rio de Janeiro, v. 66, n. 2, e20210164, 2023. DOI: 10.1590/dados.2023.66.2.303. |
| Bolognesi et al. 2022 | https://doi.org/10.1590/1807-0191202531120 | CC-BY 4.0 | BOLOGNESI, Bruno; RIBEIRO, Ednaldo; CODATO, Adriano; SILVA, Bruno Fernando da. O desaparecimento do centro ideológico no sistema partidário brasileiro: a classificação mais atualizada dos experts. **Opinião Pública**, Campinas, v. 31, e31120, 2025. DOI: 10.1590/1807-0191202531120. |
| Dados Bolognesi 2018–2022 | https://doi.org/10.7910/DVN/MFIXKW | CC0 1.0 | BOLOGNESI, Bruno; CODATO, Adriano; RIBEIRO, Ednaldo; SILVA, Bruno Fernando da. **Database on the ideological classification of all Brazilian political parties (2018-2022)**. Harvard Dataverse, V1, 2025. DOI: 10.7910/DVN/MFIXKW. |

Notas: a BLS usa siglas atuais de linhagem (CID = PPS, DEM = PFL, MDB = PMDB, PL = PR, REP = PRB;
"PP" é a linhagem ARENA/PDS/PPR; "PP (old)" é o PP de 1993). A 10ª onda da BLS foi aplicada em
março–novembro de 2025 (Latin American Centre, Oxford: https://www.lac.ox.ac.uk/node/4900671), mas
não estava publicada em 2026-10-23.

---

## Governos e coalizões

**IPEA — Atlas do Estado Brasileiro, "Gabinetes ministeriais no Brasil (1989-2020)", Acir Almeida**
- Página: https://www.ipea.gov.br/atlasestado/consulta/154 (traz os % de cadeiras de referência do
  PROJECT.md §7.5, todos conferidos).
- CSV: https://www.ipea.gov.br/atlasestado/arquivos/downloads/6727-nroministeriosporpresidencia.csv
  (52 gabinetes, ministérios por partido, **sem datas e sem % de cadeiras**, siglas atuais).
- Nota Técnica: ALMEIDA, Acir. **Gabinetes ministeriais da Nova República (1985-2020): cargos,
  composição partidária e mudança**. Brasília: Ipea, out. 2021 (Nota Técnica Diest nº 53). DOI:
  10.38116/ntdiest53.
  https://www.ipea.gov.br/atlasestado/arquivos/rmd/1034-nt53diestgabinetesministeriaisnovarepublica.pdf
  (43 gabinetes com mês de início).
- **Licença:** rodapé do Atlas "Todos direitos reservados"; a NT 53 permite "a reprodução deste texto
  e dos dados nele contidos, desde que citada a fonte. Reproduções para fins comerciais são proibidas."
- **Citação:** "Fonte: Atlas do Estado Brasileiro - IPEA, com base em dados de Acir Almeida."
- Cobre de mar/1985 a dez/2020, segundo a própria Nota Técnica (a página do Atlas fala em coleta
  encerrada "em meados de 2020"). Sem atualização posterior; de 2021 em diante, curadoria do projeto
  (`data/manual/ministros_pos2020.csv`, com a fonte de cada nomeação).

**NIPE/Cebrap — Banco de Dados Legislativos** — https://bancodedadoslegislativos.com.br
- **Fora do ar em 2026-10-23** (domínio não resolve). Última cópia arquivada:
  https://web.archive.org/web/20260213075831/https://bancodedadoslegislativos.com.br/downloads.php
- Conteúdo (segundo a cópia): votações, votos e indicações das lideranças da Câmara (1988–2019);
  coalizões (1988–mar/2021); proposições; filiação só sob pedido; Senado "em breve".
- **Licença:** nenhuma de redistribuição publicada; "Copyright © NIPE CEBRAP"; download com cadastro.
- **Citação exigida:** "NIPE CEBRAP (2021). Banco de Dados Legislativos do CEBRAP. Visitado em
  [data]. Disponível em https://bancodedadoslegislativos.com.br"

**Datas dos governos**
- Biblioteca da Presidência, Galeria dos ex-Presidentes:
  https://www.gov.br/secretariageral/pt-br/centrais-de-conteudo/biblioteca-da-pr/galeria-dos-ex-presidentes/
- Posse de Temer (31/08/2016): https://www.congressonacional.leg.br/sessoes/taquigrafia/-/notas/s/3925
- Bolsonaro: https://presidentes.an.gov.br/index.php/centro-de-referencia-de-acervos-presidenciais/assuntos/biografias/199-jair-messias-bolsonaro
  (trocas de partido só confirmadas na imprensa: PSL em 07/03/2018, desfiliação em 19/11/2019, PL em
  30/11/2021).
- EC 111/2021 (DOU 29/09/2021): https://www.planalto.gov.br/ccivil_03/constituicao/emendas/emc/emc111.htm
  — art. 4º: mandatos dos eleitos em 2022 "durarão até a posse de seus sucessores, em 5 e 6 de
  janeiro de 2027".

---

## Senado Federal / Congresso Nacional — Dados Abertos (Fase 4 e vetos)

- API: https://legis.senado.leg.br/dadosabertos (OpenAPI: `/dadosabertos/v3/api-docs`); portal:
  https://www12.senado.leg.br/dados-abertos
- Votações de plenário: `https://legis.senado.leg.br/dadosabertos/dados/ListaVotacoes{ANO}.xml`
  (1991–2026, com voto individual nas votações abertas). **Qualidade irregular:** em 2016, 7 das 13
  votações são de matérias de 1998–1999 e a votação final do impeachment não aparece.
- Senadores por legislatura: `/dadosabertos/senador/lista/legislatura/{n}`; filiações em
  `/senador/{codigo}/filiacoes` são fracas para o histórico (siglas atuais).
- Vetos (sessões conjuntas): `/plenario/resultado/veto/{codigo}` e
  `/plenario/resultado/veto/dispositivo/{codigo}` trazem votos de deputados (nome, partido, UF, sem o
  id da Câmara) pelo menos desde março de 2016.
- **Licença:** política de uso do portal: "pode ser utilizado pelos usuários, desde que seja citada a
  fonte e para fins lícitos"
  (https://www12.senado.leg.br/institucional/documentos/politica-de-uso-do-portal-do-senado-federal).
- **Citação:** "Fonte: Senado Federal — Dados Abertos, acesso em [data]."
- `https://www.congressonacional.leg.br/dados-abertos` responde 404.

---

## Referência de método (não usar como dado)

- Basômetro (Estadão): https://github.com/estadao/basometro — governismo a partir de 2003; abstenção
  e obstrução contam contra o governo; votações com orientação "liberado" descartadas.
- Poder360 (14/12/2023): https://www.poder360.com.br/congresso/lula-da-mais-cargos-e-verbas-e-eleva-taxa-de-governismo-na-camara/
- Congresso em Foco, Radar do Congresso (30/01/2024): https://congressoemfoco.com.br/noticia/29156/veja-quem-mais-votou-a-favor-e-contra-o-governo-na-camara-em-2023 — a falta também conta contra.
- DIAP, Análise do Governismo (jun/2023): https://www.diap.org.br/images/stories/analise_governismo_camara_2023-06.pdf
- Agência Câmara (31/07/2025), perda de mandato de 7 deputados (sobras eleitorais de 2022):
  https://www.camara.leg.br/noticias/1184072-camara-declara-a-perda-de-mandato-de-sete-deputados-federais-e-convoca-novos-eleitos/
- Câmara dos Deputados, visita virtual ao Plenário Ulysses Guimarães (396 lugares; voto de qualquer
  cadeira; primeira fila reservada aos líderes):
  https://www.camara.leg.br/internet/visitaVirtual/english/edificioPrincipal/plenario/plenarioConteudo.html
- Conjur (26/06/2025), STF mantém a regra das sobras para 2022 (ADIs 7.228 e 7.263; decisão de 2024,
  aplicação a 2022 decidida em março de 2025, embargos rejeitados em 24/06/2025):
  https://www.conjur.com.br/2025-jun-26/stf-mantem-aplicacao-de-regra-de-divisao-das-sobras-eleitorais-nas-eleicoes-de-2022/
- A Gazeta (05/2023), TSE cassa por unanimidade o registro de Deltan Dallagnol (16/05/2023):
  https://www.agazeta.com.br/brasil/por-unanimidade-tse-cassa-mandato-do-deputado-deltan-dallagnol-0523
  (no `consulta_cand_2022` do TSE ele segue "ELEITO POR QP", conferido em 2026-10-24).

---

## Diários oficiais (impeachments)

- Diário do Congresso Nacional, Seção I, nº 161, 30/09/1992 (ata da sessão de 29/09/1992; votação
  nominal nas pp. 22121–22127): https://imagem.camara.leg.br/Imagem/d/pdf/DCD30SET1992.pdf
- Diário da Câmara dos Deputados, ano LXXI, nº 056, 18/04/2016 (ata da 91ª sessão; chamada nas
  pp. 57–118): https://imagem.camara.leg.br/Imagem/d/pdf/DCD0020160418000560000.PDF
- Acervo: https://imagem.camara.leg.br (busca por data). Domínio público, citada a fonte.
- Conferência secundária: Congresso em Foco, "Quem foram os 38 deputados que votaram contra o
  impeachment de Collor"; notas taquigráficas do DETAQ da sessão 091.2.55.O (2016).

