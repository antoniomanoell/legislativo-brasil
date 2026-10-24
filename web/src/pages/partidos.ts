// Partidos (PROJECT.md, 4.1.3), versão básica da Fase 1: lista de partidos com bancada e, em
// ?p=<id>, a ficha com linhagem, cadeiras por momento e posição ideológica por legislatura.

import '../design/mapa.css';
import '../design/congresso.css';
import {
  carregarAgregados,
  carregarCatalogo,
  carregarIdeologia,
  carregarPartidos,
  type Agregados,
  type Catalogo,
  type Ideologia,
  type Partido,
} from '../dados';
import { iniciarTema } from '../design/tema';
import { esc, formatarNumero } from '../formato';
import { nomeFonte } from '../ideologia';
import { mostrarAtualizacao } from '../atualizacao';

const $ = (sel: string) => document.querySelector(sel) as HTMLElement;

function data(iso: string): string {
  return iso.length === 10 ? iso.split('-').reverse().join('/') : iso;
}

function link(id: string, partidos: Record<string, Partido>): string {
  const p = partidos[id];
  return `<a href="partidos.html?p=${encodeURIComponent(id)}">${esc(p ? `${p.sigla} — ${p.nome}` : id)}</a>`;
}

function lista(cat: Catalogo, agregados: Agregados, partidos: Record<string, Partido>): string {
  const presenca = new Map<string, { primeiro: number; ultimo: number; maximo: number }>();
  for (const m of cat.momentos) {
    for (const [id, n] of Object.entries(agregados[m.id] ?? {})) {
      const atual = presenca.get(id) ?? { primeiro: m.ano, ultimo: m.ano, maximo: 0 };
      atual.primeiro = Math.min(atual.primeiro, m.ano);
      atual.ultimo = Math.max(atual.ultimo, m.ano);
      atual.maximo = Math.max(atual.maximo, n);
      presenca.set(id, atual);
    }
  }
  const linhas = [...presenca.entries()]
    .sort((a, b) =>
      (partidos[a[0]]?.sigla ?? a[0]).localeCompare(partidos[b[0]]?.sigla ?? b[0], 'pt-BR'),
    )
    .map(
      ([id, p]) =>
        `<tr><td>${link(id, partidos)}</td><td class="num">${p.primeiro}${p.ultimo !== p.primeiro ? `–${p.ultimo}` : ''}</td><td class="num">${p.maximo}</td></tr>`,
    )
    .join('');
  return `<h1 class="bloco-titulo">Partidos com bancada na Câmara</h1>
    <p class="bloco-dica">Partidos com ao menos uma cadeira entre os eleitos (1990–2026) ou nas fotos de 1º de fevereiro (2003–2026). Um partido renomeado é o mesmo partido; fusões criam partido novo.</p>
    <div class="tabela-rolagem"><table class="ranking">
    <thead><tr><th scope="col">Partido (sigla e nome atuais)</th><th scope="col">Com bancada</th><th scope="col">Maior bancada</th></tr></thead>
    <tbody>${linhas}</tbody></table></div>`;
}

