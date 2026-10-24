// Quem acompanha cada governo, pelo espectro (página Governos; DECISIONS 2026-10-24): governismo de
// cada partido no governo, na posição ideológica da legislatura daquele governo (BLS até 2023,
// Bolognesi et al. depois, sem converter uma escala na outra), e o resumo por lado da escala.
//
// Lado da escala: na BLS, abaixo ou acima do ponto médio (0), porque a fonte não publica faixas; em
// Bolognesi et al., pelas faixas dos autores (o centro fica de fora). O lado do governo é o da posição
// do próprio presidente na BLS.

import type { Agregados, Catalogo, Governo, Indicadores, Pontuacao, Ideologia } from '../dados';
import { esc, formatarNumero } from '../formato';
import { corDe } from '../ideologia';

export type Lado = 'esquerda' | 'direita';

export interface PontoPartido {
  partido: string;
  sigla: string;
  cadeiras: number;
  governismo: number;
  pontuacao: Pontuacao;
}

export interface PainelGoverno {
  governo: Governo;
  legislatura: number;
  data: string;
  pontos: PontoPartido[];
  /** Governismo médio ponderado pelas cadeiras, por lado da escala (null se o lado não tem partido). */
  lados: Record<Lado, { cadeiras: number; governismo: number | null }>;
  ladoDoGoverno: Lado | null;
}

const FAIXAS_ESQUERDA = new Set(['extrema-esquerda', 'esquerda', 'centro-esquerda']);

export function ladoDaPosicao(p: Pontuacao): Lado | null {
  if (p.fonte_id === 'bls')
    return p.pontuacao < 0 ? 'esquerda' : p.pontuacao > 0 ? 'direita' : null;
  if (!p.faixa || p.faixa === 'centro') return null;
  return FAIXAS_ESQUERDA.has(p.faixa) ? 'esquerda' : 'direita';
}

/** Um painel por governo com governismo: a foto de 1º/fev do primeiro ano do mandato dá as cadeiras
 * e a legislatura (que define a fonte da posição ideológica). */
export function montarPaineis(
  governos: Governo[],
  indicadores: Indicadores,
  ideologia: Ideologia,
  catalogo: Catalogo,
  agregados: Agregados,
  sigla: (partido: string, data: string) => string,
): PainelGoverno[] {
  const fotos = catalogo.momentos.filter((m) => m.tipo === 'exercicio' && m.data);
  const paineis: PainelGoverno[] = [];
  for (const g of governos) {
    const foto = fotos.find((m) => (m.data as string) >= g.inicio && (m.data as string) <= g.fim);
    if (!foto) continue;
    const posicoes = ideologia[String(foto.legislatura)] ?? {};
    const pontos: PontoPartido[] = [];
    for (const [partido, cadeiras] of Object.entries(agregados[foto.id] ?? {})) {
      const governismo = indicadores.partidos[partido]?.governos?.[g.governo_id]?.governismo;
      const pontuacao = posicoes[partido];
      if (governismo == null || !pontuacao) continue;
      pontos.push({
        partido,
        sigla: sigla(partido, foto.data as string),
        cadeiras,
        governismo,
        pontuacao,
      });
    }
    if (!pontos.length) continue;
    const lados = {} as PainelGoverno['lados'];
    for (const lado of ['esquerda', 'direita'] as const) {
      const doLado = pontos.filter((p) => ladoDaPosicao(p.pontuacao) === lado);
      const cadeiras = doLado.reduce((s, p) => s + p.cadeiras, 0);
      lados[lado] = {
        cadeiras,
        governismo: cadeiras
          ? doLado.reduce((s, p) => s + p.governismo * p.cadeiras, 0) / cadeiras
          : null,
      };
    }
    const pres = g.posicao_presidente?.pontuacao;
    paineis.push({
      governo: g,
      legislatura: foto.legislatura,
      data: foto.data as string,
      pontos,
      lados,
      ladoDoGoverno: pres == null ? null : pres < 0 ? 'esquerda' : 'direita',
    });
  }
  return paineis;
}

const pct = (v: number | null) => (v == null ? '—' : `${Math.round(100 * v)}%`);

