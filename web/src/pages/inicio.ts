// Início: hemiciclo de um momento (eleitos de uma eleição ou foto de 1º/fev), linha do tempo,
// tabela acessível e cadeiras por partido (PROJECT.md, 4.1.1). Estado na URL: ?m=<momento>&v=tabela.

import '../design/mapa.css';
import '../design/congresso.css';
import { desenharHemiciclo } from '../charts/hemiciclo-svg';
import { compor, type Composicao } from '../composicao';
import {
  carregarCatalogo,
  casaDaUrl,
  carregarGovernos,
  carregarIdeologia,
  carregarMomento,
  carregarPartidos,
  type BaseNoMomento,
  type Governos,
  type Partido,
  type Catalogo,
  type Deputado,
  type Ideologia,
  type Momento,
  type TipoMomento,
} from '../dados';
import { ajuda } from '../design/ajuda';
import { iniciarTema } from '../design/tema';
import { esc, pct } from '../formato';
import { siglaEm } from '../siglas';
import { coresDasFaixas, corDe, FAIXAS, linhaDeFonte, nomeFonte, NOTA_EXTREMA } from '../ideologia';
import { mostrarAtualizacao } from '../atualizacao';
import { barraPosicao, celulaPosicao } from '../posicao';
import { descreverPresidente, governoEm, posicaoDoPresidente } from '../presidente';

const $ = <T extends HTMLElement = HTMLElement>(sel: string) => document.querySelector(sel) as T;

const ICONE_PLAY =
  '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M4 2.5v11l9-5.5z" fill="currentColor"/></svg>';
const ICONE_PAUSA =
  '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M4 2.5h3v11H4zM9 2.5h3v11H9z" fill="currentColor"/></svg>';
const PASSO_MS = 1200;

interface Estado {
  momento: Momento;
  visao: 'hemiciclo' | 'tabela';
  /** Esmaecer no hemiciclo quem não é da base formal do governo (só em fotos em exercício). */
  destacarBase: boolean;
}

const casa = casaDaUrl();
let catalogo: Catalogo;
let ideologia: Ideologia;
let governos: Governos;
let partidos: Record<string, Partido>;
let estado: Estado;
let composicao: Composicao;
let deputados: Deputado[] = [];
let timer: number | undefined;

function momentosDo(tipo: TipoMomento): Momento[] {
  return catalogo.momentos.filter((m) => m.tipo === tipo);
}

function lerUrl(): Estado {
  const p = new URLSearchParams(location.search);
  const exercicio = momentosDo('exercicio');
  const momento =
    catalogo.momentos.find((m) => m.id === p.get('m')) ?? (exercicio.at(-1) as Momento);
  return {
    momento,
    visao: p.get('v') === 'tabela' ? 'tabela' : 'hemiciclo',
    destacarBase: p.get('b') === '1',
  };
}

function gravarUrl(): void {
  const p = new URLSearchParams({ m: estado.momento.id });
  if (casa === 'senado') p.set('c', 'senado');
  if (estado.visao === 'tabela') p.set('v', 'tabela');
  if (estado.destacarBase) p.set('b', '1');
  history.replaceState(null, '', `?${p}`);
}

/** Ao trocar eleitos ↔ em exercício, vai para o momento do outro tipo mais próximo no tempo. */
function maisProximo(tipo: TipoMomento, ano: number): Momento {
  const lista = momentosDo(tipo);
  return lista.reduce((a, b) => (Math.abs(b.ano - ano) < Math.abs(a.ano - ano) ? b : a));
}

function pontosDaLegislatura() {
  return ideologia[String(estado.momento.legislatura)] ?? {};
}

