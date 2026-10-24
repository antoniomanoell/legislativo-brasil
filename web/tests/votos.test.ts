import { expect, it } from 'vitest';
import type { VotacoesDoAno } from '../src/dados';
import { decodificar, placarPorPartido } from '../src/votos';

const ano: VotacoesDoAno = {
  deputados: [
    [10, 'Ana', 'SP'],
    [20, 'Beto', 'RJ'],
    [30, 'Caio', 'MG'],
    [40, 'Dora', 'BA'],
  ],
  partidos: ['pmdb', 'psdb', 'pt'],
  votacoes: [],
};

it('decodifica voto e partido no momento do voto, sem os ausentes', () => {
  const v = {
    id: 'x',
    data: '2016-10-10',
    descricao: '',
    proposicoes: [],
    aprovada: true,
    orientacao_governo: 'Sim',
    placar: [1, 2, 0, 0] as [number, number, number, number],
    pec: false,
    v: 'SN.N',
    p: '21.2',
  };
  const votos = decodificar(ano, v);
  expect(votos.map((x) => [x.nome, x.partido, x.voto])).toEqual([
    ['Ana', 'pt', 'Sim'],
    ['Beto', 'psdb', 'Não'],
    ['Dora', 'pt', 'Não'],
  ]);
  const placar = placarPorPartido(votos);
  expect(placar.get('pt')).toEqual({ contagem: [1, 1, 0, 0, 0], rice: 0 });
  expect(placar.get('psdb')?.rice).toBe(1);
});