/** Barras agrupadas: governismo médio do lado esquerdo e do direito, por governo. */
export function svgResumo(paineis: PainelGoverno[], rotulo: (g: Governo) => string): string {
  const largura = 860;
  const altura = 260;
  const m = 46;
  const topo = 24;
  const base = 196;
  const passo = (largura - 2 * m) / Math.max(paineis.length, 1);
  const y = (v: number) => base - v * (base - topo);
  const partes: string[] = [];
  for (const t of [0, 0.5, 1]) {
    partes.push(
      `<line x1="${m}" x2="${largura - m}" y1="${y(t)}" y2="${y(t)}" class="grafico-grade"/><text x="${m - 6}" y="${y(t) + 4}" class="grafico-eixo" text-anchor="end">${t * 100}%</text>`,
    );
  }
  paineis.forEach((p, i) => {
    const largBarra = Math.min(passo * 0.3, 44);
    const x0 = m + i * passo + passo / 2 - largBarra;
    (['esquerda', 'direita'] as const).forEach((lado, j) => {
      const v = p.lados[lado].governismo;
      if (v == null) return;
      const x = x0 + j * largBarra;
      partes.push(
        `<rect x="${x.toFixed(1)}" y="${y(v).toFixed(1)}" width="${(largBarra - 3).toFixed(1)}" height="${(base - y(v)).toFixed(1)}" rx="3" class="barra-lado-${lado}"><title>${esc(rotulo(p.governo))}: partidos do lado ${lado} da escala, ${pct(v)} (${p.lados[lado].cadeiras} cadeiras)</title></rect><text x="${(x + largBarra / 2 - 1.5).toFixed(1)}" y="${(y(v) - 5).toFixed(1)}" class="grafico-valor" text-anchor="middle">${Math.round(100 * v)}</text>`,
      );
    });
    const cx = m + i * passo + passo / 2;
    const ladoGov = p.ladoDoGoverno ? `governo de ${p.ladoDoGoverno}` : '';
    partes.push(
      `<text x="${cx.toFixed(1)}" y="${base + 18}" class="grafico-rotulo" text-anchor="middle">${esc(rotulo(p.governo))}</text><text x="${cx.toFixed(1)}" y="${base + 34}" class="grafico-eixo" text-anchor="middle">${ladoGov}</text>`,
    );
  });
  return `<svg viewBox="0 0 ${largura} ${altura}" class="grafico-espectro" role="img" aria-label="Governismo médio dos partidos de cada lado da escala ideológica, por governo. A tabela abaixo traz os mesmos números.">${partes.join('')}</svg>`;
}

/** Painel de um governo: posição (horizontal, na escala da época) × governismo (vertical). */
export function svgPainel(p: PainelGoverno, cores: string[]): string {
  const largura = 400;
  const altura = 250;
  const m = 38;
  const bls = p.pontos[0]?.pontuacao.fonte_id === 'bls';
  const [lo, hi] = bls ? [-1, 1] : [0, 10];
  const x = (v: number) => m + ((v - lo) / (hi - lo)) * (largura - 2 * m);
  const y = (v: number) => 20 + (1 - v) * (altura - 76);
  const partes: string[] = [];
  for (const t of [0, 0.5, 1]) {
    partes.push(
      `<line x1="${m}" x2="${largura - m}" y1="${y(t)}" y2="${y(t)}" class="grafico-grade"/><text x="${m - 4}" y="${y(t) + 4}" class="grafico-eixo" text-anchor="end">${t * 100}%</text>`,
    );
  }
  partes.push(
    `<line x1="${x((lo + hi) / 2)}" x2="${x((lo + hi) / 2)}" y1="20" y2="${altura - 56}" class="linha-meio"/>`,
  );
  for (const q of [...p.pontos].sort((a, b) => b.cadeiras - a.cadeiras)) {
    const r = Math.sqrt(q.cadeiras) * 1.3;
    const titulo = `${q.sigla}: governismo ${pct(q.governismo)}, ${q.cadeiras} cadeiras, posição ${formatarNumero(q.pontuacao.pontuacao, bls ? 2 : 1)}`;
    partes.push(
      `<circle cx="${x(q.pontuacao.pontuacao).toFixed(1)}" cy="${y(q.governismo).toFixed(1)}" r="${r.toFixed(1)}" fill="${corDe(q.pontuacao, cores)}" class="ponto-partido"><title>${esc(titulo)}</title></circle>`,
    );
    if (q.cadeiras >= 30) {
      partes.push(
        `<text x="${x(q.pontuacao.pontuacao).toFixed(1)}" y="${(y(q.governismo) - r - 3).toFixed(1)}" class="grafico-eixo" text-anchor="middle">${esc(q.sigla)}</text>`,
      );
    }
  }
  const fonte = bls
    ? `BLS ${p.pontos[0]?.pontuacao.ano_medicao} (−1 a +1)`
    : `Bolognesi et al. ${p.pontos[0]?.pontuacao.ano_medicao} (0 a 10)`;
  partes.push(
    `<text x="${m}" y="${altura - 36}" class="grafico-eixo">← esquerda</text><text x="${largura - m}" y="${altura - 36}" class="grafico-eixo" text-anchor="end">direita →</text><text x="${largura / 2}" y="${altura - 16}" class="grafico-eixo" text-anchor="middle">posição do partido · ${esc(fonte)}</text>`,
  );
  return `<svg viewBox="0 0 ${largura} ${altura}" class="grafico-espectro" role="img" aria-label="Partidos pela posição ideológica e pelo governismo">${partes.join('')}</svg>`;
}
