// Evolução (PROJECT.md, 4.1.2). Por decisão A7, não há "% por faixa" antes da 57ª legislatura:
// a evolução mostra onde cada bancada estava na escala da fonte vigente, em dois painéis separados
// pela quebra de método. Estado na URL: ?c=senado&t=exercicio&l=1.

import '../design/mapa.css';
import '../design/congresso.css';
import {
  carregarAgregados,
  carregarCatalogo,
  carregarIdeologia,
  carregarPartidos,
  casaDaUrl,
  type Agregados,
  type Catalogo,
  type Ideologia,
  type Momento,
  type Partido,
  type TipoMomento,
} from '../dados';
import { ajuda } from '../design/ajuda';
import { iniciarTema } from '../design/tema';
import { esc, formatarNumero, pct } from '../formato';
import { coresDasFaixas, corDe, FAIXAS } from '../ideologia';
import { somarPorLinhagem } from '../linhagem';
import { mostrarAtualizacao } from '../atualizacao';

const $ = (sel: string) => document.querySelector(sel) as HTMLElement;
const SVG = 'http://www.w3.org/2000/svg';

let catalogo: Catalogo;
let ideologia: Ideologia;
let partidos: Record<string, Partido>;
let agregados: Agregados;
const casa = casaDaUrl();
let tipo: TipoMomento = 'eleitos';
let linhagem = false;

interface Escala {
  min: number;
  max: number;
  marcas: number[];
  /** Faixas de fundo (Bolognesi): [início, fim, índice da faixa]. */
  faixas?: [number, number, number][];
}

const ESCALA_BLS: Escala = { min: -1, max: 1, marcas: [-1, -0.5, 0, 0.5, 1] };
const ESCALA_BOLOGNESI: Escala = {
  min: 0,
  max: 10,
  marcas: [0, 2, 4, 6, 8, 10],
  faixas: [
    [0, 1.5, 0],
    [1.5, 3, 1],
    [3, 4.5, 2],
    [4.5, 5.5, 3],
    [5.5, 7, 4],
    [7, 8.5, 5],
    [8.5, 10, 6],
  ],
};

function no<K extends keyof SVGElementTagNameMap>(
  tag: K,
  attrs: Record<string, string | number>,
  texto?: string,
): SVGElementTagNameMap[K] {
  const e = document.createElementNS(SVG, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, String(v));
  if (texto !== undefined) e.textContent = texto;
  return e;
}

/** Um painel: uma linha por momento, um círculo por partido classificado. */
function painel(alvo: HTMLElement, momentos: Momento[], escala: Escala, titulo: string): void {
  if (!momentos.length) {
    alvo.replaceChildren();
    return;
  }
  const cores = coresDasFaixas();
  const largura = 820;
  const esq = 92;
  const dir = 150;
  const linha = 40;
  const topo = 46;
  const altura = topo + momentos.length * linha + 10;
  const x = (v: number) =>
    esq + ((v - escala.min) / (escala.max - escala.min)) * (largura - esq - dir);

  const svg = no('svg', {
    viewBox: `0 0 ${largura} ${altura}`,
    class: 'grafico-pontos',
    role: 'img',
    'aria-label': `${titulo}. A tabela de cadeiras por partido, abaixo, traz os mesmos números.`,
  });
  svg.append(no('text', { x: esq, y: 14, class: 'grafico-titulo' }, titulo));

  for (const [ini, fim, i] of escala.faixas ?? []) {
    svg.append(
      no('rect', {
        x: x(ini),
        y: topo - 8,
        width: x(fim) - x(ini),
        height: altura - topo,
        fill: cores[i] as string,
        opacity: 0.16,
      }),
    );
    svg.append(
      no(
        'text',
        { x: (x(ini) + x(fim)) / 2, y: topo - 12, class: 'grafico-faixa' },
        FAIXAS[i] ?? '',
      ),
    );
  }
  for (const m of escala.marcas) {
    svg.append(
      no('line', { x1: x(m), x2: x(m), y1: topo - 6, y2: altura - 6, class: 'grafico-grade' }),
    );
    svg.append(
      no(
        'text',
        { x: x(m), y: altura - 0, class: 'grafico-eixo' },
        formatarNumero(m, Number.isInteger(m) ? 0 : 1),
      ),
    );
  }
  if (!escala.faixas) {
    svg.append(
      no('text', { x: x(-1), y: 30, class: 'grafico-eixo', 'text-anchor': 'start' }, '← esquerda'),
    );
    svg.append(
      no('text', { x: x(1), y: 30, class: 'grafico-eixo', 'text-anchor': 'end' }, 'direita →'),
    );
  }

  momentos.forEach((m, i) => {
    const y = topo + i * linha + linha / 2;
    const pontos = ideologia[String(m.legislatura)] ?? {};
    const cadeiras = agregados[m.id] ?? {};
    svg.append(
      no(
        'text',
        { x: esq - 12, y: y + 4, class: 'grafico-rotulo', 'text-anchor': 'end' },
        String(m.ano),
      ),
    );
    let fora = 0;
    const lista = Object.entries(cadeiras).sort((a, b) => b[1] - a[1]);
    for (const [id, n] of lista) {
      const p = pontos[id];
      if (!p) {
        fora += n;
        continue;
      }
      const c = no('circle', {
        cx: x(p.pontuacao),
        cy: y,
        // Área proporcional às cadeiras; no Senado (81) a escala é maior para que se veja.
        r: Math.sqrt(n) * (casa === 'senado' ? 2.5 : 1.25),
        fill: corDe(p, cores),
        class: 'ponto-partido',
      });
      const sigla = partidos[id]?.sigla ?? id;
      c.append(
        no(
          'title',
          {},
          `${m.ano}: ${sigla}, ${n} cadeiras — ${formatarNumero(p.pontuacao, p.fonte_id === 'bls' ? 2 : 1)}`,
        ),
      );
      svg.append(c);
    }
    const total = m.ocupadas;
    svg.append(
      no(
        'text',
        { x: largura - dir + 14, y: y + 4, class: 'grafico-rotulo-fora' },
        fora ? `não classif.: ${pct(fora, total)}` : '',
      ),
    );
  });
  alvo.replaceChildren(svg);
}

