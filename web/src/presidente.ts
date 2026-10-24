// Presidente numa data e a posição dele na escala da BLS (Zucco & Power), com a ressalva de quando a
// avaliação foi feita (DECISIONS 2026-10-24: durante o mandato; senão, a primeira posterior; senão,
// a mais recente anterior).

import type { Governo } from './dados';
import { esc, formatarNumero } from './formato';

export function governoEm(governos: Governo[], dia: string): Governo | undefined {
  return governos.find((g) => g.inicio <= dia && dia <= g.fim);
}

const RELACAO = {
  durante: 'avaliação feita durante o mandato',
  depois: 'avaliação feita depois do mandato',
  antes: 'avaliação feita antes deste mandato',
} as const;

/** "0,18 na escala da BLS, de −1 (esquerda) a +1 (direita) — avaliação feita depois do mandato,
 * em 2013". */
export function posicaoDoPresidente(g: Governo): string {
  const p = g.posicao_presidente;
  if (!p) return 'sem avaliação na fonte';
  return `<strong>${formatarNumero(p.pontuacao, 2)}</strong> na escala da BLS, de −1 (esquerda) a +1 (direita) — ${RELACAO[p.relacao]}, em ${p.ano_medicao}`;
}

/** Nome, partido e posição do presidente. */
export function descreverPresidente(g: Governo): string {
  return `${esc(g.presidente)} (${esc(g.partido_presidente)}) · posição: ${posicaoDoPresidente(g)}`;
}
