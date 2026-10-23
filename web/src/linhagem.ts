// "Seguir linhagem" (PROJECT.md, 7.3): soma cada partido ao partido em que ele terminou, seguindo
// fusões e incorporações (data/manual/linhagens.csv). Renomeações já são o mesmo partido.

import type { Partido } from './dados';

/** Partido final da linhagem de `id` (ele mesmo, se não foi fundido nem incorporado). */
export function partidoFinal(id: string, partidos: Record<string, Partido>): string {
  let atual = id;
  const vistos = new Set<string>();
  for (;;) {
    const destino = partidos[atual]?.destino[0]?.partido;
    if (!destino || vistos.has(destino)) return atual;
    vistos.add(atual);
    atual = destino;
  }
}

/** Soma as cadeiras de cada momento pelo partido final da linhagem. */
export function somarPorLinhagem(
  cadeiras: Record<string, number>,
  partidos: Record<string, Partido>,
): Record<string, number> {
  const soma: Record<string, number> = {};
  for (const [id, n] of Object.entries(cadeiras)) {
    const final = partidoFinal(id, partidos);
    soma[final] = (soma[final] ?? 0) + n;
  }
  return soma;
}
