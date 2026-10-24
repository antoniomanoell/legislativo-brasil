import { describe, expect, it } from 'vitest';
import { ladoDaPosicao, montarPaineis } from '../src/charts/espectro-governismo';
import type { Catalogo, Governo, Indicadores, Ideologia, Pontuacao } from '../src/dados';

const bls = (v: number): Pontuacao => ({
  pontuacao: v,
  erro_padrao: null,
  n: null,
  faixa: null,
  fonte_id: 'bls',
  ano_medicao: 2005,
  sigla_fonte: 'X',
  escala: '-1 a 1',
  nota: null,
});

describe('ladoDaPosicao', () => {
  it('BLS pelo sinal; Bolognesi pela faixa, sem o centro', () => {
    expect(ladoDaPosicao(bls(-0.5))).toBe('esquerda');
    expect(ladoDaPosicao(bls(0.1))).toBe('direita');
    expect(ladoDaPosicao({ ...bls(5), fonte_id: 'bolognesi', faixa: 'centro' })).toBeNull();
    expect(ladoDaPosicao({ ...bls(6.9), fonte_id: 'bolognesi', faixa: 'centro-direita' })).toBe(
      'direita',
    );
  });
});

describe('montarPaineis', () => {
  it('pondera o governismo pelas cadeiras e usa a posição do presidente', () => {
    const governo = {
      governo_id: 'lula1',
      presidente: 'Lula',
      inicio: '2003-01-01',
      fim: '2006-12-31',
      posicao_presidente: {
        pontuacao: -0.42,
        erro_padrao: 0.04,
        ano_medicao: 2013,
        relacao: 'depois',
      },
    } as Governo;
    const catalogo = {
      momentos: [{ id: '2003-02-01', tipo: 'exercicio', data: '2003-02-01', legislatura: 52 }],
    } as unknown as Catalogo;
    const ind = {
      partidos: {
        pt: { governos: { lula1: { governismo: 0.9 } } },
        pfl: { governos: { lula1: { governismo: 0.4 } } },
        pmdb: { governos: { lula1: { governismo: 0.8 } } },
      },
    } as unknown as Indicadores;
    const ideologia: Ideologia = { '52': { pt: bls(-0.5), pfl: bls(0.7), pmdb: bls(0.1) } };
    const [p] = montarPaineis(
      [governo],
      ind,
      ideologia,
      catalogo,
      { '2003-02-01': { pt: 90, pfl: 75, pmdb: 75 } },
      (x) => x,
    );
    expect(p?.ladoDoGoverno).toBe('esquerda');
    expect(p?.lados.esquerda).toEqual({ cadeiras: 90, governismo: 0.9 });
    expect(p?.lados.direita.cadeiras).toBe(150);
    expect(p?.lados.direita.governismo).toBeCloseTo(0.6);
  });
});
