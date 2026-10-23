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
- **Fonte:** Emenda Constitucional nº 111, de 28/09/2021 [confirmar texto no Planalto e registrar em SOURCES.md].

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
