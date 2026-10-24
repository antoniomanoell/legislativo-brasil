// O Congresso a partir de 1º/fev/2027 (58ª legislatura): Câmara com os 513 eleitos de 2026 e
// Senado com os 54 eleitos de 2026 mais as 27 cadeiras com mandato até 2031 (DECISIONS 2026-10-24).
// Composição prevista, não definitiva: depende do 2º turno, da diplomação e de trocas de partido.

import '../design/mapa.css';
import '../design/congresso.css';
import { desenharHemiciclo } from '../charts/hemiciclo-svg';
import { compor, type Composicao } from '../composicao';
import {
  carregarCongresso2027,
  carregarIdeologia,
  type Deputado,
  type Pontuacao,
  type Senador2027,
} from '../dados';
import { iniciarTema } from '../design/tema';
import { esc, pct } from '../formato';
import { coresDasFaixas, corDe, descrever, FAIXAS, linhaDeFonte, nomeFonte } from '../ideologia';
import { mostrarAtualizacao } from '../atualizacao';

const $ = (sel: string) => document.querySelector(sel) as HTMLElement;

function dataBr(iso: string): string {
  return iso.split('-').reverse().join('/');
}

interface Casa {
  id: 'camara' | 'senado';
  nome: string;
  membros: Deputado[];
  composicao: Composicao;
}

/** Cadeiras por faixa ideológica (só as faixas dos autores; não classificados à parte). */
function porFaixa(c: Composicao): number[] {
  const n = FAIXAS.map(() => 0);
  for (const g of c.classificados) {
    const i = FAIXAS.indexOf(g.pontuacao?.faixa as (typeof FAIXAS)[number]);
    if (i >= 0) n[i] = (n[i] ?? 0) + g.deputados.length;
  }
  return n;
}

function barraFaixas(c: Composicao, total: number): string {
  const cores = coresDasFaixas();
  const n = porFaixa(c);
  const fora = c.naoClassificados.reduce((s, g) => s + g.deputados.length, 0);
  const segmentos = n
    .map((v, i) =>
      v ? `<span style="flex:${v};background:${cores[i]}" title="${FAIXAS[i]}: ${v}"></span>` : '',
    )
    .join('');
  const linhas = n
    .map((v, i) =>
      v
        ? `<tr><td><span class="amostra" style="background:${cores[i]}" aria-hidden="true"></span>${FAIXAS[i]}</td><td class="num">${v}</td><td class="num">${pct(v, total)}</td></tr>`
        : '',
    )
    .join('');
  return `<div class="barra-faixas" aria-hidden="true">${segmentos}${fora ? `<span class="amostra-hachura" style="flex:${fora}"></span>` : ''}</div>
    <table class="ranking tabela-faixas"><caption class="so-leitor">Cadeiras por faixa ideológica do partido</caption>
    <thead><tr><th scope="col">Faixa</th><th scope="col">Cadeiras</th><th scope="col">%</th></tr></thead>
    <tbody>${linhas}${fora ? `<tr><td><span class="amostra amostra-hachura" aria-hidden="true"></span>não classificado</td><td class="num">${fora}</td><td class="num">${pct(fora, total)}</td></tr>` : ''}</tbody></table>`;
}

function tabelaPartidos(casa: Casa): string {
  const cores = coresDasFaixas();
  const total = casa.membros.length;
  const linhas = [...casa.composicao.classificados, ...casa.composicao.naoClassificados]
    .map((g) => {
      const corCss = g.pontuacao ? `background:${corDe(g.pontuacao, cores)}` : '';
      const classe = g.pontuacao ? 'cor-partido' : 'cor-partido amostra-hachura';
      return `<tr><td><span class="${classe}" style="${corCss}" aria-hidden="true"></span><a href="partidos.html?p=${encodeURIComponent(g.partido)}">${esc(g.sigla)}</a></td>
        <td class="num">${g.deputados.length}</td><td class="num">${pct(g.deputados.length, total)}</td>
        <td class="posicao-celula">${esc(descrever(g.pontuacao))}</td></tr>`;
    })
    .join('');
  return `<details class="detalhes-partidos"><summary>Cadeiras por partido</summary><div class="tabela-rolagem"><table class="ranking">
    <caption class="so-leitor">${esc(casa.nome)} a partir de 2027: cadeiras por partido, da esquerda para a direita</caption>
    <thead><tr><th scope="col">Partido</th><th scope="col">Cadeiras</th><th scope="col">%</th><th scope="col">Posição</th></tr></thead>
    <tbody>${linhas}</tbody></table></div></details>`;
}

function foraDaOrdem(c: Composicao): string {
  if (!c.naoClassificados.length) return '';
  const n = c.naoClassificados.reduce((s, g) => s + g.deputados.length, 0);
  const lista = c.naoClassificados.map((g) => `${esc(g.sigla)} (${g.deputados.length})`).join(', ');
  return `<div class="nao-classificados"><span>Não classificados, fora da ordenação: ${n} — ${lista}</span>
    <div class="fileira-a-parte" aria-hidden="true">${'<span class="amostra-hachura"></span>'.repeat(n)}</div></div>`;
}