function desenharResumo(): void {
  const m = estado.momento;
  const fora = composicao.naoClassificados.reduce((s, g) => s + g.deputados.length, 0);
  const maior = [...composicao.classificados, ...composicao.naoClassificados].sort(
    (a, b) => b.deputados.length - a.deputados.length,
  )[0];
  const nPartidos = composicao.classificados.length + composicao.naoClassificados.length;
  const cartoes = [
    ['Cadeiras ocupadas', `${m.ocupadas}`, `de ${m.cadeiras} · ${m.legislatura}ª legislatura`],
    ['Partidos', `${nPartidos}`, 'com ao menos 1 cadeira'],
    ['Maior bancada', maior ? maior.sigla : '—', maior ? `${maior.deputados.length} cadeiras` : ''],
    ['Não classificados', `${fora}`, fora ? pct(fora, m.ocupadas) + ' das cadeiras' : 'nenhum'],
  ];
  $('#resumo').innerHTML = cartoes
    .map(
      ([rotulo, valor, detalhe], i) => `<div class="cartao${i === 0 ? ' cartao-br' : ''}">
        <span class="cartao-rotulo">${esc(rotulo as string)}</span>
        <span class="cartao-valor">${esc(valor as string)}</span>
        <span class="cartao-detalhe">${esc(detalhe as string)}</span></div>`,
    )
    .join('');
}

function desenharLegenda(): void {
  const pontos = Object.values(pontosDaLegislatura());
  const temFaixa = pontos.some((p) => p.faixa);
  const cores = coresDasFaixas();
  const itens = temFaixa
    ? FAIXAS.map(
        (f, i) =>
          `<li><span class="amostra" style="background:${cores[i]}" aria-hidden="true"></span>${f}</li>`,
      ).join('')
    : `<li>esquerda<span class="legenda-continua" aria-hidden="true"></span>direita (escala −1 a +1, sem rótulo de faixa)</li>`;
  const p0 = pontos[0];
  const fonte = p0
    ? `Posição: ${esc(nomeFonte(p0))}${p0.nota && estado.momento.legislatura === 58 ? ` — ${esc(p0.nota)}` : ''}`
    : '';
  $('#legenda').innerHTML = `<p class="legenda-titulo">${fonte}</p><ul>${itens}
    <li><span class="amostra amostra-hachura" aria-hidden="true"></span>não classificado</li></ul>${temFaixa ? `<p class="nota-extrema">${esc(NOTA_EXTREMA)}</p>` : ''}`;
}

function desenharForaDaOrdem(): void {
  const m = estado.momento;
  const fora = composicao.naoClassificados;
  const vagas = m.em_curso ? 0 : m.cadeiras - m.ocupadas;
  const partes: string[] = [];
  if (m.em_curso) {
    partes.push(`<div class="nao-classificados">
      <span>Cadeiras com mandato em curso, não renovadas nesta eleição: ${m.em_curso}</span>
      <div class="fileira-a-parte" aria-hidden="true">${'<span class="vaga"></span>'.repeat(m.em_curso)}</div></div>`);
  }
  if (fora.length) {
    const lista = fora.map((g) => `${esc(g.sigla)} (${g.deputados.length})`).join(', ');
    const n = fora.reduce((s, g) => s + g.deputados.length, 0);
    partes.push(`<div class="nao-classificados">
      <span>Não classificados, fora da ordenação: ${n} — ${lista}</span>
      <div class="fileira-a-parte" aria-hidden="true">${'<span class="amostra-hachura"></span>'.repeat(n)}</div></div>`);
  }
  if (vagas > 0) {
    partes.push(`<div class="nao-classificados">
      <span>Cadeiras sem ninguém em exercício nesta data: ${vagas}</span>
      <div class="fileira-a-parte" aria-hidden="true">${'<span class="vaga"></span>'.repeat(vagas)}</div></div>`);
  }
  $('#fora-da-ordem').innerHTML = partes.join('');
}

function desenharFicha(texto: string): void {
  $('#ficha').innerHTML = texto;
}

function desenharTabelaDeputados(): void {
  const pontos = pontosDaLegislatura();
  const linhas = [...deputados]
    .sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'))
    .map(
      (d) =>
        `<tr><td>${esc(d.nome)}</td><td>${esc(d.uf)}</td><td>${esc(d.sigla)}</td><td>${celulaPosicao(pontos[d.partido])}</td></tr>`,
    )
    .join('');
  $('#tabela-deputados').innerHTML =
    `<p class="bloco-dica">${esc(linhaDeFonte(Object.values(pontos)))}</p><table class="ranking">
    <caption class="so-leitor">${esc(estado.momento.rotulo)} — deputados em ordem alfabética</caption>
    <thead><tr><th scope="col">Nome</th><th scope="col">UF</th><th scope="col">Partido</th><th scope="col">Posição do partido</th></tr></thead>
    <tbody>${linhas}</tbody></table>`;
}

