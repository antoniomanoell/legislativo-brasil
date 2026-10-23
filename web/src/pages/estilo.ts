// Página interna de amostra (Fase 0): componentes do mapa e paletas candidatas das faixas.

import '../design/mapa.css';
import '../design/congresso.css';
import { hemiciclo } from '../charts/hemiciclo';
import { ajuda } from '../design/ajuda';
import { FAIXAS, PALETAS, type Paleta } from '../design/paletas';
import { iniciarTema, temaAtual } from '../design/tema';

const SVG = 'http://www.w3.org/2000/svg';

// Distribuição fictícia por faixa (soma 513 com os não classificados), só para avaliar cor.
const FICTICIO = [14, 78, 52, 66, 104, 118, 61];
const NAO_CLASSIFICADOS = 20;

const TOKENS = [
  '--fundo-pagina',
  '--fundo',
  '--fundo-2',
  '--fundo-3',
  '--texto',
  '--texto-2',
  '--borda',
  '--borda-forte',
  '--acento',
  '--acento-forte',
  '--selecao',
  '--barra',
  '--aviso-fundo',
  '--aviso-borda',
  '--foco',
  '--hachura-fundo',
  '--hachura-linha',
];

function amostra(fundo: string): HTMLSpanElement {
  const s = document.createElement('span');
  s.className = 'amostra';
  s.style.background = fundo;
  s.setAttribute('aria-hidden', 'true');
  return s;
}

function desenharTokens(): void {
  const el = document.querySelector('#tokens') as HTMLElement;
  el.replaceChildren(
    ...TOKENS.map((t) => {
      const d = document.createElement('div');
      d.className = 'token';
      const c = document.createElement('code');
      c.textContent = t;
      d.append(amostra(`var(${t})`), c);
      return d;
    }),
  );
}

function svgHemiciclo(cores: readonly string[]): SVGSVGElement {
  const cadeiras = hemiciclo(FICTICIO.reduce((a, b) => a + b, 0));
  // Cada faixa ocupa uma fatia contínua, na ordem das cadeiras (esquerda → direita).
  const faixaDa: number[] = FICTICIO.flatMap((n, i) => Array<number>(n).fill(i));
  const svg = document.createElementNS(SVG, 'svg');
  svg.setAttribute('viewBox', '-1.04 -1.04 2.08 1.08');
  svg.setAttribute('class', 'hemiciclo');
  svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', 'Hemiciclo com dados fictícios, colorido pela paleta');
  cadeiras.forEach((c, i) => {
    const f = faixaDa[i] as number;
    const circ = document.createElementNS(SVG, 'circle');
    circ.setAttribute('cx', String(c.x));
    circ.setAttribute('cy', String(-c.y));
    circ.setAttribute('r', String(c.r));
    circ.setAttribute('fill', cores[f] as string);
    circ.setAttribute('class', 'cadeira');
    circ.setAttribute('vector-effect', 'non-scaling-stroke');
    const titulo = document.createElementNS(SVG, 'title');
    titulo.textContent = FAIXAS[f] as string;
    circ.append(titulo);
    svg.append(circ);
  });
  return svg;
}

function cartaoPaleta(p: Paleta): HTMLElement {
  const cores = temaAtual() === 'escuro' ? p.escuro : p.claro;
  const art = document.createElement('article');
  art.innerHTML = `<h3 class="bloco-titulo">${p.id} · ${p.nome}</h3>`;
  art.append(svgHemiciclo(cores));
  const nota = document.createElement('p');
  nota.className = 'nota-hemiciclo';
  nota.textContent =
    'A posição das cadeiras é representativa; não corresponde ao assento real no plenário.';
  const fora = document.createElement('div');
  fora.className = 'nao-classificados';
  fora.append(
    amostra('var(--hachura-fundo)'),
    `Não classificados: ${NAO_CLASSIFICADOS} (fora da ordenação)`,
  );
  (fora.firstElementChild as HTMLElement).style.background =
    'repeating-linear-gradient(-45deg, var(--hachura-fundo) 0 3px, var(--hachura-linha) 3px 4px)';
  const legenda = document.createElement('div');
  legenda.className = 'legenda';
  const ul = document.createElement('ul');
  FAIXAS.forEach((f, i) => {
    const li = document.createElement('li');
    li.append(amostra(cores[i] as string), f);
    ul.append(li);
  });
  legenda.append(ul);
  const val = document.createElement('p');
  val.className = 'paleta-validacao';
  val.textContent = p.validacao;
  art.append(nota, fora, legenda, val);
  return art;
}

function desenharPaletas(): void {
  (document.querySelector('#paletas-lista') as HTMLElement).replaceChildren(
    ...PALETAS.map(cartaoPaleta),
  );
}

function ligarSlider(): void {
  const range = document.querySelector('#slider-demo') as HTMLInputElement;
  const rotulo = document.querySelector('#slider-rotulo') as HTMLElement;
  const pintar = () => {
    const ini = Number(range.min);
    const pct = ((Number(range.value) - ini) / (Number(range.max) - ini)) * 100;
    range.style.setProperty('--progresso', `${pct}%`);
    rotulo.textContent = `1º/fev/${range.value} · em exercício`;
  };
  range.addEventListener('input', pintar);
  pintar();
}

(document.querySelector('#ajuda-demo') as HTMLElement).innerHTML = ajuda(
  'ajuda-exemplo',
  'Como ler',
  'Explicação curta num popover nativo, como no mapa.',
);
desenharTokens();
desenharPaletas();
ligarSlider();
iniciarTema(desenharPaletas);
