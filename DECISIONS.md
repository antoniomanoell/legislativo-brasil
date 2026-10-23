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

## 2026-10-23 — CI sem testes de navegador na Fase 0
- **Decisão:** o CI roda lint, formatação, tipos, testes unitários e build (pipeline e web). Os testes
  de fumaça com Playwright, como no mapa, entram na Fase 1, quando houver páginas de verdade.
- **Motivo:** hoje só existe a página de amostra; instalar navegador no CI não testaria nada útil.