function desenharTabelaPartidos(): void {
  const cores = coresDasFaixas();
  const m = estado.momento;
  const grupos = [...composicao.classificados, ...composicao.naoClassificados];
  const linhas = grupos
    .map((g) => {
      const corCss = g.pontuacao ? `background:${corDe(g.pontuacao, cores)}` : '';
      const classe = g.pontuacao ? 'cor-partido' : 'cor-partido amostra-hachura';
      return `<tr><td><span class="${classe}" style="${corCss}" aria-hidden="true"></span><a href="partidos.html?p=${encodeURIComponent(g.partido)}">${esc(g.sigla)}</a></td>
        <td class="num">${g.deputados.length}</td><td class="num">${pct(g.deputados.length, m.ocupadas)}</td>
        <td>${celulaPosicao(g.pontuacao)}</td></tr>`;
    })
    .join('');
  $('#tabela-partidos').innerHTML =
    `<p class="bloco-dica">${esc(linhaDeFonte(Object.values(pontosDaLegislatura())))}</p><div class="tabela-rolagem"><table class="ranking">
    <caption class="so-leitor">Cadeiras por partido — ${esc(m.rotulo)}, da esquerda para a direita; não classificados no fim</caption>
    <thead><tr><th scope="col">Partido</th><th scope="col">Cadeiras</th><th scope="col">%</th><th scope="col">Posição</th></tr></thead>
    <tbody>${linhas}</tbody></table></div>`;
}

function desenharSlider(): void {
  const lista = momentosDo(estado.momento.tipo);
  const range = $<HTMLInputElement>('#slider input');
  range.max = String(lista.length - 1);
  const i = lista.findIndex((m) => m.id === estado.momento.id);
  range.value = String(i);
  range.style.setProperty(
    '--progresso',
    `${lista.length > 1 ? (i / (lista.length - 1)) * 100 : 100}%`,
  );
  const rotulo = `${estado.momento.rotulo} · ${estado.momento.legislatura}ª legislatura`;
  $('#slider output').textContent = rotulo;
  range.setAttribute('aria-valuetext', rotulo);
  $('#aviso-lacuna').textContent = avisoLacuna();
}

function avisoLacuna(): string {
  const eleitos =
    'Eleitos conforme a situação atual de cada candidato no TSE, que já inclui retotalizações e decisões judiciais posteriores à eleição.';
  if (casa === 'camara') {
    return estado.momento.tipo === 'exercicio'
      ? 'Fotos em exercício só a partir de 2003: antes disso a Câmara não tem registro datado de quem exercia o mandato e por qual partido. Para 1990–2002, veja os eleitos.'
      : eleitos;
  }
  if (estado.momento.tipo === 'eleitos') {
    return `${eleitos} O Senado renova 1/3 ou 2/3 das cadeiras a cada eleição; as demais seguem com mandato em curso.`;
  }
  const anos = (catalogo.lacunas ?? []).map((l) => l.data.slice(0, 4));
  return `Fotos do Senado só nos anos em que os registros oficiais de exercício somam exatamente 81 senadores, 3 por estado. Sem foto (registros incompletos ou sobrepostos na fonte): ${anos.join(', ')}. Partido pela filiação datada no Senado.`;
}

async function mostrar(momento: Momento): Promise<void> {
  estado.momento = momento;
  gravarUrl();
  deputados = await carregarMomento(momento.id);
  if (estado.momento !== momento) return; // outra troca chegou antes
  composicao = compor(deputados, pontosDaLegislatura());
  document
    .querySelectorAll<HTMLButtonElement>('[data-tipo]')
    .forEach((b) => b.setAttribute('aria-pressed', String(b.dataset['tipo'] === momento.tipo)));
  $('#titulo-momento').textContent =
    `${casa === 'senado' ? 'Senado' : 'Câmara'} — ${momento.rotulo} — ${momento.legislatura}ª legislatura`;
  desenharResumo();
  desenharSlider();
  desenharLinhaPresidente();
  desenharLinhaBase();
  desenharTudoQueDependeDoTema();
  desenharTabelaDeputados();
  desenharFicha('');
}

