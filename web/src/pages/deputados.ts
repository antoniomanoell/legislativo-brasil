// Deputados (PROJECT.md, 4.1.4): busca e perfil com partidos ao longo do tempo, presença e
// governismo por legislatura e por governo (DECISIONS A3, A8) e os votos nominais, por ano.
// Dados de votação só de dez/2001 em diante na Câmara; com ?c=senado, os senadores (1991 em diante).

import '../design/mapa.css';
import '../design/congresso.css';
import {
  carregarGovernos,
  carregarIndicadores,
  carregarPartidos,
  carregarVotacoesDoAno,
  casaDaUrl,
  type IndicadoresDeputado,
  type Partido,
} from '../dados';
import { iniciarTema } from '../design/tema';
import { esc, formatarNumero } from '../formato';
import { siglaEm } from '../siglas';
import { VOTO } from '../votos';

const $ = (sel: string) => document.querySelector(sel) as HTMLElement;
const casa = casaDaUrl();
const senado = casa === 'senado';
const sufixoCasa = senado ? '&c=senado' : '';
const NOME = senado
  ? { um: 'Senador', varios: 'Senadores', buscar: 'Buscar senador' }
  : { um: 'Deputado', varios: 'Deputados', buscar: 'Buscar deputado' };
const paginaBusca = `deputados.html${senado ? '?c=senado' : ''}`;

const pctOuTraco = (x: number | undefined) =>
  x === undefined ? '—' : `${formatarNumero(100 * x, 1)}%`;

function dataBr(iso: string): string {
  return iso.slice(0, 10).split('-').reverse().join('/');
}

function semAcento(s: string): string {
  return s
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .toLowerCase();
}

async function perfil(id: string): Promise<void> {
  const [ind, partidos, governos] = await Promise.all([
    carregarIndicadores(casa),
    carregarPartidos(),
    carregarGovernos(),
  ]);
  const d = ind.deputados[id];
  if (!d) {
    $('#conteudo').innerHTML =
      `<h1 class="bloco-titulo">${NOME.um} não encontrado</h1><p><a href="${paginaBusca}">Buscar</a></p>`;
    return;
  }
  document.title = `${d.nome} — ${NOME.varios} — Congresso em Números`;
  const sigla = (p: string, data: string) => siglaEm(p, data, partidos as Record<string, Partido>);
  const filiacoes = d.partidos
    .map(
      ([p, de, ate]) =>
        `<li><a href="partidos.html?p=${encodeURIComponent(p)}">${esc(sigla(p, de))}</a> — votos de ${dataBr(de)} a ${dataBr(ate)}</li>`,
    )
    .join('');
  const legs = Object.entries(d.legislaturas ?? {})
    .sort((a, b) => Number(a[0]) - Number(b[0]))
    .map(
      ([leg, x]) =>
        `<tr><td>${leg}ª</td><td class="num">${pctOuTraco(x.presenca)}</td><td class="num">${x.votacoes_esperadas ?? '—'}</td><td class="num">${pctOuTraco(x.governismo)}</td><td class="num">${x.votos ?? '—'}</td></tr>`,
    )
    .join('');
  const nomeGoverno = (g: string) => {
    const x = governos.governos.find((y) => y.governo_id === g);
    return x ? `${x.presidente} (${x.inicio.slice(0, 4)}–${x.fim.slice(0, 4)})` : g;
  };
  const govs = Object.entries(d.governos ?? {})
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(
      ([g, x]) =>
        `<tr><td>${esc(nomeGoverno(g))}</td><td class="num">${pctOuTraco(x.governismo)}</td><td class="num">${x.votos}</td></tr>`,
    )
    .join('');
  const anos = [
    ...new Set(
      d.partidos.flatMap(([, de, ate]) => {
        const lista: number[] = [];
        for (let a = Number(de.slice(0, 4)); a <= Number(ate.slice(0, 4)); a++) lista.push(a);
        return lista;
      }),
    ),
  ].sort((a, b) => b - a);

  $('#conteudo').innerHTML = `<p class="voltar"><a href="${paginaBusca}">← ${NOME.buscar}</a></p>
    <h1 class="bloco-titulo">${esc(d.nome)} — ${esc(d.uf)}</h1>
    <h2>Partidos (${senado ? 'pela filiação na data de cada voto' : 'pelo registro nos votos'})</h2><ul>${filiacoes}</ul>
    <h2>Presença e governismo por legislatura</h2>
    <p class="bloco-dica">${senado ? 'Presença: votações abertas em que registrou voto ÷ votações em que foi listado, menos licenças e ausências a serviço do Senado (presidente da sessão não conta).' : 'Presença: votações nominais em que registrou voto ÷ votações ocorridas enquanto estava em exercício ("Artigo 17" não conta).'} Governismo: votos iguais à orientação do Governo ÷ votos Sim, Não, Abstenção e Obstrução, só quando o Governo orientou Sim ou Não${senado ? ' (no Senado, registrado só de 2018–2019 em diante)' : ''}. <a href="metodologia.html">Metodologia</a></p>
    <div class="tabela-rolagem"><table class="ranking"><thead><tr><th scope="col">Legislatura</th><th scope="col">Presença</th><th scope="col">Votações esperadas</th><th scope="col">Governismo</th><th scope="col">Votos considerados</th></tr></thead><tbody>${legs || '<tr><td colspan="5">Sem votações nominais registradas.</td></tr>'}</tbody></table></div>
    ${govs ? `<h2>Governismo por governo</h2><div class="tabela-rolagem"><table class="ranking"><thead><tr><th scope="col">Governo</th><th scope="col">Governismo</th><th scope="col">Votos considerados</th></tr></thead><tbody>${govs}</tbody></table></div>` : ''}
    <h2>Votos</h2>
    <label class="campo" style="max-width:200px"><span class="campo-rotulo">Ano</span><select id="ano-votos">${anos.map((a) => `<option>${a}</option>`).join('')}</select></label>
    <div class="tabela-rolagem" id="votos"></div>
    <p class="bloco-dica">Fonte: ${senado ? 'Senado Federal' : 'Câmara dos Deputados'} — Dados Abertos (${senado ? 'código' : 'id'} ${esc(id)}).</p>`;

  const mostrarAno = async (ano: number) => {
    const doAno = await carregarVotacoesDoAno(ano, casa);
    const i = doAno.deputados.findIndex(([x]) => String(x) === id);
    const linhas = doAno.votacoes
      .filter((v) => i >= 0 && VOTO[v.v[i] as string])
      .reverse()
      .map(
        (v) =>
          `<tr><td class="num">${dataBr(v.data)}</td><td><a href="votacoes.html?v=${encodeURIComponent(v.id)}&a=${ano}${sufixoCasa}">${esc(v.proposicoes.join(', ') || 'Votação')}</a></td>
            <td>${esc(senado && v.v[i] === '7' ? 'Presidente (art. 51 RISF)' : (VOTO[v.v[i] as string] ?? ''))}</td><td>${esc(v.orientacao_governo ?? '—')}</td></tr>`,
      )
      .join('');
    $('#votos').innerHTML =
      `<table class="ranking"><thead><tr><th scope="col">Data</th><th scope="col">Proposição</th><th scope="col">Voto</th><th scope="col">Orientação do Governo</th></tr></thead><tbody>${linhas || '<tr><td colspan="4">Nenhum voto neste ano.</td></tr>'}</tbody></table>`;
  };
  const sel = $('#ano-votos') as HTMLSelectElement;
  sel.addEventListener('change', () => void mostrarAno(Number(sel.value)));
  if (anos[0]) await mostrarAno(anos[0]);
}

