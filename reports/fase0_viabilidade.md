# Relatório de viabilidade — Fase 0

Data: 2026-10-23. Base: verificação direta das fontes da seção 6 do PROJECT.md (detalhes, URLs e
licenças em `SOURCES.md`; decisões pendentes em `PENDENCIAS.md`).

## Resumo

O projeto é viável. Há, porém, uma **fronteira em 2003**:

- **De 2003 em diante**, dados oficiais e abertos cobrem quase tudo o que o PROJECT.md pede:
  composição datada, voto individual e orientação do Governo.
- **De 1991 a 2002**, há três situações:
  - **Bem coberto:** os eleitos (TSE) e a ideologia (BLS).
  - **Sem fonte oficial:** a composição em exercício em 1º/fev e o partido datado de cada deputado.
  - **Só no Cebrap:** as votações nominais. O site do Cebrap está fora do ar e o banco não tem licença
    que permita redistribuir os dados.

A ideologia é o ponto mais forte. As duas fontes são CC0, ou seja, de redistribuição livre, e trazem
os pontos de corte literais. O ponto mais fraco são os anos 1990.

## O que existe, o que não existe, o que exige curadoria

| Necessidade (PROJECT.md) | Situação | Fonte |
|---|---|---|
| Legislaturas 49ª–57ª | **Existe** | Câmara |
| 58ª legislatura (eleita em 2026) | Não existe ainda na Câmara; **curadoria** a partir do TSE | TSE |
| Eleitos por eleição, 1990–2026 | **Existe** (1990 em TXT sem cabeçalho; 2026 provisório) | TSE |
| Quem exerceu mandato, por legislatura | **Existe** (titulares e suplentes, sem datas antes de 2003) | Câmara |
| Fotos em exercício em 1º/fev, 2003+ | **Existe** (histórico datado de status e partido) | Câmara |
| Fotos em exercício em 1º/fev, 1991–2002 | **Não existe** em fonte aberta | Cebrap (sob pedido) ou curadoria |
| Linhagens partidárias desde 1995 | **Existe**, com data e processo | TSE |
| Linhagens antes de 1995 | **Curadoria** (outra fonte documental) | — |
| Ideologia, 48ª–56ª (BLS) | **Existe**, CC0, escala −1/+1 com erro-padrão | Harvard Dataverse |
| Ideologia, 2018 e 2022 (Bolognesi) | **Existe**, CC0, com cortes das sete faixas | Harvard Dataverse |
| Ideologia, 57ª (2023–2027) | Só Bolognesi 2022 (BLS 2025 aplicada mas não publicada) | — |
| Base formal (ministérios), 1989–meados de 2020 | **Existe**, mas o CSV não tem datas; as datas estão na Nota Técnica 53. Uso comercial proibido | IPEA |
| Base formal, meados de 2020 → hoje | **Curadoria** (prevista no PROJECT.md) | DOU, imprensa |
| Voto individual, 2001–2026 | **Existe** (~639 MB em CSV) | Câmara |
| Orientação do Governo, 2003–2026 | **Existe** (nem toda votação tem) | Câmara |
| Voto individual e orientações, 1991–2000 | Só no Cebrap: **fora do ar e sem licença** | Cebrap |
| Votos nos impeachments (1992, 2016) | **Não existe** nos dados abertos; só o placar | Diário da Câmara (curadoria) |
| PEC: votações de mérito em 1º/2º turno | PEC identificável; turno e mérito **só pelo texto** | Câmara |
| Vetos com voto nominal de deputados | Existe desde ~2016, **sem o id da Câmara** | Senado |
| Senado (Fase 4): votos, 1991+ | Existe, com qualidade irregular (ex.: 2016) | Senado |

## Consequências por fase

**Fase 1 (composição + ideologia + hemiciclo).**
- Viável para todas as eleições (1990–2026) na visão "eleitos" e para as fotos de 2003 a 2026.
- As fotos de 1991 a 2002 dependem da decisão A15.
- A tabela de ideologia pode ser montada já. Os rótulos dependem das decisões A7 (crosswalk) e A17
  (média ponderada ou bruta).

