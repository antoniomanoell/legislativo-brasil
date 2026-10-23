import { describe, expect, it } from 'vitest';
import type { Partido } from '../src/dados';
import { partidoFinal, somarPorLinhagem } from '../src/linhagem';

const p = (destino?: string): Partido => ({
  sigla: '',
  nome: '',
  observacao: null,
  renomeacoes: [],
  origem: [],
  destino: destino ? [{ partido: destino, tipo: 'fusão', data: '', confirmado_no_tse: 'sim' }] : [],
});

const partidos = {
  pfl: p('uniao'),
  psl: p('uniao'),
  uniao: p(),
  pds: p('ppr'),
  ppr: p('ppb'),
  ppb: p(),
  pt: p(),
};

describe('linhagem', () => {
  it('segue fusões até o partido final', () => {
    expect(partidoFinal('pds', partidos)).toBe('ppb');
    expect(partidoFinal('pt', partidos)).toBe('pt');
    expect(partidoFinal('desconhecido', partidos)).toBe('desconhecido');
  });

  it('soma as cadeiras pela linhagem', () => {
    expect(somarPorLinhagem({ pfl: 43, psl: 1, pt: 86 }, partidos)).toEqual({ uniao: 44, pt: 86 });
  });
});
