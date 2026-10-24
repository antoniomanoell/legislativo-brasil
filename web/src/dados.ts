// Tipos e carregamento dos JSON gerados pelo pipeline (pipeline/src/congresso/load/site.py).

export type TipoMomento = 'eleitos' | 'exercicio';
export type Casa = 'camara' | 'senado';

/** Casa na URL (?c=senado); Câmara por padrão. */
export function casaDaUrl(): Casa {
  return new URLSearchParams(location.search).get('c') === 'senado' ? 'senado' : 'camara';
}

export interface Momento {
  id: string;
  tipo: TipoMomento;
  ano: number;
  data?: string;
  legislatura: number;
  rotulo: string;
  /** Cadeiras da Câmara naquele momento (503 em 1990; 513 depois). */
  cadeiras: number;
  /** Cadeiras com alguém eleito ou em exercício. A diferença são as cadeiras vagas. */
  ocupadas: number;
  fonte: 'tse' | 'camara' | 'senado';
  fonte_gerada_em?: string[];
  /** Senado, eleitos: cadeiras não renovadas naquela eleição (§7.8). */
  em_curso?: number;
  /** Senado, fotos: base formal do governo na data. */
  base?: { gabinete: string | null; partidos: string[]; cadeiras_base: number | null } | null;
}

export interface Fonte {
  nome: string;
  url: string;
  licenca: string;
  citacao?: string;
}

export interface Catalogo {
  gerado_em?: string;
  momentos: Momento[];
  legislaturas?: Record<string, { eleicao: number; inicio: string; fim: string }>;
  fontes?: Record<string, Fonte>;
  /** Senado: anos sem foto de 1º/fev e o motivo. */
  lacunas?: { data: string; motivo: string }[];
}

export interface Deputado {
  nome: string;
  uf: string;
  partido: string;
  sigla: string;
}

export interface Pontuacao {
  pontuacao: number;
  erro_padrao: number | null;
  n: number | null;
  /** Só onde a fonte publica rótulo (Bolognesi); null na BLS (DECISIONS A7). */
  faixa: string | null;
  fonte_id: 'bls' | 'bolognesi';
  ano_medicao: number;
  sigla_fonte: string;
  escala: string;
  nota: string | null;
}

/** legislatura → partido → pontuação. Partido ausente = não classificado. */
export type Ideologia = Record<string, Record<string, Pontuacao>>;

export interface Partido {
  sigla: string;
  nome: string;
  observacao: string | null;
  renomeacoes: { sigla_anterior: string; sigla_nova: string; data: string }[];
  origem: { partido: string; tipo: string; data: string; confirmado_no_tse: string }[];
  destino: { partido: string; tipo: string; data: string; confirmado_no_tse: string }[];
}

/** momento → partido → cadeiras. */
export type Agregados = Record<string, Record<string, number>>;

export interface Governo {
  governo_id: string;
  presidente: string;
  inicio: string;
  fim: string;
  partido_presidente: string;
  partido_id_inicio: string | null;
  observacao: string | null;
}

export interface Gabinete {
  gabinete: string;
  /** AAAA-MM quando a fonte só dá o mês; AAAA-MM-DD quando dá o dia. */
  inicio: string;
  evento: 'A' | 'B' | 'C';
  partidos: string[];
  governo: string | null;
  fonte: string;
  /** Na curadoria pós-2020: quem tem ministro e não foi contado, e por quê. */
  observacao: string | null;
  base_no_inicio: { data: string; cadeiras: number; em_exercicio: number } | null;
}

export interface BaseNoMomento {
  gabinete: string | null;
  partidos: string[];
  cadeiras_base: number | null;
  ocupadas: number;
  governo: string | null;
}

export interface Governos {
  cobertura_ate: string;
  governos: Governo[];
  gabinetes: Gabinete[];
  base_por_momento: Record<string, BaseNoMomento>;
}

export interface VotacaoResumo {
  id: string;
  data: string;
  /** Texto do resultado (o que foi votado e o placar), da Câmara. */
  descricao: string;
  proposicoes: string[];
  aprovada: boolean;
  orientacao_governo: string | null;
  /** [Sim, Não, Abstenção, Obstrução] */
  placar: [number, number, number, number];
  pec: boolean;
  /** Votações de impeachment, transcritas do Diário (DECISIONS A6). */
  impeachment?: boolean;
  arquivo?: string;
  ausentes?: number;
  fonte?: string;
}

export interface VotacaoCompleta extends VotacaoResumo {
  /** Um caractere por deputado da lista do ano: S, N, A, O, 7 (Artigo 17) ou . (sem voto). */
  v: string;
  /** Partido no momento do voto: índice em base 36 na lista de partidos do ano; . = sem voto. */
  p: string;
}

export interface VotacoesDoAno {
  /** [id na Câmara, nome, UF] */
  deputados: [number, string, string][];
  partidos: string[];
  votacoes: VotacaoCompleta[];
}

export interface IndicadorPartido {
  governismo: number | null;
  votos: number | null;
  votacoes_governo: number | null;
  rice: number | null;
  votacoes_rice: number | null;
}

export interface IndicadoresDeputado {
  nome: string;
  uf: string;
  /** [partido, primeiro voto, último voto] */
  partidos: [string, string, string][];
  legislaturas?: Record<
    string,
    { governismo?: number; votos?: number; presenca?: number; votacoes_esperadas?: number }
  >;
  governos?: Record<string, { governismo: number; votos: number }>;
}

export interface Indicadores {
  partidos: Record<
    string,
    { anos?: Record<string, IndicadorPartido>; governos?: Record<string, IndicadorPartido> }
  >;
  deputados: Record<string, IndicadoresDeputado>;
}

const cache = new Map<string, Promise<unknown>>();

function carregar<T>(caminho: string): Promise<T> {
  let p = cache.get(caminho);
  if (!p) {
    p = fetch(`${import.meta.env.BASE_URL}data/${caminho}`).then((r) => {
      if (!r.ok) throw new Error(`Falha ao carregar ${caminho}: ${r.status}`);
      return r.json();
    });
    cache.set(caminho, p);
  }
  return p as Promise<T>;
}

export const carregarCatalogo = (casa: Casa = 'camara') =>
  carregar<Catalogo>(casa === 'senado' ? 'catalogo-senado.json' : 'catalogo.json');
export const carregarIdeologia = () => carregar<Ideologia>('ideologia.json');
export const carregarPartidos = () => carregar<Record<string, Partido>>('partidos.json');
export const carregarAgregados = (casa: Casa = 'camara') =>
  carregar<Agregados>(casa === 'senado' ? 'agregados-senado.json' : 'agregados.json');
export const carregarGovernos = () => carregar<Governos>('governos.json');
export const carregarIndiceVotacoes = (casa: Casa = 'camara') =>
  carregar<VotacaoResumo[]>(`votacoes/${casa === 'senado' ? 'indice-senado' : 'indice'}.json`);
export const carregarVotacoesDoAno = (ano: number, casa: Casa = 'camara') =>
  carregar<VotacoesDoAno>(`votacoes/${casa === 'senado' ? 'senado' : 'ano'}-${ano}.json`);
export const carregarArquivoVotacao = (arquivo: string) =>
  carregar<VotacoesDoAno>(`votacoes/${arquivo}.json`);
export const carregarIndicadores = (casa: Casa = 'camara') =>
  carregar<Indicadores>(casa === 'senado' ? 'indicadores-senado.json' : 'indicadores.json');
export const carregarMomento = (id: string) => carregar<Deputado[]>(`momentos/${id}.json`);
