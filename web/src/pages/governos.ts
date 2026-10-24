// Governos (PROJECT.md, 4.1.5), Fase 2: presidentes, gabinetes e partidos com ministério (base
// formal, critério do IPEA) e as cadeiras desses partidos em cada 1º de fevereiro. O comportamento
// de voto (governismo) entra na Fase 3.

import '../design/mapa.css';
import '../design/congresso.css';
import {
  montarPaineis,
  svgPainel,
  svgResumo,
  type PainelGoverno,
} from '../charts/espectro-governismo';
import {
  carregarAgregados,
  carregarCatalogo,
  carregarIdeologia,
  carregarGovernos,
  carregarIndicadores,
  carregarPartidos,
  type Indicadores,
  type Catalogo,
  type Gabinete,
  type Governos,
  type Ministro,
  type Partido,
} from '../dados';
import { ajuda } from '../design/ajuda';
import { iniciarTema } from '../design/tema';
import { esc, formatarNumero, pct } from '../formato';
import { coresDasFaixas } from '../ideologia';
import { siglaEm } from '../siglas';
import { mostrarAtualizacao } from '../atualizacao';
import { posicaoDoPresidente } from '../presidente';

const $ = (sel: string) => document.querySelector(sel) as HTMLElement;
const SVG = 'http://www.w3.org/2000/svg';
const MAIORIA = 257;

const EVENTO: Record<Gabinete['evento'], string> = {
  A: 'posse do presidente',
  B: 'mudança de partidos',
  C: 'mudança relevante de ministro',
};

const MESES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];

function dataCurta(iso: string): string {
  const [a, m, d] = iso.split('-');
  const mes = `${MESES[Number(m) - 1]}/${a}`;
  return d ? `${Number(d)}/${mes}` : mes;
}

function siglas(ids: string[], data: string, partidos: Record<string, Partido>): string {
  if (!ids.length) return '<span class="posicao-celula">nenhum partido</span>';
  return ids
    .map(
      (id) =>
        `<a href="partidos.html?p=${encodeURIComponent(id)}">${esc(siglaEm(id, data, partidos))}</a>`,
    )
    .join(', ');
}

function grafico(cat: Catalogo, gov: Governos): SVGSVGElement {
  const fotos = cat.momentos.filter((m) => m.tipo === 'exercicio');
  const largura = 820;
  const altura = 230;
  const esq = 44;
  const base = 190;
  const topo = 20;
  const passo = (largura - esq - 10) / fotos.length;
  const y = (v: number) => base - (v / 513) * (base - topo);
  const svg = document.createElementNS(SVG, 'svg');
  svg.setAttribute('viewBox', `0 0 ${largura} ${altura}`);
  svg.setAttribute('class', 'grafico-pontos');
  svg.setAttribute('role', 'img');
  svg.setAttribute(
    'aria-label',
    'Cadeiras dos partidos com ministério em cada 1º de fevereiro. Os números estão nas tabelas abaixo.',
  );
  const no = (tag: string, a: Record<string, string | number>, texto?: string) => {
    const e = document.createElementNS(SVG, tag);
    for (const [k, v] of Object.entries(a)) e.setAttribute(k, String(v));
    if (texto !== undefined) e.textContent = texto;
    svg.append(e);
    return e;
  };
  for (const v of [0, 128, 257, 385, 513]) {
    no('line', { x1: esq, x2: largura - 10, y1: y(v), y2: y(v), class: 'grafico-grade' });
    no('text', { x: esq - 6, y: y(v) + 4, class: 'grafico-eixo', 'text-anchor': 'end' }, String(v));
  }
  no('line', {
    x1: esq,
    x2: largura - 10,
    y1: y(MAIORIA),
    y2: y(MAIORIA),
    class: 'linha-maioria',
  });
  no(
    'text',
    { x: largura - 150, y: y(MAIORIA) - 6, class: 'grafico-eixo', 'text-anchor': 'start' },
    'maioria absoluta: 257',
  );
  fotos.forEach((m, i) => {
    const b = gov.base_por_momento[m.id];
    const x = esq + i * passo + passo * 0.15;
    const w = passo * 0.7;
    if (b?.cadeiras_base == null) {
      no('rect', { x, y: topo, width: w, height: base - topo, class: 'barra-sem-dados' });
    } else {
      const r = no('rect', {
        x,
        y: y(b.cadeiras_base),
        width: w,
        height: base - y(b.cadeiras_base),
        rx: 3,
        class: 'barra-base',
      });
      const t = document.createElementNS(SVG, 'title');
      t.textContent = `1º/fev/${m.ano}: ${b.cadeiras_base} cadeiras (${pct(b.cadeiras_base, m.cadeiras)}), gabinete ${b.gabinete}`;
      r.append(t);
    }
    if (i % 2 === 0 || fotos.length < 14) {
      no('text', { x: x + w / 2, y: base + 16, class: 'grafico-eixo' }, String(m.ano));
    }
  });
  return svg;
}

