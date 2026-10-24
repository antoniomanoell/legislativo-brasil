// Votações (PROJECT.md, 4.1.6): lista filtrável das votações nominais do plenário (2001 em diante)
// e, em ?v=<id>&a=<ano>, a votação com placar por partido, orientação do Governo e hemiciclo
// colorido pelo voto. Destaques só por critério objetivo (§7.7): PEC em 1º/2º turno. Com ?c=senado,
// as votações abertas do plenário do Senado (1991 em diante).

import '../design/mapa.css';
import '../design/congresso.css';
import { desenharHemiciclo } from '../charts/hemiciclo-svg';
import { compor } from '../composicao';
import {
  carregarIdeologia,
  carregarIndiceVotacoes,
  carregarPartidos,
  carregarArquivoVotacao,
  carregarVotacoesDoAno,
  casaDaUrl,
  type Deputado,
  type Ideologia,
  type Partido,
  type VotacaoResumo,
} from '../dados';
import { iniciarTema } from '../design/tema';
import { esc, formatarNumero } from '../formato';
import { coresDasFaixas } from '../ideologia';
import { siglaEm } from '../siglas';
import { COR_VOTO, decodificar, placarPorPartido, type Voto } from '../votos';

const $ = (sel: string) => document.querySelector(sel) as HTMLElement;
const POR_PAGINA = 100;
const casa = casaDaUrl();
const senado = casa === 'senado';
/** Sufixo dos links internos que mantêm a Casa. */
const sufixoCasa = senado ? '&c=senado' : '';
const parlamentar = senado ? 'senador' : 'deputado';
/** O código "7" é o presidente da sessão: "Artigo 17" na Câmara, "art. 51 RISF" no Senado. */
const ROTULO_PRESIDENTE = senado ? 'Presidente (art. 51 RISF)' : 'Artigo 17';
const rotuloVoto = (v: Voto) => (v === 'Artigo 17' ? ROTULO_PRESIDENTE : v);

function dataBr(iso: string): string {
  return iso.slice(0, 10).split('-').reverse().join('/');
}

function legislaturaEm(iso: string): number {
  const ano = Number(iso.slice(0, 4));
  const antesDaPosse = iso.slice(5, 10) < '02-01';
  const base = antesDaPosse ? ano - 1 : ano;
  return 52 + Math.floor((base - 2003) / 4);
}

function rotuloProposicao(v: VotacaoResumo): string {
  return v.proposicoes.length ? v.proposicoes.join(', ') : 'Votação';
}

function cortar(texto: string, n: number): string {
  return texto.length > n ? `${texto.slice(0, n).trimEnd()}…` : texto;
}

/** Ementa da primeira proposição, ou a descrição da votação quando a fonte não traz ementa. */
function ementa(v: VotacaoResumo): string {
  return v.materias?.find((m) => m.ementa)?.ementa ?? v.descricao;
}

/** Proposições votadas, cada uma com a ementa e o link para a página oficial. */
function materias(v: VotacaoResumo): string {
  if (!v.materias?.length) return '';
  const casaFonte = senado ? 'do Senado' : 'da Câmara';
  const link = (url: string, texto: string) =>
    `<a href="${esc(url)}" target="_blank" rel="noopener">${esc(texto)}</a>`;
  return `<h2 class="bloco-titulo">O que foi votado</h2>
    <p class="bloco-dica">Ementa, temas e indexação são publicados ${senado ? 'pelo Senado' : 'pela Câmara'}; o site não resume nem interpreta o texto.</p>
    <ul class="lista-materias">${v.materias
      .map((m) =>
        [
          `${link(m.url, m.rotulo)} <span class="bloco-dica">(página no portal ${casaFonte})</span>`,
          m.inteiro_teor ? ` · ${link(m.inteiro_teor, 'inteiro teor')}` : '',
          m.ementa ? `<br>${esc(m.ementa)}` : '',
          m.norma ? `<br>Norma gerada: ${link(m.norma.url, m.norma.rotulo)}` : '',
          m.temas?.length
            ? `<br><span class="posicao-celula">Temas: ${esc(m.temas.join('; '))}</span>`
            : '',
          m.assuntos
            ? `<details class="indexacao"><summary>Indexação oficial (palavras-chave)</summary><p class="posicao-celula">${esc(m.assuntos)}</p></details>`
            : '',
        ].join(''),
      )
      .map((x) => `<li>${x}</li>`)
      .join('')}</ul>`;
}