function momentosDo(t: TipoMomento): Momento[] {
  return catalogo.momentos.filter((m) => m.tipo === t);
}

function desenharPaineis(): void {
  const lista = momentosDo(tipo);
  const comBls = lista.filter((m) => ideologia[String(m.legislatura)] && m.legislatura <= 56);
  const comBolognesi = lista.filter((m) => m.legislatura >= 57);
  painel($('#painel-bls'), comBls, ESCALA_BLS, 'BLS (Zucco & Power) — escala −1 a +1, sem faixas');
  painel(
    $('#painel-bolognesi'),
    comBolognesi,
    ESCALA_BOLOGNESI,
    'Bolognesi et al. (2022) — escala 0 a 10, com as sete faixas dos autores',
  );
}

/** Sigla atual, siglas anteriores (renomeações) e, em homônimos, o nome por extenso. */
function rotuloPartido(id: string, comAntecessores: boolean): string {
  const p = partidos[id];
  if (!p) return esc(id);
  const anteriores = [...new Set(p.renomeacoes.map((r) => r.sigla_anterior))].filter(
    (s) => s !== p.sigla,
  );
  const homonimo = Object.entries(partidos).some(
    ([outro, q]) => outro !== id && q.sigla === p.sigla,
  );
  const extras = [
    anteriores.length ? `ex-${anteriores.join(', ')}` : '',
    homonimo ? p.nome : '',
    comAntecessores && p.origem.length ? 'e antecessores' : '',
  ].filter(Boolean);
  return `${esc(p.sigla)}${extras.length ? ` <span class="th-unidade">${esc(extras.join(' · '))}</span>` : ''}`;
}

function desenharTabela(): void {
  const lista = momentosDo(tipo);
  const porMomento = lista.map((m) => {
    const c = agregados[m.id] ?? {};
    return linhagem ? somarPorLinhagem(c, partidos) : c;
  });
  const totais = new Map<string, number>();
  porMomento.forEach((c) =>
    Object.entries(c).forEach(([id, n]) => totais.set(id, (totais.get(id) ?? 0) + n)),
  );
  const ids = [...totais.keys()].sort((a, b) => (totais.get(b) ?? 0) - (totais.get(a) ?? 0));
  const maximo = Math.max(...porMomento.flatMap((c) => Object.values(c)), 1);
  const cabeca = lista.map((m) => `<th scope="col">${m.ano}</th>`).join('');
  const linhas = ids
    .map((id) => {
      const nome = rotuloPartido(id, linhagem);
      const celulas = porMomento
        .map((c) => {
          const n = c[id];
          if (!n) return '<td class="celula-vazia"></td>';
          // Teto de 0,6: acima disso o texto perde contraste (WCAG 4,5:1) nos dois temas.
          const alfa = 0.12 + 0.48 * (n / maximo);
          return `<td class="num celula-calor" style="--alfa:${alfa.toFixed(2)}">${n}</td>`;
        })
        .join('');
      return `<tr><th scope="row"><a href="partidos.html?p=${encodeURIComponent(id)}">${nome}</a></th>${celulas}</tr>`;
    })
    .join('');
  $('#tabela-cadeiras').innerHTML = `<table class="ranking tabela-calor">
    <caption class="so-leitor">Cadeiras por partido, ${tipo === 'eleitos' ? 'eleitos em cada eleição' : 'em exercício em 1º de fevereiro'}${linhagem ? ', somadas pela linhagem' : ''}</caption>
    <thead><tr><th scope="col">Partido</th>${cabeca}</tr></thead><tbody>${linhas}</tbody></table>`;
}