/** Base formal × comportamento (PROJECT.md 3.2): governismo e coesão de cada partido no governo,
 * com a indicação de se teve ministério em algum gabinete. */
function comportamento(
  governo: string,
  gabs: Gabinete[],
  ind: Indicadores,
  partidos: Record<string, Partido>,
  inicio: string,
): string {
  const comMinisterio = new Set(gabs.flatMap((g) => g.partidos));
  const linhas = Object.entries(ind.partidos)
    .map(([id, x]) => ({ id, x: x.governos?.[governo] }))
    .filter((r) => r.x && r.x.governismo !== null && (r.x.votos ?? 0) > 0)
    .sort((a, b) => (b.x?.governismo ?? 0) - (a.x?.governismo ?? 0));
  if (!linhas.length) return '';
  const pctTexto = (v: number | null | undefined) =>
    v == null ? '—' : `${formatarNumero(100 * v, 1)}%`;
  const corpo = linhas
    .map(
      ({ id, x }) =>
        `<tr><td><a href="partidos.html?p=${encodeURIComponent(id)}">${esc(siglaEm(id, inicio, partidos))}</a></td>
        <td>${comMinisterio.has(id) ? 'sim' : 'não'}</td><td class="num">${pctTexto(x?.governismo)}</td>
        <td class="num">${x?.votos ?? '—'}</td><td class="num">${x?.rice == null ? '—' : formatarNumero(x.rice, 2)}</td></tr>`,
    )
    .join('');
  return `<h3>Como os partidos votaram</h3>
    <p class="bloco-dica">Governismo: votos iguais à orientação do Governo ÷ votos Sim, Não, Abstenção e Obstrução, nas votações nominais em que o Governo orientou Sim ou Não. Coesão: Índice de Rice médio. Ministério: se o partido teve ministro em algum gabinete deste governo.</p>
    <div class="tabela-rolagem"><table class="ranking"><thead><tr><th scope="col">Partido</th><th scope="col">Ministério</th><th scope="col">Governismo</th><th scope="col">Votos considerados</th><th scope="col">Coesão</th></tr></thead><tbody>${corpo}</tbody></table></div>`;
}

/** Texto da fonte com os endereços como links (o texto é escapado pedaço a pedaço, para não
 * quebrar endereços com "&"). */
function comLinks(texto: string): string {
  return texto
    .split(/(https?:\/\/[^\s|]+)/)
    .map((parte, i) => {
      if (i % 2 === 0) return esc(parte);
      const url = parte.replace(/[;,.)]+$/, '');
      const resto = parte.slice(url.length);
      const rotulo = url.replace(/^https?:\/\//, '');
      return `<a href="${esc(url)}" target="_blank" rel="noopener">${esc(rotulo.length > 60 ? `${rotulo.slice(0, 60)}…` : rotulo)}</a>${esc(resto)}`;
    })
    .join('');
}

/** Fonte de um gabinete: a citação do IPEA ou os links da curadoria (o caminho do arquivo do
 * repositório não interessa ao leitor; a lista de ministros vem logo abaixo). */