/** Base formal do governo na data (só fotos em exercício): partidos com ministro (IPEA e
 * curadoria) e suas cadeiras. Sem dados depois do fim da cobertura. */
function baseDoMomento(): BaseNoMomento | undefined {
  const m = estado.momento;
  if (m.tipo !== 'exercicio') return undefined;
  if (casa === 'camara') return governos.base_por_momento[m.id];
  // Senado: a base vem no próprio momento; o governo é o vigente na data da foto.
  if (!m.base || !m.data) return undefined;
  const dia = m.data;
  const governo = governos.governos.find((g) => g.inicio <= dia && dia <= g.fim);
  return { ...m.base, ocupadas: m.ocupadas, governo: governo?.governo_id ?? null };
}

function fonteDoGabinete(nome: string): string {
  const g = governos.gabinetes.find((x) => x.gabinete === nome);
  return g?.fonte.startsWith('Curadoria')
    ? 'curadoria do projeto pelo critério do IPEA'
    : 'IPEA (Almeida, 2021)';
}

/** Presidente na data da foto ou, nos eleitos, no início da legislatura (1º/fev do ano seguinte). */
function desenharLinhaPresidente(): void {
  const m = estado.momento;
  const dia = m.tipo === 'exercicio' && m.data ? m.data : `${m.ano + 1}-02-01`;
  const g = governoEm(governos.governos, dia);
  const quando = m.tipo === 'exercicio' ? 'Presidente' : 'Presidente no início da legislatura';
  $('#linha-presidente').innerHTML = g
    ? `${quando}: <strong>${descreverPresidente(g)}</strong>${posicaoDoPresidente(g)}`
    : `${quando}: ainda não registrado no site.`;
}

function desenharLinhaBase(): void {
  const el = $('#linha-base');
  const base = baseDoMomento();
  el.hidden = !base;
  if (!base) return;
  if (base.gabinete === null || base.cadeiras_base === null) {
    el.innerHTML = `Base formal: sem dados nesta data. <a href="governos.html">Governos</a>`;
    return;
  }
  const siglas =
    base.partidos.map((id) => siglaEm(id, estado.momento.id, partidos)).join(', ') || 'nenhum';
  el.innerHTML = `Base formal (partidos com ministro, gabinete ${esc(base.gabinete)}): ${esc(siglas)} — ${base.cadeiras_base} cadeiras (${pct(base.cadeiras_base, estado.momento.cadeiras)}). Fonte: ${fonteDoGabinete(base.gabinete)}.
    <label><input type="checkbox" id="destacar-base"${estado.destacarBase ? ' checked' : ''}> destacar no hemiciclo</label>`;
  ($('#destacar-base') as HTMLInputElement).addEventListener('change', (e) => {
    estado.destacarBase = (e.target as HTMLInputElement).checked;
    gravarUrl();
    desenharTudoQueDependeDoTema();
  });
}

function desenharTudoQueDependeDoTema(): void {
  const base = baseDoMomento();
  const destaque =
    estado.destacarBase && base?.cadeiras_base !== null && base
      ? new Set(base.partidos)
      : undefined;
  desenharHemiciclo(
    $('#hemiciclo'),
    composicao,
    coresDasFaixas(),
    (s) =>
      desenharFicha(
        s
          ? `<strong>${esc(s.deputado.nome)}</strong> · ${esc(s.deputado.sigla)} · ${esc(s.deputado.uf)}${s.pontuacao?.faixa ? ` — ${esc(s.pontuacao.faixa)}` : ''}${barraPosicao(s.pontuacao)}`
          : '',
      ),
    destaque,
  );
  desenharForaDaOrdem();
  desenharLegenda();
  desenharTabelaPartidos();
}

function mudarVisao(visao: Estado['visao']): void {
  estado.visao = visao;
  gravarUrl();
  $('#area-hemiciclo').hidden = visao !== 'hemiciclo';
  $('#area-tabela').hidden = visao !== 'tabela';
  document
    .querySelectorAll<HTMLButtonElement>('[data-visao]')
    .forEach((b) => b.setAttribute('aria-pressed', String(b.dataset['visao'] === visao)));
}

