// Tipos e carregamento dos JSON gerados pelo pipeline (pipeline/src/congresso/load/site.py).

export type TipoMomento = 'eleitos' | 'exercicio';

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
  fonte: 'tse' | 'camara';
  fonte_gerada_em?: string[];
}

export interface Fonte {
  nome: string;
  url: string;
  licenca: string;
  citacao?: string;
}

export interface Catalogo {
  gerado_em: string;
  momentos: Momento[];
  legislaturas: Record<string, { eleicao: number; inicio: string; fim: string }>;
  fontes: Record<string, Fonte>;
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

export const carregarCatalogo = () => carregar<Catalogo>('catalogo.json');
export const carregarIdeologia = () => carregar<Ideologia>('ideologia.json');
export const carregarPartidos = () => carregar<Record<string, Partido>>('partidos.json');
export const carregarAgregados = () => carregar<Agregados>('agregados.json');
export const carregarGovernos = () => carregar<Governos>('governos.json');
export const carregarMomento = (id: string) => carregar<Deputado[]>(`momentos/${id}.json`);
