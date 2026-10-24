// Decodifica o formato compacto das votações (pipeline/src/congresso/load/votacoes_site.py).

import type { VotacaoCompleta, VotacoesDoAno } from './dados';

export type Voto = 'Sim' | 'Não' | 'Abstenção' | 'Obstrução' | 'Artigo 17';

export const VOTO: Record<string, Voto> = {
  S: 'Sim',
  N: 'Não',
  A: 'Abstenção',
  O: 'Obstrução',
  '7': 'Artigo 17',
};

export const COR_VOTO: Record<Voto, string> = {
  Sim: 'var(--voto-sim)',
  Não: 'var(--voto-nao)',
  Obstrução: 'var(--voto-obstrucao)',
  Abstenção: 'var(--voto-abstencao)',
  'Artigo 17': 'transparent',
};

export interface VotoDeputado {
  id: number;
  nome: string;
  uf: string;
  partido: string;
  voto: Voto;
}

const BASE36 = '0123456789abcdefghijklmnopqrstuvwxyz';

/** Quem votou nesta votação, com o voto e o partido no momento do voto. */
export function decodificar(ano: VotacoesDoAno, v: VotacaoCompleta): VotoDeputado[] {
  const lista: VotoDeputado[] = [];
  for (let i = 0; i < v.v.length; i++) {
    const voto = VOTO[v.v[i] as string];
    if (!voto) continue;
    const [id, nome, uf] = ano.deputados[i] as [number, string, string];
    const partido = ano.partidos[BASE36.indexOf(v.p[i] as string)] ?? '';
    lista.push({ id, nome, uf, partido, voto });
  }
  return lista;
}

/** Placar por partido: [Sim, Não, Abstenção, Obstrução, Artigo 17] e Rice (só Sim e Não). */
export function placarPorPartido(
  votos: VotoDeputado[],
): Map<string, { contagem: number[]; rice: number | null }> {
  const ordem: Voto[] = ['Sim', 'Não', 'Abstenção', 'Obstrução', 'Artigo 17'];
  const mapa = new Map<string, number[]>();
  for (const x of votos) {
    const c = mapa.get(x.partido) ?? [0, 0, 0, 0, 0];
    c[ordem.indexOf(x.voto)] = (c[ordem.indexOf(x.voto)] ?? 0) + 1;
    mapa.set(x.partido, c);
  }
  const saida = new Map<string, { contagem: number[]; rice: number | null }>();
  for (const [p, c] of mapa) {
    const [s = 0, n = 0] = c;
    saida.set(p, { contagem: c, rice: s + n ? Math.abs(s - n) / (s + n) : null });
  }
  return saida;
}
