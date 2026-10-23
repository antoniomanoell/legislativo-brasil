import { expect, it } from 'vitest';
import type { Partido } from '../src/dados';
import { siglaEm } from '../src/siglas';

const prb: Partido = {
  sigla: 'REPUBLICANOS',
  nome: 'Republicanos',
  observacao: null,
  renomeacoes: [
    { sigla_anterior: 'PRB', sigla_nova: 'REPUBLICANOS', data: '2019-08-15' },
    { sigla_anterior: 'PMR', sigla_nova: 'PRB', data: '2009-09-21' },
  ],
  origem: [],
  destino: [],
};

it('usa a sigla vigente na data', () => {
  const partidos = { prb };
  expect(siglaEm('prb', '2007-06', partidos)).toBe('PMR');
  expect(siglaEm('prb', '2010-02-01', partidos)).toBe('PRB');
  expect(siglaEm('prb', '2022-02-01', partidos)).toBe('REPUBLICANOS');
  expect(siglaEm('xyz', '2022-02-01', partidos)).toBe('xyz');
});