/** As 27 cadeiras do Senado que não estavam em disputa em 2026, com as notas. */
function tabelaContinuam(senado: Senador2027[], posicao: string): string {
  const linhas = senado
    .filter((s) => s.origem === 'mandato_ate_2031')
    .sort((a, b) => a.uf.localeCompare(b.uf))
    .map(
      (s) =>
        `<tr><td>${esc(s.uf)}</td><td>${esc(s.nome)}</td><td>${esc(s.sigla)}</td><td class="posicao-celula">${esc(s.nota ?? '')}</td></tr>`,
    )
    .join('');
  return `<details class="detalhes-partidos"><summary>As 27 cadeiras com mandato até 2031</summary>
    <p class="bloco-dica">Eleitas em 2022. Em cada uma, quem a ocupava em ${dataBr(posicao)} pelos registros do Senado, com o partido da filiação registrada nessa data.</p>
    <div class="tabela-rolagem"><table class="ranking"><thead><tr><th scope="col">UF</th><th scope="col">Senador</th><th scope="col">Partido</th><th scope="col">Observação</th></tr></thead>
    <tbody>${linhas}</tbody></table></div></details>`;
}

function secao(casa: Casa, extra: string): string {
  const total = casa.membros.length;
  const maior = [...casa.composicao.classificados, ...casa.composicao.naoClassificados].sort(
    (a, b) => b.deputados.length - a.deputados.length,
  )[0];
  const nPartidos = casa.composicao.classificados.length + casa.composicao.naoClassificados.length;
  return `<section class="bloco" aria-labelledby="titulo-${casa.id}">
    <div class="bloco-cabeca"><h2 class="bloco-titulo" id="titulo-${casa.id}">${esc(casa.nome)} — ${total} cadeiras</h2>
    <p class="bloco-dica">${nPartidos} partidos; maior bancada: ${esc(maior?.sigla ?? '—')} (${maior?.deputados.length ?? 0}). Passe o mouse ou toque numa cadeira; no teclado, use as setas.</p></div>
    <div id="hemiciclo-${casa.id}"></div>
    <p id="ficha-${casa.id}" class="ficha-cadeira" aria-live="polite"></p>
    ${foraDaOrdem(casa.composicao)}
    <h3 class="subtitulo-2027">Por faixa ideológica do partido</h3>
    ${barraFaixas(casa.composicao, total)}
    ${tabelaPartidos(casa)}
    ${extra}
  </section>`;
}

async function iniciar(): Promise<void> {
  const [dados, ideologia] = await Promise.all([carregarCongresso2027(), carregarIdeologia()]);
  const pontos: Record<string, Pontuacao> = ideologia[String(dados.legislatura)] ?? {};
  const casas: Casa[] = [
    {
      id: 'camara',
      nome: 'Câmara dos Deputados',
      membros: dados.camara,
      composicao: compor(dados.camara, pontos),
    },
    {
      id: 'senado',
      nome: 'Senado Federal',
      membros: dados.senado,
      composicao: compor(dados.senado, pontos),
    },
  ];
  const p0 = Object.values(pontos)[0];
  const cores = coresDasFaixas();
  const legenda = `<div class="legenda"><p class="legenda-titulo">${p0 ? `Posição: ${esc(nomeFonte(p0))}` : ''}</p><ul>${FAIXAS.map(
    (f, i) =>
      `<li><span class="amostra" style="background:${cores[i]}" aria-hidden="true"></span>${f}</li>`,
  ).join(
    '',
  )}<li><span class="amostra amostra-hachura" aria-hidden="true"></span>não classificado</li></ul></div>`;

  $('#conteudo').innerHTML = `<section class="bloco">
      <h1 class="bloco-titulo">O Congresso a partir de 1º de fevereiro de 2027</h1>
      <p>Composição prevista da ${dados.legislatura}ª legislatura. Na Câmara, os 513 deputados eleitos em 2026. No Senado, os 54 eleitos em 2026 (duas vagas por UF) e as 27 cadeiras eleitas em 2022, com mandato até 2031.</p>
      <p class="aviso-lacuna">É uma previsão, não a composição definitiva. Os eleitos seguem a situação atual no TSE e podem mudar até a diplomação (candidaturas em recurso). O partido é o da eleição (eleitos de 2026) ou o da filiação registrada pelo Senado em ${dataBr(dados.posicao_em)} (cadeiras até 2031); trocas de partido até a posse não aparecem. Senadores eleitos governador saem e entram os suplentes; o 2º turno de 25/10/2026 ainda pode mudar duas cadeiras (veja a lista do Senado). ${esc(linhaDeFonte(Object.values(pontos)))}</p>
      ${legenda}
    </section>
    ${secao(casas[0] as Casa, '')}
    ${secao(casas[1] as Casa, tabelaContinuam(dados.senado, dados.posicao_em))}`;

  const desenhar = () => {
    for (const casa of casas) {
      desenharHemiciclo($(`#hemiciclo-${casa.id}`), casa.composicao, coresDasFaixas(), (sel) => {
        const ficha = $(`#ficha-${casa.id}`);
        if (!sel) {
          ficha.innerHTML = '';
          return;
        }
        const d = sel.deputado as Deputado & Partial<Senador2027>;
        const origem =
          d.origem === 'mandato_ate_2031'
            ? ' · mandato até 2031'
            : d.origem === 'eleito_2026'
              ? ' · eleito em 2026'
              : '';
        ficha.innerHTML = `<strong>${esc(d.nome)}</strong> · ${esc(d.sigla)} · ${esc(d.uf)}${origem} — ${esc(descrever(pontos[d.partido]))}${d.nota ? `<br><span class="posicao-celula">${esc(d.nota)}</span>` : ''}`;
      });
    }
  };
  desenhar();
  iniciarTema(desenhar);
  document.body.dataset['pronto'] = 'true';
}

void mostrarAtualizacao(['congresso_2027']);
iniciar().catch((erro: unknown) => {
  console.error(erro);
  $('#erro').hidden = false;
});