function resultado(v: VotacaoResumo): string {
  if (v.aprovada === null) return 'sem resultado registrado';
  return v.aprovada ? 'aprovada' : 'rejeitada';
}

/** Aviso quando o resultado da fonte contraria a maioria simples do placar. */
function avisoResultado(v: VotacaoResumo): string {
  const [s, n] = v.placar;
  if (v.aprovada === null)
    return `<p class="aviso-lacuna">A fonte não registra o resultado desta votação; veja o texto da votação acima.</p>`;
  if ((v.aprovada && s >= n) || (!v.aprovada && s <= n)) return '';
  return `<p class="aviso-lacuna">O resultado registrado pela fonte não coincide com a maioria simples do placar. Pode ser quórum qualificado (PEC: 3/5 da Casa; lei complementar: maioria absoluta), votação de texto destacado ou de parecer contrário (em que "Sim" mantém o parecer) ou erro na fonte. Confira o texto da votação e a página da proposição.</p>`;
}

function orientacao(v: VotacaoResumo): string {
  const o = v.orientacao_governo;
  if (!o) return 'sem orientação registrada';
  if (o === 'Liberado') return 'liberou a bancada';
  return o;
}

function legendaVotos(): string {
  const itens: [Voto | 'ausente', string][] = [
    ['Sim', 'Sim'],
    ['Não', 'Não'],
    ['Obstrução', 'Obstrução'],
    ['Abstenção', 'Abstenção'],
    ['Artigo 17', `${ROTULO_PRESIDENTE}: presidente da sessão`],
  ];
  return `<ul>${itens
    .map(
      ([v, rotulo]) =>
        `<li><span class="amostra" style="background:${COR_VOTO[v as Voto]};${v === 'Artigo 17' ? 'box-shadow: inset 0 0 0 1px var(--texto-2)' : ''}" aria-hidden="true"></span>${rotulo}</li>`,
    )
    .join('')}</ul>`;
}

