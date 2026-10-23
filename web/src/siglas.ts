// Sigla de um partido numa data, a partir das renomeações registradas no TSE (partidos.json).
// Evita anacronismo: o PRB de 2010 não aparece como "REPUBLICANOS", nem o PR de 2013 como "PL".

import type { Partido } from './dados';

/** `data` em AAAA-MM ou AAAA-MM-DD. */
export function siglaEm(id: string, data: string, partidos: Record<string, Partido>): string {
  const p = partidos[id];
  if (!p) return id;
  const posteriores = p.renomeacoes
    .filter((r) => r.data > data)
    .sort((a, b) => a.data.localeCompare(b.data));
  return posteriores[0]?.sigla_anterior ?? p.sigla;
}
