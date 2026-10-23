// Desenho do hemiciclo em SVG (geometria em hemiciclo.ts). Cor = posição ideológica do partido;
// a identidade do partido vem dos separadores e das siglas, não da cor (PROJECT.md, 9).
// Teclado: o hemiciclo é um só ponto de tabulação; setas andam entre cadeiras, Home/End vão às
// pontas, Esc limpa a seleção. Cada movimento é anunciado numa região viva para leitores de tela.

import type { Composicao } from '../composicao';
import { emOrdem } from '../composicao';
import type { Deputado } from '../dados';
import { corDe, descrever } from '../ideologia';
import { hemiciclo } from './hemiciclo';

const SVG = 'http://www.w3.org/2000/svg';
/** Partidos com pelo menos esta fração das cadeiras ganham sigla escrita junto ao arco. */
const FRACAO_ROTULO = 0.025;

export interface Selecao {
  deputado: Deputado;
  descricao: string;
}

function el<K extends keyof SVGElementTagNameMap>(
  tag: K,
  attrs: Record<string, string | number>,
): SVGElementTagNameMap[K] {
  const e = document.createElementNS(SVG, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, String(v));
  return e;
}

export function desenharHemiciclo(
  alvo: HTMLElement,
  composicao: Composicao,
  cores: string[],
  aoMudar: (s: Selecao | undefined, origem: 'teclado' | 'ponteiro') => void,
): void {
  const ordem = emOrdem(composicao);
  const cadeiras = hemiciclo(ordem.length);
  const svg = el('svg', {
    viewBox: '-1.22 -1.2 2.44 1.26',
    class: 'hemiciclo',
    tabindex: 0,
    role: 'group',
    'aria-roledescription': 'hemiciclo',
    'aria-label': `Hemiciclo com ${ordem.length} cadeiras de partidos classificados, da esquerda para a direita. Use as setas para percorrer as cadeiras.`,
  });

  // Separadores entre partidos: uma linha radial no ângulo médio entre o último deputado de um
  // partido e o primeiro do seguinte.
  const separadores = el('g', { class: 'separadores' });
  const rotulos = el('g', { class: 'rotulos-hemiciclo', 'aria-hidden': 'true' });
  let inicio = 0;
  composicao.classificados.forEach((grupo, gi) => {
    const fim = inicio + grupo.deputados.length;
    const primeiro = cadeiras[inicio];
    const ultimo = cadeiras[fim - 1];
    if (gi > 0 && primeiro) {
      const anterior = cadeiras[inicio - 1];
      const ang = anterior ? (anterior.angulo + primeiro.angulo) / 2 : primeiro.angulo;
      separadores.append(
        el('line', {
          x1: 0.33 * Math.cos(ang),
          y1: -0.33 * Math.sin(ang),
          x2: 1.05 * Math.cos(ang),
          y2: -1.05 * Math.sin(ang),
        }),
      );
    }
    if (primeiro && ultimo && grupo.deputados.length / ordem.length >= FRACAO_ROTULO) {
      const ang = (primeiro.angulo + ultimo.angulo) / 2;
      const x = 1.11 * Math.cos(ang);
      const texto = el('text', {
        x,
        y: -1.11 * Math.sin(ang),
        'text-anchor': Math.abs(x) < 0.25 ? 'middle' : x < 0 ? 'end' : 'start',
        'dominant-baseline': 'middle',
      });
      texto.textContent = grupo.sigla;
      rotulos.append(texto);
    }
    inicio = fim;
  });

  const circulos = cadeiras.map((c, i) => {
    const item = ordem[i] as (typeof ordem)[number];
    const circ = el('circle', {
      cx: c.x,
      cy: -c.y,
      r: c.r,
      class: 'cadeira',
      fill: corDe(item.grupo.pontuacao, cores),
      'data-i': i,
    });
    svg.append(circ);
    return circ;
  });
  svg.append(separadores, rotulos);

  let atual = -1;
  const selecionar = (i: number, origem: 'teclado' | 'ponteiro') => {
    circulos[atual]?.classList.remove('ativa');
    atual = i;
    const item = ordem[i];
    if (!item) return aoMudar(undefined, origem);
    circulos[i]?.classList.add('ativa');
    aoMudar({ deputado: item.deputado, descricao: descrever(item.grupo.pontuacao) }, origem);
  };

  svg.addEventListener('pointerover', (e) => {
    const i = (e.target as Element).getAttribute('data-i');
    if (i !== null) selecionar(Number(i), 'ponteiro');
  });
  svg.addEventListener('click', (e) => {
    const i = (e.target as Element).getAttribute('data-i');
    if (i !== null) selecionar(Number(i), 'ponteiro');
  });
  svg.addEventListener('keydown', (e) => {
    const ultimo = ordem.length - 1;
    const passos: Record<string, number> = {
      ArrowRight: atual + 1,
      ArrowDown: atual + 1,
      ArrowLeft: atual - 1,
      ArrowUp: atual - 1,
      Home: 0,
      End: ultimo,
    };
    if (e.key === 'Escape') return selecionar(-1, 'teclado');
    const destino = passos[e.key];
    if (destino === undefined) return;
    e.preventDefault();
    selecionar(Math.max(0, Math.min(ultimo, atual < 0 ? 0 : destino)), 'teclado');
  });

  alvo.replaceChildren(svg);
}