async function busca(): Promise<void> {
  const [ind, partidos] = await Promise.all([carregarIndicadores(casa), carregarPartidos()]);
  const lista = Object.entries(ind.deputados) as [string, IndicadoresDeputado][];
  $('#conteudo').innerHTML =
    `<div class="barra-viz"><div class="visao" role="group" aria-label="Casa">
      <button type="button" data-casa="camara" aria-pressed="${!senado}">Câmara</button>
      <button type="button" data-casa="senado" aria-pressed="${senado}">Senado</button></div></div>
    <h1 class="bloco-titulo">${NOME.varios}</h1>
    <p class="bloco-dica">${senado ? `${lista.length} senadores listados em votações abertas do plenário de 1991 em diante.` : `${lista.length} deputados com voto nominal registrado de dez/2001 em diante.`}</p>
    <form class="filtros" role="search"><label class="campo" style="flex:1 1 280px"><span class="campo-rotulo">Buscar</span>
      <input type="search" id="q" placeholder="nome, UF ou partido" autocomplete="off"></label></form>
    <p id="contagem" class="bloco-dica" aria-live="polite"></p>
    <div class="tabela-rolagem"><table class="ranking"><thead><tr><th scope="col">Nome</th><th scope="col">UF</th><th scope="col">Partidos</th><th scope="col">Legislaturas</th></tr></thead><tbody id="linhas"></tbody></table></div>`;
  const q = $('#q') as HTMLInputElement;
  q.value = new URLSearchParams(location.search).get('q') ?? '';
  document.querySelectorAll<HTMLButtonElement>('[data-casa]').forEach((b) =>
    b.addEventListener('click', () => {
      if (b.dataset['casa'] !== casa)
        location.search = b.dataset['casa'] === 'senado' ? '?c=senado' : '';
    }),
  );
  const aplicar = () => {
    const termo = semAcento(q.value.trim());
    const url = new URLSearchParams();
    if (senado) url.set('c', 'senado');
    if (termo) url.set('q', q.value.trim());
    history.replaceState(null, '', url.size ? `?${url}` : location.pathname);
    const achados = lista
      .map(([id, d]) => {
        const siglas = [...new Set(d.partidos.map(([p, de]) => siglaEm(p, de, partidos)))];
        return { id, d, siglas };
      })
      .filter(
        ({ d, siglas }) =>
          !termo || semAcento(`${d.nome} ${d.uf} ${siglas.join(' ')}`).includes(termo),
      )
      .sort((a, b) => a.d.nome.localeCompare(b.d.nome, 'pt-BR'));
    $('#contagem').textContent = `${achados.length} ${NOME.varios.toLowerCase()}`;
    $('#linhas').innerHTML = achados
      .slice(0, 200)
      .map(
        ({ id, d, siglas }) =>
          `<tr><td><a href="deputados.html?d=${id}${sufixoCasa}">${esc(d.nome)}</a></td><td>${esc(d.uf)}</td><td>${esc(siglas.join(', '))}</td><td>${Object.keys(
            d.legislaturas ?? {},
          )
            .map((l) => `${l}ª`)
            .join(', ')}</td></tr>`,
      )
      .join('');
  };
  q.addEventListener('input', aplicar);
  aplicar();
}

iniciarTema();
const idDeputado = new URLSearchParams(location.search).get('d');
(idDeputado ? perfil(idDeputado) : busca())
  .then(() => (document.body.dataset['pronto'] = 'true'))
  .catch((erro: unknown) => {
    console.error(erro);
    $('#erro').hidden = false;
  });