**Fase 2 (governos).**
- Viável até meados de 2020 com o IPEA. As datas dos gabinetes vêm da Nota Técnica 53 (decisão A18).
- Depois disso, curadoria manual, como já previsto.
- Os valores de referência do §7.5 conferem todos com o texto do IPEA.

**Fase 3 (votações).**
- Viável a partir de 2003 com governismo, e de 2001 só com votos.
- Os anos 1990 dependem de autorização do Cebrap (A16). O §7.6 já prevê mostrar a lacuna se ela não vier.
- Os impeachments dependem de A6.

**Fase 4 (Senado).**
- Votos desde 1991 existem, mas exigem validação ano a ano.
- As filiações históricas de senadores precisarão de outra fonte.
- O Cebrap nunca publicou os votos do Senado.

## Validação do Apêndice A contra o TSE

O TSE mostra a situação **atual** de cada candidato, não a da noite da eleição. Por isso é preciso
definir o que é "eleito" (A14). Divergências encontradas (Apêndice → TSE):

| Ano | Divergências |
|---|---|
| 1990 | PDS 42→45, PRN 40→38, PTB 38→37 |
| 1994 | PSDB 62→63, PPR 52→51, PT 49→50, PP 36→34, PTB 31→32 |
| 1998 | PT 58→59 |
| 2002 | PMDB 75→76, PPB 49→48 |
| 2006 | PSDB 65→66, PPS 21→22. O "PR 23" do Apêndice era, na eleição, PL 23 + PRONA 2 (corrigido) |
| 2010 | PT 88→86, PMDB 79→78, PSDB 53→54, PP 41→44, PSB 34→35, PDT 28→27 |
| 2014 | PT 70→69, PMDB 66→65, PSD 37→36 |
| 2018 | PSD 34→35, PRB 30→29, PSDB 29→30 |
| 2022 | PL 99→98, PT 68→69, União 59→57, MDB 42→41, Republicanos 41→40, PDT 17→16, PSB 14→15, PSOL 12→13, Podemos 12→14 (parte delas pela troca de 7 cadeiras decidida pelo STF) |
| 2026 | Os 10 partidos listados batem |

A tolerância de ±2 por partido da seção 10.1 absorve quase tudo. Excedem a tolerância: PDS em 1990
(+3), PP em 2010 (+3) e Podemos em 2022 (+2, no limite). Esses casos precisam ser investigados na
Fase 1.

## Recomendações

1. **Escrever ao NIPE/Cebrap** pedindo os dados (votos 1988–2002, indicações das lideranças e
   filiação de deputados) e **autorização para publicar dados derivados**. É a única fonte para os
   anos 1990. O pedido pode correr em paralelo com a Fase 1. Posso redigir o e-mail.
2. **Começar a Fase 1 pelo período 2003–2026 e pelos eleitos de 1990 a 2026**, que não dependem de
   nenhuma decisão aberta, exceto A14. As fotos de 1991–2002 entram quando A15 for decidida.
3. **Antes de gerar qualquer rótulo ideológico:** decidir A7 (crosswalk) e A17. Posso preparar a
   análise do crosswalk com os 38 pares já levantados, para você decidir com números na mão.
4. **Licença dos dados derivados (A12):** a cláusula não comercial do IPEA e a falta de licença do
   Cebrap limitam o que pode ir no download público. Ideologia (CC0), TSE (CC-BY) e Câmara (domínio
   público) não têm restrição.
5. **2026:** tratar como provisório até a diplomação; reprocessar depois.

## Decisões necessárias para seguir

Por ordem de impacto na Fase 1: **A14** (o que é eleito), **A15** (fotos de 1991–2002), **A7 e A17**
(rótulos), **A1 e A2** (onda por legislatura) e **A9** (paleta). As demais (A3–A6, A8, A16, A18)
podem esperar as Fases 2 e 3.
