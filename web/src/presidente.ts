// Presidente numa data e a posição dele na escala da BLS (Zucco & Power), com a ressalva de quando a
// avaliação foi feita (DECISIONS 2026-10-24: durante o mandato; senão, a primeira posterior; senão,
// a mais recente anterior).

import type { Governo } from './dados';
import { esc } from './formato';
import { barraPosicao } from './posicao';

export function governoEm(governos: Governo[], dia: string): Governo | undefined {
  return governos.find((g) => g.inicio <= dia && dia <= g.fim);
}

const RELACAO = {
  durante: 'avaliação feita durante o mandato',
  depois: 'avaliação feita depois do mandato',
  antes: 'avaliação feita antes deste mandato',
} as const;

/** Barra esquerda ↔ direita da posição do presidente (BLS), com o ano e a relação com o mandato. */
export function posicaoDoPresidente(g: Governo): string {
  const p = g.posicao_presidente;
  if (!p) return '<span class="posicao-celula">sem avaliação na fonte</span>';
  return barraPosicao(
    { pontuacao: p.pontuacao, fonte_id: 'bls', ano_medicao: p.ano_medicao },
    { nota: RELACAO[p.relacao] },
  );
}

/** Nome e partido do presidente. */
export function descreverPresidente(g: Governo): string {
  return `${esc(g.presidente)} (${esc(g.partido_presidente)})`;
}