function fonteDoGabinete(fonte: string): string {
  if (!fonte.startsWith('Curadoria')) return comLinks(fonte);
  const links = fonte.split(' | ').slice(1);
  return `curadoria do projeto pelo critério do IPEA${links.length ? ` — ${links.map(comLinks).join(' · ')}` : ''}`;
}

function tabelaMinistros(lista: Ministro[]): string {
  if (!lista.length) return '';
  const linhas = [...lista]
    .sort((a, b) => a.posse.localeCompare(b.posse))
    .map(
      (m) => `<tr><td>${esc(m.ministro)}</td><td>${esc(m.cargo)}</td><td>${esc(m.partido)}</td>
        <td class="num">${esc(dataCurta(m.posse))}${m.saida ? ` a ${esc(dataCurta(m.saida))}` : ''}</td>
        <td>${esc(m.conta)}</td>
        <td class="posicao-celula">${m.motivo ? `${esc(m.motivo)}<br>` : ''}${m.fontes.map((u, i) => `<a href="${esc(u)}" target="_blank" rel="noopener">fonte ${i + 1}</a>`).join(' · ')}</td></tr>`,
    )
    .join('');
  return `<details class="detalhes-partidos"><summary>Ministros com filiação partidária: classificação e fontes (${lista.length})</summary>
    <div class="tabela-rolagem"><table class="ranking"><thead><tr><th scope="col">Ministro</th><th scope="col">Cargo</th><th scope="col">Partido</th><th scope="col">Período</th><th scope="col">Conta para a base?</th><th scope="col">Motivo e fontes</th></tr></thead>
    <tbody>${linhas}</tbody></table></div></details>`;
}

const NOMES_CURTOS: Record<string, string> = {
  collor: 'Collor',
  itamar: 'Itamar',
  fhc1: 'FHC 1',
  fhc2: 'FHC 2',
  lula1: 'Lula 1',
  lula2: 'Lula 2',
  dilma1: 'Dilma 1',
  dilma2: 'Dilma 2',
  temer: 'Temer',
  bolsonaro: 'Bolsonaro',
  lula3: 'Lula 3',
};

/** Nome curto do governo para os gráficos ("Lula 3", "Temer"). */
function rotuloGoverno(g: { governo_id: string; presidente: string }): string {
  return NOMES_CURTOS[g.governo_id] ?? g.presidente;
}

const pctLado = (v: number | null) => (v == null ? '—' : `${formatarNumero(100 * v, 0)}%`);

function tabelaLados(paineis: PainelGoverno[], casa: string): string {
  const linhas = paineis
    .map((p) => {
      const c = (l: 'esquerda' | 'direita') =>
        p.lados[l].governismo == null
          ? '—'
          : `${pctLado(p.lados[l].governismo)} <span class="posicao-celula">(${p.lados[l].cadeiras} cadeiras)</span>`;
      return `<tr><td>${esc(rotuloGoverno(p.governo))}</td><td>${p.ladoDoGoverno ?? '—'}</td><td class="num">${c('esquerda')}</td><td class="num">${c('direita')}</td></tr>`;
    })
    .join('');
  return `<details class="detalhes-partidos"><summary>Os números (${casa})</summary><div class="tabela-rolagem"><table class="ranking"><thead><tr><th scope="col">Governo</th><th scope="col">Lado do presidente</th><th scope="col">Governismo, lado esquerdo</th><th scope="col">Governismo, lado direito</th></tr></thead><tbody>${linhas}</tbody></table></div></details>`;
}

