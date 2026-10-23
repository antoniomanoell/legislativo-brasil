// Paletas candidatas para as sete faixas ideológicas (PROJECT.md, seção 9; decisão do Antônio,
// PENDENCIAS.md A9). Divergentes: dois matizes que escurecem para as pontas e cinza neutro no centro.
// Nenhuma usa vermelho, azul ou verde puros, as cores de marca mais comuns entre os partidos.
// "Não classificado" não é cor: é a hachura do mapa (--hachura-*), para não parecer uma posição.
//
// Geradas em OKLCH (claro: L 0,43/0,61/0,79 e centro 0,89; escuro: L 0,84/0,66/0,50 e centro 0,38)
// e conferidas com o validador de paletas (CVD por protan/deutan/tritan e visão normal, ΔE OKLab
// entre faixas vizinhas). Resultado em DECISIONS.md quando o Antônio escolher.

export const FAIXAS = [
  'extrema-esquerda',
  'esquerda',
  'centro-esquerda',
  'centro',
  'centro-direita',
  'direita',
  'extrema-direita',
] as const;

export type Faixa = (typeof FAIXAS)[number];

export interface Paleta {
  id: string;
  nome: string;
  claro: readonly string[];
  escuro: readonly string[];
  /** Resumo do validador, para a página de amostra. */
  validacao: string;
}

export const PALETAS: readonly Paleta[] = [
  {
    id: 'A',
    nome: 'Roxo ↔ laranja',
    claro: ['#5e3594', '#926bcf', '#c7a7ff', '#dbdbdb', '#faa365', '#c56604', '#8a2f00'],
    escuro: ['#d6b9ff', '#9f7ed6', '#6e519d', '#424242', '#964d09', '#ce7a3b', '#ffb57c'],
    validacao:
      'Passa em tudo nos dois temas. Pior par vizinho para daltonismo: ΔE 14,5 (claro) e 11,9 (escuro); meta ≥ 8.',
  },
  {
    id: 'B',
    nome: 'Verde-azulado ↔ ocre',
    claro: ['#006570', '#009ca6', '#20d3db', '#dbdbdb', '#ebae51', '#b67300', '#7d3d00'],
    escuro: ['#54e2e9', '#00a9b1', '#00767e', '#424242', '#8a5700', '#c0851f', '#f8bf6c'],
    validacao:
      'No tema claro, centro-esquerda × centro fica no piso para protanopia (ΔE 6,1): aceitável só porque partido e tabela acompanham a cor.',
  },
  {
    id: 'C',
    nome: 'Magenta ↔ verde-azulado',
    claro: ['#842162', '#c05998', '#f697ce', '#dbdbdb', '#20d3db', '#009ca6', '#006570'],
    escuro: ['#ffaadc', '#c96fa4', '#914373', '#424242', '#00767e', '#00a9b1', '#54e2e9'],
    validacao:
      'Mesma ressalva da B, do lado direito (centro × centro-direita, ΔE 6,1 para protanopia no tema claro).',
  },
];