function parar(): void {
  if (timer) window.clearInterval(timer);
  timer = undefined;
  const play = $('#slider .play');
  play.innerHTML = ICONE_PLAY;
  play.setAttribute('aria-label', 'Animar ao longo do tempo');
}

function ligarControles(): void {
  const range = $<HTMLInputElement>('#slider input');
  range.addEventListener('input', () => {
    parar();
    const m = momentosDo(estado.momento.tipo)[Number(range.value)];
    if (m) void mostrar(m);
  });
  const play = $('#slider .play');
  play.innerHTML = ICONE_PLAY;
  play.addEventListener('click', () => {
    if (timer) return parar();
    const lista = momentosDo(estado.momento.tipo);
    if (estado.momento === lista.at(-1)) void mostrar(lista[0] as Momento);
    play.innerHTML = ICONE_PAUSA;
    play.setAttribute('aria-label', 'Pausar animação');
    timer = window.setInterval(() => {
      const i = lista.indexOf(estado.momento);
      const prox = lista[i + 1];
      if (!prox) return parar();
      void mostrar(prox);
    }, PASSO_MS);
  });
  document.querySelectorAll<HTMLButtonElement>('[data-tipo]').forEach((b) =>
    b.addEventListener('click', () => {
      parar();
      const tipo = b.dataset['tipo'] as TipoMomento;
      if (tipo !== estado.momento.tipo) void mostrar(maisProximo(tipo, estado.momento.ano));
    }),
  );
  document
    .querySelectorAll<HTMLButtonElement>('[data-visao]')
    .forEach((b) =>
      b.addEventListener('click', () => mudarVisao(b.dataset['visao'] as Estado['visao'])),
    );
}

async function iniciar(): Promise<void> {
  [catalogo, ideologia, governos, partidos] = await Promise.all([
    carregarCatalogo(casa),
    carregarIdeologia(),
    carregarGovernos(),
    carregarPartidos(),
  ]);
  estado = lerUrl();
  $('#ajuda-hemiciclo').innerHTML = ajuda(
    'ajuda-hemiciclo-pop',
    'Como ler o hemiciclo',
    'Cada bolinha é uma cadeira. Os partidos vão da esquerda para a direita pela posição ideológica medida pela fonte acadêmica da legislatura; dentro do partido, os parlamentares estão em ordem alfabética. A cor mostra a posição do partido, não o partido: partidos de mesma posição têm a mesma cor e são separados por linhas e siglas. Partidos sem medição na fonte ficam fora da ordenação, à parte. <a href="metodologia.html">Metodologia</a>',
  );
  $('#titulo-tabela').textContent = casa === 'senado' ? 'Senadores' : 'Deputados';
  // A regra dos lugares (só líderes com lugar marcado) foi conferida para a Câmara, não para o Senado.
  if (casa === 'senado')
    $('#nota-hemiciclo').textContent =
      'A posição das cadeiras é representativa; não corresponde ao assento real no plenário.';
  $('#rodape-fontes').textContent =
    `Composição: TSE (eleitos), Câmara dos Deputados e Senado Federal (em exercício). Posição ideológica: Zucco & Power (BLS) e Bolognesi et al.`;
  document.querySelectorAll<HTMLButtonElement>('[data-casa]').forEach((b) => {
    b.setAttribute('aria-pressed', String(b.dataset['casa'] === casa));
    b.addEventListener('click', () => {
      if (b.dataset['casa'] !== casa)
        location.search = b.dataset['casa'] === 'senado' ? '?c=senado' : '';
    });
  });
  ligarControles();
  mudarVisao(estado.visao);
  iniciarTema(() => desenharTudoQueDependeDoTema());
  await mostrar(estado.momento);
  document.body.dataset['pronto'] = 'true';
}

void mostrarAtualizacao([
  casa === 'senado' ? 'composicao_senado' : 'composicao_camara',
  'governos',
]);
iniciar().catch((erro: unknown) => {
  console.error(erro);
  $('#erro').hidden = false;
});
