// Cor, rótulo e texto de fonte da posição ideológica (PROJECT.md, 7.4; DECISIONS A7, A9, A17).
// - Bolognesi (57ª e 58ª): cor da faixa publicada.
// - BLS (49ª a 56ª): sem faixa; cor contínua pela pontuação (−1 a +1), com os mesmos dois matizes.
// - Sem pontuação: "não classificado", em hachura, fora da ordenação.

import type { Pontuacao } from './dados';
import { formatarNumero } from './formato';

export const FAIXAS = [
  'extrema-esquerda',
  'esquerda',
  'centro-esquerda',
  'centro',
  'centro-direita',
  'direita',
  'extrema-direita',
] as const;

export const HACHURA_SVG = 'url(#hachura)';

/** Tons das faixas no tema atual, lidos das variáveis do CSS (congresso.css). */
export function coresDasFaixas(): string[] {
  const estilo = getComputedStyle(document.documentElement);
  return FAIXAS.map((_, i) => estilo.getPropertyValue(`--faixa-${i + 1}`).trim());
}

function rgb(hex: string): [number, number, number] {
  const h = hex.replace('#', '');
  return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16)) as [number, number, number];
}

function hex([r, g, b]: number[]): string {
  return `#${[r, g, b]
    .map((v) =>
      Math.round(v ?? 0)
        .toString(16)
        .padStart(2, '0'),
    )
    .join('')}`;
}

/** Cor contínua da BLS: −1 e +1 nas pontas da paleta, 0 no centro, interpolação entre os tons. */
export function corContinua(valor: number, cores: string[]): string {
  const t = ((Math.max(-1, Math.min(1, valor)) + 1) / 2) * (cores.length - 1);
  const i = Math.min(Math.floor(t), cores.length - 2);
  const f = t - i;
  const a = rgb(cores[i] as string);
  const b = rgb(cores[i + 1] as string);
  return hex(a.map((v, k) => v + ((b[k] as number) - v) * f));
}

/** Cor da cadeira de um partido numa legislatura. */
export function corDe(p: Pontuacao | undefined, cores: string[]): string {
  if (!p) return HACHURA_SVG;
  if (p.faixa) return cores[FAIXAS.indexOf(p.faixa as (typeof FAIXAS)[number])] ?? HACHURA_SVG;
  return corContinua(p.pontuacao, cores);
}

export function nomeFonte(p: Pontuacao): string {
  return p.fonte_id === 'bls'
    ? `Zucco & Power, BLS ${p.ano_medicao}`
    : `Bolognesi et al., ${p.ano_medicao}`;
}

/** "centro-direita (6,2) — fonte: Bolognesi et al., 2022" (PROJECT.md, 1.1). */
export function descrever(p: Pontuacao | undefined): string {
  if (!p) return 'não classificado (sem medição na fonte para esta legislatura)';
  const casas = p.fonte_id === 'bls' ? 2 : 1;
  const valor = formatarNumero(p.pontuacao, casas);
  const escala = p.fonte_id === 'bls' ? 'escala −1 a +1' : 'escala 0 a 10';
  const posicao = p.faixa ? `${p.faixa} (${valor})` : `${valor} na ${escala}, sem rótulo de faixa`;
  return `${posicao} — fonte: ${nomeFonte(p)}`;
}
