// Barra "esquerda ↔ direita" com a posição de um partido ou presidente (decisão do Antônio,
// 2026-10-24: opção B). A barra muda com a fonte, para a quebra de escala continuar visível:
// contínua na BLS (−1 a +1, sem faixas) e dividida nas sete faixas dos autores em Bolognesi et al.
// (0 a 10). O número e a fonte vêm sempre embaixo.

import type { Pontuacao } from './dados';
import { esc, formatarNumero } from './formato';

/** Larguras das faixas de Bolognesi et al. na escala de 0 a 10 (cortes dos autores). */
const LARGURAS_FAIXAS = [1.5, 1.5, 1.5, 1, 1.5, 1.5, 1.5];

type Posicao = Pick<Pontuacao, 'pontuacao' | 'fonte_id' | 'ano_medicao'> & {
  faixa?: string | null;
};

function fracao(p: Posicao): number {
  const t = p.fonte_id === 'bls' ? (p.pontuacao + 1) / 2 : p.pontuacao / 10;
  return Math.max(0, Math.min(1, t));
}

function trilho(p: Posicao): string {
  if (p.fonte_id === 'bls') return '<span class="trilho trilho-continuo"></span>';
  const faixas = LARGURAS_FAIXAS.map(
    (w, i) => `<span style="flex:${w};background:var(--faixa-${i + 1})"></span>`,
  ).join('');
  return `<span class="trilho trilho-faixas">${faixas}</span>`;
}

/** Fonte e número: "BLS 2005 · 0,67 de −1 a +1" ou "Bolognesi et al. 2022 · 6,94 de 0 a 10". */
export function legendaPosicao(p: Posicao): string {
  return p.fonte_id === 'bls'
    ? `BLS ${p.ano_medicao} · ${formatarNumero(p.pontuacao, 2)} de −1 a +1`
    : `Bolognesi et al. ${p.ano_medicao} · ${formatarNumero(p.pontuacao, 2)} de 0 a 10`;
}

/** Barra com marcador. `compacta`: só a barra, para tabelas (o número vai no título). */
export function barraPosicao(
  p: Posicao | undefined,
  opcoes: { compacta?: boolean; nota?: string } = {},
): string {
  if (!p) return '<span class="posicao-celula">não classificado (sem medição na fonte)</span>';
  const titulo = `${p.faixa ? `${p.faixa} · ` : ''}${legendaPosicao(p)}`;
  const barra = `<span class="barra-posicao${opcoes.compacta ? ' compacta' : ''}" role="img" aria-label="${esc(titulo)}" title="${esc(titulo)}">${trilho(p)}<span class="marca-posicao" style="left:${(fracao(p) * 100).toFixed(1)}%"></span></span>`;
  if (opcoes.compacta) return barra;
  return `<span class="bloco-posicao">${barra}<span class="pontas-posicao"><span>esquerda</span><span>direita</span></span><span class="legenda-posicao">${esc(legendaPosicao(p))}${p.fonte_id === 'bls' ? ' · sem faixas na fonte' : ''}${opcoes.nota ? ` · ${esc(opcoes.nota)}` : ''}</span></span>`;
}

/** Célula de tabela: barra compacta e, ao lado, a faixa (Bolognesi) ou o número (BLS). */
export function celulaPosicao(p: Posicao | undefined): string {
  if (!p) return barraPosicao(undefined);
  const texto = p.faixa ?? formatarNumero(p.pontuacao, 2);
  return `${barraPosicao(p, { compacta: true })}<span class="posicao-celula">${esc(texto)}</span>`;
}