async function detalhe(id: string, ano: number): Promise<void> {
  const [doAno, ideologia, partidos] = await Promise.all([
    id.startsWith('impeachment-') ? carregarArquivoVotacao(id) : carregarVotacoesDoAno(ano, casa),
    carregarIdeologia(),
    carregarPartidos(),
  ]);
  const v = doAno.votacoes.find((x) => x.id === id);
  if (!v) {
    $('#conteudo').innerHTML =
      `<h1 class="bloco-titulo">Votação não encontrada</h1><p><a href="votacoes.html${senado ? '?c=senado' : ''}">Todas as votações</a></p>`;
    return;
  }
  document.title = `${rotuloProposicao(v)} (${dataBr(v.data)}) — Votações — Congresso em Números`;
  const votos = decodificar(doAno, v);
  const leg = legislaturaEm(v.data);
  const pontos = (ideologia as Ideologia)[String(leg)] ?? {};
  const sigla = (p: string) => siglaEm(p, v.data, partidos as Record<string, Partido>);
  const deputados: (Deputado & { voto: Voto })[] = votos.map((x) => ({
    nome: x.nome,
    uf: x.uf,
    partido: x.partido,
    sigla: sigla(x.partido),
    voto: x.voto,
  }));
  const composicao = compor(deputados, pontos);
  const porPartido = placarPorPartido(votos);
  const [s, n, a, o] = v.placar;
  const art17 = votos.filter((x) => x.voto === 'Artigo 17').length;
  const linhasPartido = [...composicao.classificados, ...composicao.naoClassificados]
    .map((g) => {
      const p = porPartido.get(g.partido);
      const c = p?.contagem ?? [0, 0, 0, 0, 0];
      return `<tr><td><a href="partidos.html?p=${encodeURIComponent(g.partido)}">${esc(g.sigla)}</a></td>
        ${c
          .slice(0, 4)
          .map((x) => `<td class="num">${x || ''}</td>`)
          .join('')}
        <td class="num">${p?.rice == null ? '—' : formatarNumero(p.rice, 2)}</td></tr>`;
    })
    .join('');
  $('#conteudo').innerHTML =
    `<p class="voltar"><a href="votacoes.html?ano=${ano}${sufixoCasa}">← Votações de ${ano}</a></p>
    <h1 class="bloco-titulo">${esc(rotuloProposicao(v))} — ${dataBr(v.data)}</h1>
    ${v.pec ? '<p><span class="selo">PEC: votação de mérito em 1º ou 2º turno</span></p>' : ''}
    ${v.impeachment ? '<p><span class="selo">Impeachment: voto de cada deputado transcrito do Diário oficial</span></p>' : ''}
    ${materias(v)}
    <p><strong>Votação:</strong> ${esc(v.descricao)}</p>
    <p class="placar"><strong>${resultado(v).replace(/^./, (c) => c.toUpperCase())}</strong>
      <span><span class="amostra" style="background:var(--voto-sim)"></span>Sim ${s}</span>
      <span><span class="amostra" style="background:var(--voto-nao)"></span>Não ${n}</span>
      ${o ? `<span><span class="amostra" style="background:var(--voto-obstrucao)"></span>Obstrução ${o}</span>` : ''}
      <span><span class="amostra" style="background:var(--voto-abstencao)"></span>Abstenção ${a}</span>
      ${art17 ? `<span>${ROTULO_PRESIDENTE}: ${art17}</span>` : ''}
      ${v.ausentes ? `<span>Ausentes: ${v.ausentes}</span>` : ''}</p>
    ${avisoResultado(v)}
    <p>Orientação do Governo: <strong>${esc(orientacao(v))}</strong></p>
    <section aria-labelledby="titulo-hemi">
      <h2 class="bloco-titulo" id="titulo-hemi">Voto de cada ${parlamentar}</h2>
      <p class="bloco-dica">Partidos da esquerda para a direita pela posição ideológica da ${leg}ª legislatura; cor = voto. Ausentes não aparecem. Passe o mouse ou use as setas.</p>
      <div id="hemiciclo"></div>
      <p id="ficha" class="ficha-cadeira" aria-live="polite"></p>
      <div id="fora"></div>
      <div class="legenda">${legendaVotos()}</div>
    </section>
    <h2 class="bloco-titulo">Placar por partido</h2>
    <p class="bloco-dica">Coesão (Índice de Rice) = |Sim − Não| ÷ (Sim + Não) dentro do partido: 1 = todos votaram igual.</p>
    <div class="tabela-rolagem"><table class="ranking"><thead><tr><th scope="col">Partido</th><th scope="col">Sim</th><th scope="col">Não</th><th scope="col">Abst.</th><th scope="col">Obstr.</th><th scope="col">Coesão</th></tr></thead><tbody>${linhasPartido}</tbody></table></div>
    <h2 class="bloco-titulo">Lista nominal</h2>
    <div class="tabela-rolagem"><table class="ranking"><thead><tr><th scope="col">${senado ? 'Senador' : 'Deputado'}</th><th scope="col">Partido</th><th scope="col">UF</th><th scope="col">Voto</th></tr></thead><tbody>${[
      ...votos,
    ]
      .sort((x, y) => x.nome.localeCompare(y.nome, 'pt-BR'))
      .map(
        (x) =>
          `<tr><td>${x.id ? `<a href="deputados.html?d=${x.id}${sufixoCasa}">${esc(x.nome)}</a>` : esc(x.nome)}</td><td>${esc(sigla(x.partido))}</td><td>${esc(x.uf)}</td><td>${esc(rotuloVoto(x.voto))}</td></tr>`,
      )
      .join('')}</tbody></table></div>
    <p class="bloco-dica">Fonte: ${v.fonte ? esc(v.fonte) + '. Nomes e partidos como impressos no documento.' : senado ? `Senado Federal — Dados Abertos (votação ${esc(v.id.slice(3))}). Partido pela filiação do senador na data.` : `Câmara dos Deputados — Dados Abertos (votação ${esc(v.id)}).`}</p>`;

  const corPorVoto = (d: Deputado) => COR_VOTO[(d as Deputado & { voto: Voto }).voto];
  const desenhar = () =>
    desenharHemiciclo(
      $('#hemiciclo'),
      composicao,
      coresDasFaixas(),
      (sel) =>
        ($('#ficha').innerHTML = sel
          ? `<strong>${esc(sel.deputado.nome)}</strong> · ${esc(sel.deputado.sigla)} · ${esc(sel.deputado.uf)} — voto: ${esc(rotuloVoto((sel.deputado as Deputado & { voto: Voto }).voto))}`
          : ''),
      undefined,
      corPorVoto,
    );
  desenhar();
  const fora = composicao.naoClassificados.flatMap((g) => g.deputados);
  $('#fora').innerHTML = fora.length
    ? `<div class="nao-classificados"><span>Partidos sem posição na fonte da legislatura (fora da ordenação): ${composicao.naoClassificados.map((g) => `${esc(g.sigla)} (${g.deputados.length})`).join(', ')}</span>
      <div class="fileira-a-parte" aria-hidden="true">${fora.map((d) => `<span style="background:${corPorVoto(d)}"></span>`).join('')}</div></div>`
    : '';
  iniciarTema(desenhar);
}

