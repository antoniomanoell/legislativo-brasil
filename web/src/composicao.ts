// Ordem das cadeiras e resumo por partido de um momento (PROJECT.md, 7.4 "Ordem no hemiciclo").
// Partidos classificados, da esquerda para a direita pela pontuação; dentro do partido, ordem
// alfabética. Não classificados ficam fora da ordenação, num bloco à parte.

import type { Deputado, Pontuacao } from './dados';

export interface GrupoPartido {
  partido: string;
  sigla: string;
  deputados: Deputado[];
  pontuacao?: Pontuacao;
}

export interface Composicao {
  /** Classificados, da esquerda para a direita. */
  classificados: GrupoPartido[];
  /** Sem pontuação na legislatura, por sigla. */
  naoClassificados: GrupoPartido[];
}

const porNome = (a: Deputado, b: Deputado) => a.nome.localeCompare(b.nome, 'pt-BR');

export function compor(deputados: Deputado[], pontos: Record<string, Pontuacao> = {}): Composicao {
  const grupos = new Map<string, GrupoPartido>();
  for (const d of deputados) {
    let g = grupos.get(d.partido);
    if (!g) {
      g = { partido: d.partido, sigla: d.sigla, deputados: [], pontuacao: pontos[d.partido] };
      grupos.set(d.partido, g);
    }
    g.deputados.push(d);
  }
  for (const g of grupos.values()) g.deputados.sort(porNome);
  const todos = [...grupos.values()];
  const porSigla = (a: GrupoPartido, b: GrupoPartido) => a.sigla.localeCompare(b.sigla, 'pt-BR');
  return {
    classificados: todos
      .filter((g) => g.pontuacao)
      .sort(
        (a, b) =>
          (a.pontuacao as Pontuacao).pontuacao - (b.pontuacao as Pontuacao).pontuacao ||
          porSigla(a, b),
      ),
    naoClassificados: todos.filter((g) => !g.pontuacao).sort(porSigla),
  };
}

/** Cadeiras na ordem do hemiciclo (só classificados), com o grupo de cada uma. */
export function emOrdem(c: Composicao): { deputado: Deputado; grupo: GrupoPartido }[] {
  return c.classificados.flatMap((grupo) =>
    grupo.deputados.map((deputado) => ({ deputado, grupo })),
  );
}