/** No Senado, avisa que as eleições renovam só parte das cadeiras e que faltam anos de foto. */
function desenharAvisoCasa(): void {
  const el = $('#aviso-casa');
  el.hidden = casa === 'camara';
  if (casa === 'camara') return;
  if (tipo === 'eleitos') {
    el.textContent =
      'Senado: cada eleição renova 1/3 ou 2/3 das 81 cadeiras, alternadamente. Cada linha mostra só os eleitos daquele ano; as demais cadeiras seguiam com mandato em curso.';
    return;
  }
  const anos = momentosDo('exercicio').map((m) => m.ano);
  el.textContent = `Senado em exercício: só os anos em que os registros do Senado fecham 81 senadores, 3 por UF, em 1º de fevereiro (${anos.join(', ')}). Os demais anos ficam de fora; veja a Metodologia.`;
}

function desenhar(): void {
  document
    .querySelectorAll<HTMLButtonElement>('[data-tipo]')
    .forEach((b) => b.setAttribute('aria-pressed', String(b.dataset['tipo'] === tipo)));
  const p = new URLSearchParams();
  if (casa === 'senado') p.set('c', 'senado');
  if (tipo === 'exercicio') p.set('t', 'exercicio');
  if (linhagem) p.set('l', '1');
  history.replaceState(null, '', p.size ? `?${p}` : location.pathname);
  desenharAvisoCasa();
  desenharPaineis();
  desenharTabela();
}

async function iniciar(): Promise<void> {
  [catalogo, ideologia, partidos, agregados] = await Promise.all([
    carregarCatalogo(casa),
    carregarIdeologia(),
    carregarPartidos(),
    carregarAgregados(casa),
  ]);
  document.querySelectorAll<HTMLButtonElement>('[data-casa]').forEach((b) => {
    b.setAttribute('aria-pressed', String(b.dataset['casa'] === casa));
    b.addEventListener('click', () => {
      if (b.dataset['casa'] !== casa)
        location.search = b.dataset['casa'] === 'senado' ? '?c=senado' : '';
    });
  });
  const p = new URLSearchParams(location.search);
  tipo = p.get('t') === 'exercicio' ? 'exercicio' : 'eleitos';
  linhagem = p.get('l') === '1';
  const caixa = document.querySelector<HTMLInputElement>('#seguir-linhagem') as HTMLInputElement;
  caixa.checked = linhagem;
  caixa.addEventListener('change', () => {
    linhagem = caixa.checked;
    desenhar();
  });
  document.querySelectorAll<HTMLButtonElement>('[data-tipo]').forEach((b) =>
    b.addEventListener('click', () => {
      tipo = b.dataset['tipo'] as TipoMomento;
      desenhar();
    }),
  );
  $('#ajuda-posicoes').innerHTML = ajuda(
    'ajuda-posicoes-pop',
    'Como ler',
    'Cada linha é uma eleição (ou uma data de 1º de fevereiro). Cada círculo é um partido, posto na posição que a fonte acadêmica da legislatura lhe atribui; a área do círculo é proporcional ao número de cadeiras. Partidos sem medição não aparecem no gráfico: a porcentagem de cadeiras não classificadas fica à direita de cada linha. Passe o mouse num círculo para ver o partido.',
  );
  iniciarTema(() => desenharPaineis());
  desenhar();
  document.body.dataset['pronto'] = 'true';
}

void mostrarAtualizacao([casa === 'senado' ? 'composicao_senado' : 'composicao_camara']);
iniciar().catch((erro: unknown) => {
  console.error(erro);
  $('#erro').hidden = false;
});