function ficha(
  id: string,
  cat: Catalogo,
  agregados: Agregados,
  ideologia: Ideologia,
  partidos: Record<string, Partido>,
): string {
  const p = partidos[id];
  if (!p)
    return `<h1 class="bloco-titulo">Partido não encontrado</h1><p><a href="partidos.html">Ver todos</a></p>`;
  document.title = `${p.sigla} — Partidos — Congresso em Números`;

  const nao = (c: string) =>
    c === 'sim' ? '' : ' <span class="selo">sem registro no TSE; a confirmar</span>';
  const eventos = [
    ...p.origem.map(
      (o) =>
        `<li>${esc(data(o.data))}: ${esc(o.tipo)} — recebeu ${link(o.partido, partidos)}${nao(o.confirmado_no_tse)}</li>`,
    ),
    ...p.renomeacoes.map(
      (r) =>
        `<li>${esc(data(r.data))}: mudança de nome/sigla, de ${esc(r.sigla_anterior)} para ${esc(r.sigla_nova)}</li>`,
    ),
    ...p.destino.map(
      (d) =>
        `<li>${esc(data(d.data))}: ${esc(d.tipo)} em ${link(d.partido, partidos)}${nao(d.confirmado_no_tse)}</li>`,
    ),
  ].sort();

  const cadeiras = (tipo: 'eleitos' | 'exercicio') =>
    cat.momentos
      .filter((m) => m.tipo === tipo && agregados[m.id]?.[id])
      .map(
        (m) =>
          `<tr><td>${esc(m.rotulo)}</td><td class="num">${agregados[m.id]?.[id]}</td><td class="num">${m.cadeiras}</td></tr>`,
      )
      .join('');
  const tabelaCadeiras = (titulo: string, linhas: string) =>
    linhas
      ? `<h3>${titulo}</h3><table class="ranking"><thead><tr><th scope="col">Momento</th><th scope="col">Cadeiras</th><th scope="col">Total da Câmara</th></tr></thead><tbody>${linhas}</tbody></table>`
      : '';

  const posicoes = Object.entries(ideologia)
    .filter(([, pontos]) => pontos[id])
    .map(([leg, pontos]) => {
      const x = pontos[id];
      if (!x) return '';
      const casas = x.fonte_id === 'bls' ? 2 : 1;
      const erro =
        x.erro_padrao !== null ? ` (erro-padrão ${formatarNumero(x.erro_padrao, 3)})` : '';
      return `<tr><td>${leg}ª</td><td>${esc(nomeFonte(x))} — sigla na fonte: ${esc(x.sigla_fonte)}</td>
        <td class="num">${formatarNumero(x.pontuacao, casas)}${erro}</td><td>${x.faixa ? esc(x.faixa) : '—'}</td>
        <td class="posicao-celula">${x.nota ? esc(x.nota) : ''}</td></tr>`;
    })
    .join('');
  const legislaturasComBancada = new Set(
    cat.momentos.filter((m) => agregados[m.id]?.[id]).map((m) => String(m.legislatura)),
  );
  const semMedicao = [...legislaturasComBancada].filter((l) => !ideologia[l]?.[id]).sort();

  return `<p class="voltar"><a href="partidos.html">← Todos os partidos</a></p>
    <h1 class="bloco-titulo">${esc(p.sigla)} — ${esc(p.nome)}</h1>
    ${p.observacao ? `<p class="bloco-dica">${esc(p.observacao)}</p>` : ''}
    <h2>Linhagem</h2>
    ${eventos.length ? `<ul>${eventos.join('')}</ul>` : '<p>Sem fusões, incorporações ou mudanças de nome registradas.</p>'}
    <p class="bloco-dica">Fonte: TSE, "Partidos políticos registrados" (eventos a partir de 1995).</p>
    <h2>Posição ideológica por legislatura</h2>
    ${posicoes ? `<div class="tabela-rolagem"><table class="ranking"><thead><tr><th scope="col">Legislatura</th><th scope="col">Fonte</th><th scope="col">Pontuação</th><th scope="col">Faixa</th><th scope="col">Nota</th></tr></thead><tbody>${posicoes}</tbody></table></div>` : '<p>Sem medição nas fontes usadas.</p>'}
    ${semMedicao.length ? `<p class="aviso-lacuna">Não classificado nas legislaturas ${semMedicao.map((l) => `${l}ª`).join(', ')}: a fonte daquela legislatura não mediu este partido.</p>` : ''}
    <p class="bloco-dica">A BLS usa uma escala de −1 (esquerda) a +1 (direita) e não publica faixas (—); Bolognesi et al. usam 0 a 10, com faixas. As duas escalas não são comparáveis entre si. <a href="metodologia.html">Metodologia</a></p>
    <h2>Cadeiras</h2>
    ${tabelaCadeiras('Eleitos', cadeiras('eleitos'))}
    ${tabelaCadeiras('Em exercício em 1º de fevereiro', cadeiras('exercicio'))}`;
}

async function iniciar(): Promise<void> {
  iniciarTema();
  const [cat, agregados, ideologia, partidos] = await Promise.all([
    carregarCatalogo(),
    carregarAgregados(),
    carregarIdeologia(),
    carregarPartidos(),
  ]);
  const id = new URLSearchParams(location.search).get('p');
  $('#conteudo').innerHTML = id
    ? ficha(id, cat, agregados, ideologia, partidos)
    : lista(cat, agregados, partidos);
  document.body.dataset['pronto'] = 'true';
}

void mostrarAtualizacao(['composicao_camara', 'votacoes_camara', 'governos']);
iniciar().catch((erro: unknown) => {
  console.error(erro);
  $('#erro').hidden = false;
});
