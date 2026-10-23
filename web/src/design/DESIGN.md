# DESIGN.md — identidade visual

Origem: **antoniomanoell/mapa-brasil** (Indicadores BR), commit `ce627fa` de 2026-10-23
("Celular: título do mapa com o nome curto do recorte"). PROJECT.md, seção 9.

## O que foi importado

| Arquivo aqui                                                              | Origem no mapa            | Como                                              |
| ------------------------------------------------------------------------- | ------------------------- | ------------------------------------------------- |
| `mapa.css`                                                                | `web/src/style.css`       | cópia sem alterações (só o cabeçalho de origem)   |
| `tema.ts`                                                                 | `web/src/tema.ts`         | cópia sem alterações                              |
| `ajuda.ts`                                                                | `web/src/ajuda.ts`        | cópia sem alterações                              |
| `../../public/favicon.svg`                                                | `web/public/favicon.svg`  | cópia provisória, até haver nome e ícone próprios |
| `../../.prettierrc.json`, `../../eslint.config.js`, `../../tsconfig.json` | mesmos caminhos em `web/` | cópia                                             |

**Regra:** `mapa.css`, `tema.ts` e `ajuda.ts` não são editados aqui. Mudança no visual comum vai no
mapa e é copiada de novo, com o commit novo anotado nesta tabela. Isso mantém os dois sites iguais e
a fusão futura simples (D11). O que é só deste site fica em `congresso.css` e `paletas.ts`.

## Inventário do visual do mapa

- **Tokens** (variáveis CSS em `:root`): fundos (`--fundo-pagina`, `--fundo`, `--fundo-2`,
  `--fundo-3`, `--chip`), texto (`--texto`, `--texto-2`), bordas, acento (`--acento`,
  `--acento-forte`, `--acento-suave`), seleção, barra, aviso, sombras (`--sombra-1`, `--sombra-2`),
  séries de gráfico, hachura de "sem dado", foco (`--foco`) e raio (`--raio: 14px`).
- **Tema escuro:** segue o sistema; o botão grava a escolha em `localStorage` (`data-tema` no
  `<html>`). Um script no `<head>` aplica a escolha antes da primeira pintura.
- **Tipografia:** `system-ui` (sem fonte web), corpo 1rem/1,45; páginas de texto 1,0625rem/1,65;
  títulos com `letter-spacing` negativo; números com `tabular-nums`.
- **Breakpoints:** 480, 600, 800, 960 e 1400 px; mobile-first.
- **Componentes:** cabeçalho (`.topo`, `.marca`, nav, `.botao-icone` do tema), seletores
  (`.campo`), controles segmentados (`.visao`), painéis (`.bloco`), cartões-resumo (`.cartao`),
  linha do tempo (`.slider`, `.play`), legenda (`.legenda`, `.amostra`), dica flutuante (`.dica`),
  tabela/ranking (`.ranking`, `.barra-trilho`), painel de detalhes (folha inferior no celular, gaveta
  lateral a partir de 960 px: `.painel`), ajuda "?" em popover nativo (`.ajuda`, `.ajuda-pop`),
  aviso de rascunho (`.aviso-rascunho`), selo (`.selo`), erro (`.erro`), páginas de texto (`.texto`).
- **Padrões de interação:** passar o mouse ou tocar mostra a dica; clicar abre o painel de
  detalhes; toda visualização tem alternativa em tabela; "sem dado" é hachura, nunca cor; fonte e
  notas ficam abaixo da visualização e na ficha técnica gerada a partir dos dados.

## Específico deste site (`congresso.css`, `paletas.ts`)

- Hemiciclo (`.hemiciclo`, `.cadeira`), nota de posição representativa e bloco de não classificados.
- Paletas candidatas das sete faixas ideológicas: aguardam escolha do Antônio (PENDENCIAS.md, A9).
  "Não classificado" usa a hachura do mapa, não uma cor.

## Amostra

`web/estilo.html` (rodar `npm run dev` em `web/` e abrir `/estilo.html`).