async function iniciar(): Promise<void> {
  const [cat, gov, partidos, ind, ideologia, agregados, catSen, agrSen, indSen] = await Promise.all(
    [
      carregarCatalogo(),
      carregarGovernos(),
      carregarPartidos(),
      carregarIndicadores(),
      carregarIdeologia(),
      carregarAgregados(),
      carregarCatalogo('senado'),
      carregarAgregados('senado'),
      carregarIndicadores('senado'),
    ],
  );
  const sigla = (p: string, d: string) => siglaEm(p, d, partidos);
  const paineisCamara = montarPaineis(gov.governos, ind, ideologia, cat, agregados, sigla);
  const paineisSenado = montarPaineis(gov.governos, indSen, ideologia, catSen, agrSen, sigla);
  const secoes = [...gov.governos]
    .reverse()
    .map((g) => {
      const gabs = gov.gabinetes.filter((x) => x.governo === g.governo_id);
      const linhas = gabs
        .map((x) => {
          const b = x.base_no_inicio;
          const cadeiras = b ? `${b.cadeiras} (${pct(b.cadeiras, 513)})` : '—';
          const nota = `<tr class="linha-nota"><td></td><td colspan="4">${x.observacao ? `${esc(x.observacao)}<br>` : ''}<span class="posicao-celula">Fonte: ${fonteDoGabinete(x.fonte)}</span></td></tr>`;
          return `<tr><td>${esc(x.gabinete)}</td><td>${esc(dataCurta(x.inicio))}</td><td>${EVENTO[x.evento]}</td>
            <td>${siglas(x.partidos, x.inicio, partidos)}</td><td class="num">${cadeiras}</td></tr>${nota}`;
        })
        .join('');
      const tabela = gabs.length
        ? `<div class="tabela-rolagem"><table class="ranking"><thead><tr><th scope="col">Gabinete</th><th scope="col">Início</th><th scope="col">Origem</th><th scope="col">Partidos com ministro</th><th scope="col">Cadeiras no início</th></tr></thead><tbody>${linhas}</tbody></table></div>`
        : `<p class="aviso-lacuna">Sem dados de gabinete para este governo.</p>`;
      const curadoria = gabs.some((x) => x.fonte.startsWith('Curadoria'))
        ? `<p class="aviso-lacuna">Gabinetes a partir de 2021: curadoria do projeto, ministro a ministro, pelo mesmo critério do IPEA, com fonte para cada nomeação; cobre até ${esc(dataCurta(gov.cobertura_ate))}.</p>${tabelaMinistros(gov.ministros.filter((m) => m.posse <= g.fim && (m.saida ?? '9999') >= g.inicio))}`
        : '';
      return `<section class="bloco" aria-labelledby="gov-${g.governo_id}">
        <h2 class="bloco-titulo" id="gov-${g.governo_id}">${esc(g.presidente)} — ${esc(dataCurta(g.inicio))} a ${esc(dataCurta(g.fim))}</h2>
        <p class="bloco-dica">Partido do presidente: ${esc(g.partido_presidente)}${g.observacao ? ` · ${esc(g.observacao)}` : ''}</p>
        <div class="bloco-dica">Posição do presidente:${posicaoDoPresidente(g)}</div>
        ${tabela}${curadoria}${comportamento(g.governo_id, gabs, ind, partidos, g.inicio)}</section>`;
    })
    .join('');
  $('#conteudo').outerHTML = `<div id="conteudo" class="pagina-governos">
    <section class="bloco">
      <h1 class="bloco-titulo">Governos e o Congresso</h1>
      <p class="bloco-dica">Três perguntas diferentes, que muitas vezes se confundem:</p>
      <div class="tres-perguntas">
        <div><b>1 · Base formal</b><div class="pergunta">Quem tem ministério?</div>Partidos com ao menos um ministro que os represente, pelo critério do IPEA. É um fato sobre o governo.</div>
        <div><b>2 · Governismo</b><div class="pergunta">Quem vota com o governo?</div>Proporção dos votos de cada partido iguais à orientação do governo nas votações nominais. É um fato sobre o comportamento.</div>
        <div><b>3 · Espectro</b><div class="pergunta">De que lado está cada partido?</div>A posição ideológica do partido segundo a pesquisa acadêmica da época. Permite ver se um governo é acompanhado pelo lado oposto.</div>
      </div>
      <p class="frase-chave"><strong>Ter ministério não garante voto, e votar junto não exige ministério nem afinidade ideológica.</strong></p>
    </section>
    <section class="bloco" aria-labelledby="titulo-espectro">
      <h2 class="bloco-titulo" id="titulo-espectro">Quem acompanha cada governo, pelo espectro</h2>
      <p class="bloco-dica">Governismo médio dos partidos de cada lado da escala ideológica, ponderado pelas cadeiras em 1º de fevereiro do primeiro ano do governo. Na Câmara, só há governismo de 2003 em diante.</p>
      <div class="legenda-lados"><span><i style="background:var(--faixa-2)"></i>partidos do lado esquerdo da escala</span><span><i style="background:var(--faixa-6)"></i>partidos do lado direito</span></div>
      <div id="espectro-resumo"></div>
      ${tabelaLados(paineisCamara, 'Câmara')}
      <h3>Senado</h3>
      <p class="bloco-dica">No Senado, a orientação do governo só é registrada a partir de 2019.</p>
      <div id="espectro-senado"></div>
      ${tabelaLados(paineisSenado, 'Senado')}
      <p class="aviso-lacuna">"Governo de esquerda/direita": pela posição do próprio presidente na BLS (abaixo ou acima do ponto médio). Lado do partido: até 2023, abaixo ou acima do ponto médio da escala da BLS, convenção do site porque a fonte não publica faixas; de 2023 em diante, as faixas de Bolognesi et al. (esquerda: extrema-esquerda a centro-esquerda; direita: centro-direita a extrema-direita; o centro fica de fora). As duas escalas não são a mesma régua: a comparação entre governos é de padrão, não de valor exato.</p>
      <h3>Partido a partido (Câmara)</h3>
      <p class="bloco-dica">Cada círculo é um partido: posição na escala da época (horizontal), governismo naquele governo (vertical) e área proporcional às cadeiras. Passe o mouse para ver os números.</p>
      <div class="paineis-espectro" id="espectro-paineis"></div>
    </section>
    <section class="bloco">
      <div class="bloco-cabeca"><h1 class="bloco-titulo">Base formal dos governos</h1><span id="ajuda-base"></span></div>
      <p class="bloco-dica">Cadeiras na Câmara dos partidos com ministro, em cada 1º de fevereiro. A base formal não mede como esses partidos votaram; isso entra com as votações.</p>
      <div id="grafico-base"></div>
      <p class="aviso-lacuna">Gabinetes: Nota Técnica Diest nº 53 do IPEA (Almeida, 2021), de mar/1985 a dez/2020; depois, curadoria do projeto pelo mesmo critério, até ${esc(dataCurta(gov.cobertura_ate))}. Barras tracejadas: sem dados. Cadeiras no início do gabinete só a partir de 2003, quando começa o registro datado da Câmara.</p>
    </section>
    ${secoes}</div>`;
  $('#grafico-base').append(grafico(cat, gov));
  const desenharEspectro = () => {
    const cores = coresDasFaixas();
    $('#espectro-resumo').innerHTML = svgResumo(paineisCamara, rotuloGoverno);
    $('#espectro-senado').innerHTML = paineisSenado.length
      ? svgResumo(paineisSenado, rotuloGoverno)
      : '';
    $('#espectro-paineis').innerHTML = paineisCamara
      .map(
        (p) =>
          `<div class="painel-governo"><h3>${esc(rotuloGoverno(p.governo))} <span class="bloco-dica">(${p.legislatura}ª legislatura · lado esquerdo ${pctLado(p.lados.esquerda.governismo)} · lado direito ${pctLado(p.lados.direita.governismo)})</span></h3>${svgPainel(p, cores)}</div>`,
      )
      .join('');
  };
  desenharEspectro();
  iniciarTema(desenharEspectro);
  $('#ajuda-base').innerHTML = ajuda(
    'ajuda-base-pop',
    'O que é base formal',
    'Pelo critério do IPEA, um ministro é partidário quando foi nomeado por seus vínculos com um partido e é reconhecido por esse partido como seu representante; filiação sozinha não basta. Um novo gabinete começa com a posse do presidente, com a entrada ou saída de partidos, ou com uma mudança relevante de ministro.',
  );
  document.body.dataset['pronto'] = 'true';
}

void mostrarAtualizacao(['governos', 'composicao_camara', 'votacoes_camara']);
iniciar().catch((erro: unknown) => {
  console.error(erro);
  $('#erro').hidden = false;
});
