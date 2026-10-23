import { describe, expect, it } from 'vitest';
import { compor, emOrdem } from '../src/composicao';
import type { Deputado, Pontuacao } from '../src/dados';
import { corContinua, descrever, linhaDeFonte } from '../src/ideologia';

const dep = (nome: string, partido: string, sigla = partido.toUpperCase()): Deputado => ({
  nome,
  uf: 'SP',
  partido,
  sigla,
});

const ponto = (pontuacao: number, faixa: string | null = null): Pontuacao => ({
  pontuacao,
  erro_padrao: null,
  n: null,
  faixa,
  fonte_id: faixa ? 'bolognesi' : 'bls',
  ano_medicao: faixa ? 2022 : 2021,
  sigla_fonte: 'X',
  escala: '',
  nota: null,
});

describe('compor', () => {
  const deputados = [
    dep('Zé', 'pt'),
    dep('Ana', 'pt'),
    dep('Bia', 'pl'),
    dep('Caio', 'prd'),
    dep('Dora', 'psol'),
  ];
  const pontos = { pt: ponto(-0.69), pl: ponto(0.49), psol: ponto(-0.87) };

  it('ordena partidos da esquerda para a direita e deputados por nome', () => {
    const c = compor(deputados, pontos);
    expect(c.classificados.map((g) => g.partido)).toEqual(['psol', 'pt', 'pl']);
    expect(emOrdem(c).map((x) => x.deputado.nome)).toEqual(['Dora', 'Ana', 'Zé', 'Bia']);
  });

  it('deixa quem não tem pontuação fora da ordenação', () => {
    const c = compor(deputados, pontos);
    expect(c.naoClassificados.map((g) => g.partido)).toEqual(['prd']);
    expect(emOrdem(c)).toHaveLength(4);
  });
});

describe('ideologia', () => {
  it('a cor contínua usa as pontas e o centro da paleta', () => {
    const cores = ['#000000', '#111111', '#222222', '#808080', '#aaaaaa', '#cccccc', '#ffffff'];
    expect(corContinua(-1, cores)).toBe('#000000');
    expect(corContinua(0, cores)).toBe('#808080');
    expect(corContinua(1, cores)).toBe('#ffffff');
    expect(corContinua(5, cores)).toBe('#ffffff');
  });

  it('descreve sem repetir a fonte, e sem rótulo na BLS', () => {
    expect(descrever(ponto(6.2, 'centro-direita'))).toBe('centro-direita (6,2)');
    expect(descrever(ponto(-0.69))).toBe('-0,69');
    expect(descrever(undefined)).toMatch(/^não classificado/);
  });

  it('a fonte aparece numa linha própria', () => {
    expect(linhaDeFonte([ponto(6.2, 'centro-direita')])).toBe(
      'Posição ideológica: Bolognesi et al., 2022 (escala 0 a 10, faixas dos autores).',
    );
  });
});