async function lista(): Promise<void> {
  iniciarTema();
  const indice = await carregarIndiceVotacoes(casa);
  const anos = [...new Set(indice.map((v) => Number(v.data.slice(0, 4))))].sort((a, b) => b - a);
  const regulares = indice.filter((v) => !v.impeachment);
  const anosRegulares = [...new Set(regulares.map((v) => Number(v.data.slice(0, 4))))].sort(
    (a, b) => b - a,
  );
  const p = new URLSearchParams(location.search);
  const explicacao = senado
    ? `${regulares.length} votações nominais abertas do plenário do Senado, de ${anosRegulares.at(-1)} a ${anosRegulares[0]}. Votações secretas não têm voto individual e ficam de fora. A fonte é incompleta em alguns anos: 2015 não tem nenhuma votação cuja lista de senadores bata com os mandatos, 2016 tem 6, e 1992 e 1996–1998 poucas; 25 votações com lista incompatível com os mandatos foram retiradas (veja a Metodologia). A orientação do Governo só é registrada a partir de 2018–2019. Destaque só por critério objetivo: PEC votada em 1º ou 2º turno.`
    : `${regulares.length} votações nominais com voto registrado pela Câmara, de ${anosRegulares.at(-1)} a ${anosRegulares[0]}. Antes de dez/2001 a Câmara não publica o voto de cada deputado. Destaque só por critério objetivo: PEC em 1º ou 2º turno e autorização de impeachment (1992 e 2016, transcritos do Diário oficial).`;
  $('#conteudo').innerHTML =
    `<div class="barra-viz"><div class="visao" role="group" aria-label="Casa">
      <button type="button" data-casa="camara" aria-pressed="${!senado}">Câmara</button>
      <button type="button" data-casa="senado" aria-pressed="${senado}">Senado</button></div></div>
    <h1 class="bloco-titulo">Votações nominais do plenário ${senado ? 'do Senado' : 'da Câmara'}</h1>
    <p class="bloco-dica">${explicacao}</p>
    <form class="filtros" id="filtros" role="search">
      <label class="campo" style="flex:0 1 140px"><span class="campo-rotulo">Ano</span>
        <select name="ano"><option value="">Todos</option>${anos.map((a) => `<option>${a}</option>`).join('')}</select></label>
      <label class="campo" style="flex:1 1 240px"><span class="campo-rotulo">Buscar</span>
        <input type="search" name="q" placeholder="proposição, ementa ou texto (ex.: PEC 6/2019, previdência)"></label>
      <label class="caixa"><input type="checkbox" name="d"> só destaques (${senado ? 'PEC em 1º ou 2º turno' : 'PEC e impeachment'})</label>
      <label class="caixa"><input type="checkbox" name="g"> só com orientação Sim/Não do Governo</label>
    </form>
    <p id="contagem" class="bloco-dica" aria-live="polite"></p>
    <div class="tabela-rolagem"><table class="ranking"><thead><tr><th scope="col">Data</th><th scope="col">Proposição</th><th scope="col">O que foi votado</th><th scope="col">Resultado</th><th scope="col">Sim × Não</th><th scope="col">Governo</th></tr></thead><tbody id="linhas"></tbody></table></div>
    <p><button type="button" id="mais" class="botao-sobre" hidden>Mostrar mais</button></p>`;
  const form = $('#filtros') as HTMLFormElement;
  (form.elements.namedItem('ano') as HTMLSelectElement).value = p.get('ano') ?? String(anos[0]);
  (form.elements.namedItem('q') as HTMLInputElement).value = p.get('q') ?? '';
  (form.elements.namedItem('d') as HTMLInputElement).checked = p.get('d') === '1';
  document.querySelectorAll<HTMLButtonElement>('[data-casa]').forEach((b) =>
    b.addEventListener('click', () => {
      if (b.dataset['casa'] !== casa)
        location.search = b.dataset['casa'] === 'senado' ? '?c=senado' : '';
    }),
  );
  (form.elements.namedItem('g') as HTMLInputElement).checked = p.get('g') === '1';
  let limite = POR_PAGINA;

  const aplicar = () => {
    const f = new FormData(form);
    const ano = String(f.get('ano') ?? '');
    const q = String(f.get('q') ?? '')
      .trim()
      .toLowerCase();
    const soPec = f.get('d') === 'on';
    const soGov = f.get('g') === 'on';
    const url = new URLSearchParams();
    if (senado) url.set('c', 'senado');
    if (ano) url.set('ano', ano);
    if (q) url.set('q', q);
    if (soPec) url.set('d', '1');
    if (soGov) url.set('g', '1');
    history.replaceState(null, '', url.size ? `?${url}` : location.pathname);
    const filtradas = indice
      .filter(
        (v) =>
          (!ano || v.data.startsWith(ano)) &&
          (!soPec || v.pec || v.impeachment) &&
          (!soGov || v.orientacao_governo === 'Sim' || v.orientacao_governo === 'Não') &&
          (!q ||
            `${v.proposicoes.join(' ')} ${v.descricao} ${v.materias?.map((m) => m.ementa).join(' ') ?? ''}`
              .toLowerCase()
              .includes(q)),
      )
      .sort((a, b) => b.data.localeCompare(a.data));
    $('#contagem').textContent = `${filtradas.length} votações`;
    $('#linhas').innerHTML = filtradas
      .slice(0, limite)
      .map(
        (v) => `<tr><td class="num">${dataBr(v.data)}</td>
          <td><a href="votacoes.html?v=${encodeURIComponent(v.id)}&a=${v.data.slice(0, 4)}${sufixoCasa}">${esc(rotuloProposicao(v))}</a>${v.pec ? ' <span class="selo">PEC</span>' : ''}${v.impeachment ? ' <span class="selo">impeachment</span>' : ''}</td>
          <td>${esc(cortar(ementa(v), 180))}<br><span class="posicao-celula">${esc(cortar(v.descricao, 120))}</span></td>
          <td>${resultado(v)}</td><td class="num">${v.placar[0]} × ${v.placar[1]}</td>
          <td>${esc(v.orientacao_governo ?? '—')}</td></tr>`,
      )
      .join('');
    $('#mais').hidden = filtradas.length <= limite;
  };
  form.addEventListener('input', () => {
    limite = POR_PAGINA;
    aplicar();
  });
  form.addEventListener('submit', (e) => e.preventDefault());
  $('#mais').addEventListener('click', () => {
    limite += POR_PAGINA;
    aplicar();
  });
  aplicar();
}

const p = new URLSearchParams(location.search);
const id = p.get('v');
(id ? detalhe(id, Number(p.get('a') ?? id.slice(0, 4))) : lista())
  .then(() => (document.body.dataset['pronto'] = 'true'))
  .catch((erro: unknown) => {
    console.error(erro);
    $('#erro').hidden = false;
  });
