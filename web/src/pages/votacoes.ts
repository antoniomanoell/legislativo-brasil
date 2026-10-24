// Votações (PROJECT.md, 4.1.6): lista filtrável das votações nominais do plenário (2001 em diante)
// e, em ?v=<id>&a=<ano>, a votação com placar por partido, orientação do Governo e hemiciclo
// colorido pelo voto. Destaques só por critério objetivo (§7.7): PEC em 1º/2º turno.

import '../design/mapa.css';
import '../design/congresso.css';
import { desenharHemiciclo } from '../charts/hemiciclo-svg';
import { compor } from '../composicao';
import {
  carregarIdeologia,
  carregarIndiceVotacoes,
  carregarPartidos,
  carregarVotacoesDoAno,
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
    ['Artigo 17', 'Artigo 17 (presidente da sessão)'],
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
    carregarVotacoesDoAno(ano),
    carregarIdeologia(),
    carregarPartidos(),
  ]);
  const v = doAno.votacoes.find((x) => x.id === id);
  if (!v) {
    $('#conteudo').innerHTML =
      `<h1 class="bloco-titulo">Votação não encontrada</h1><p><a href="votacoes.html">Todas as votações</a></p>`;
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
    `<p class="voltar"><a href="votacoes.html?ano=${ano}">← Votações de ${ano}</a></p>
    <h1 class="bloco-titulo">${esc(rotuloProposicao(v))} — ${dataBr(v.data)}</h1>
    ${v.pec ? '<p><span class="selo">PEC: votação de mérito em 1º ou 2º turno</span></p>' : ''}
    <p>${esc(v.descricao)}</p>
    <p class="placar"><strong>${v.aprovada ? 'Aprovada' : 'Rejeitada'}</strong>
      <span><span class="amostra" style="background:var(--voto-sim)"></span>Sim ${s}</span>
      <span><span class="amostra" style="background:var(--voto-nao)"></span>Não ${n}</span>
      <span><span class="amostra" style="background:var(--voto-obstrucao)"></span>Obstrução ${o}</span>
      <span><span class="amostra" style="background:var(--voto-abstencao)"></span>Abstenção ${a}</span>
      ${art17 ? `<span>Artigo 17: ${art17}</span>` : ''}</p>
    <p>Orientação do Governo: <strong>${esc(orientacao(v))}</strong></p>
    <section aria-labelledby="titulo-hemi">
      <h2 class="bloco-titulo" id="titulo-hemi">Voto de cada deputado</h2>
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
    <div class="tabela-rolagem"><table class="ranking"><thead><tr><th scope="col">Deputado</th><th scope="col">Partido</th><th scope="col">UF</th><th scope="col">Voto</th></tr></thead><tbody>${[
      ...votos,
    ]
      .sort((x, y) => x.nome.localeCompare(y.nome, 'pt-BR'))
      .map(
        (x) =>
          `<tr><td><a href="deputados.html?d=${x.id}">${esc(x.nome)}</a></td><td>${esc(sigla(x.partido))}</td><td>${esc(x.uf)}</td><td>${esc(x.voto)}</td></tr>`,
      )
      .join('')}</tbody></table></div>
    <p class="bloco-dica">Fonte: Câmara dos Deputados — Dados Abertos (votação ${esc(v.id)}).</p>`;

  const corPorVoto = (d: Deputado) => COR_VOTO[(d as Deputado & { voto: Voto }).voto];
  const desenhar = () =>
    desenharHemiciclo(
      $('#hemiciclo'),
      composicao,
      coresDasFaixas(),
      (sel) =>
        ($('#ficha').innerHTML = sel
          ? `<strong>${esc(sel.deputado.nome)}</strong> · ${esc(sel.deputado.sigla)} · ${esc(sel.deputado.uf)} — voto: ${esc((sel.deputado as Deputado & { voto: Voto }).voto)}`
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
  const indice = await carregarIndiceVotacoes();
  const anos = [...new Set(indice.map((v) => Number(v.data.slice(0, 4))))].sort((a, b) => b - a);
  const p = new URLSearchParams(location.search);
  $('#conteudo').innerHTML = `<h1 class="bloco-titulo">Votações nominais do plenário</h1>
    <p class="bloco-dica">${indice.length} votações nominais de ${anos.at(-1)} a ${anos[0]}. Antes de dez/2001 a Câmara não publica o voto de cada deputado. Destaque só por critério objetivo: PEC em 1º ou 2º turno.</p>
    <form class="filtros" id="filtros" role="search">
      <label class="campo" style="flex:0 1 140px"><span class="campo-rotulo">Ano</span>
        <select name="ano"><option value="">Todos</option>${anos.map((a) => `<option>${a}</option>`).join('')}</select></label>
      <label class="campo" style="flex:1 1 240px"><span class="campo-rotulo">Buscar</span>
        <input type="search" name="q" placeholder="proposição ou texto (ex.: PEC 6/2019)"></label>
      <label class="caixa"><input type="checkbox" name="d"> só destaques (PEC)</label>
      <label class="caixa"><input type="checkbox" name="g"> só com orientação Sim/Não do Governo</label>
    </form>
    <p id="contagem" class="bloco-dica" aria-live="polite"></p>
    <div class="tabela-rolagem"><table class="ranking"><thead><tr><th scope="col">Data</th><th scope="col">Proposição</th><th scope="col">Descrição</th><th scope="col">Resultado</th><th scope="col">Sim × Não</th><th scope="col">Governo</th></tr></thead><tbody id="linhas"></tbody></table></div>
    <p><button type="button" id="mais" class="botao-sobre" hidden>Mostrar mais</button></p>`;
  const form = $('#filtros') as HTMLFormElement;
  (form.elements.namedItem('ano') as HTMLSelectElement).value = p.get('ano') ?? String(anos[0]);
  (form.elements.namedItem('q') as HTMLInputElement).value = p.get('q') ?? '';
  (form.elements.namedItem('d') as HTMLInputElement).checked = p.get('d') === '1';
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
    if (ano) url.set('ano', ano);
    if (q) url.set('q', q);
    if (soPec) url.set('d', '1');
    if (soGov) url.set('g', '1');
    history.replaceState(null, '', url.size ? `?${url}` : location.pathname);
    const filtradas = indice
      .filter(
        (v) =>
          (!ano || v.data.startsWith(ano)) &&
          (!soPec || v.pec) &&
          (!soGov || v.orientacao_governo === 'Sim' || v.orientacao_governo === 'Não') &&
          (!q || `${v.proposicoes.join(' ')} ${v.descricao}`.toLowerCase().includes(q)),
      )
      .sort((a, b) => b.data.localeCompare(a.data));
    $('#contagem').textContent = `${filtradas.length} votações`;
    $('#linhas').innerHTML = filtradas
      .slice(0, limite)
      .map(
        (v) => `<tr><td class="num">${dataBr(v.data)}</td>
          <td><a href="votacoes.html?v=${encodeURIComponent(v.id)}&a=${v.data.slice(0, 4)}">${esc(rotuloProposicao(v))}</a>${v.pec ? ' <span class="selo">PEC</span>' : ''}</td>
          <td class="posicao-celula">${esc(v.descricao.slice(0, 140))}${v.descricao.length > 140 ? '…' : ''}</td>
          <td>${v.aprovada ? 'aprovada' : 'rejeitada'}</td><td class="num">${v.placar[0]} × ${v.placar[1]}</td>
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
