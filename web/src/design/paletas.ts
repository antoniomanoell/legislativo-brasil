// Paletas das sete faixas ideológicas (PROJECT.md, seção 9; DECISIONS A9). A escolhida é a D,
// vermelho (esquerda) ↔ azul (direita), a convenção mais reconhecível; as demais ficam como registro
// das candidatas. Divergentes: dois matizes que escurecem para as pontas e cinza neutro no centro.
// "Não classificado" não é cor: é a hachura do mapa (--hachura-*), para não parecer uma posição.
//
// Geradas em OKLCH e conferidas com o validador de paletas (daltonismo protan/deutan/tritan e visão
// normal, ΔE OKLab entre faixas vizinhas; contraste contra o fundo de cada tema). Os valores da D
// estão repetidos em congresso.css (--faixa-1 a --faixa-7).

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
    id: 'D',
    nome: 'Vermelho ↔ azul (escolhida)',
    claro: ['#901e1c', '#ce5950', '#ff988d', '#dbdbdb', '#80beff', '#3d84db', '#004d9f'],
    escuro: ['#ffbbb1', '#e77f75', '#ad524a', '#424242', '#3d73b6', '#67a4f1', '#a8d8ff'],
    validacao:
      'Passa em tudo nos dois temas. Pior par vizinho para daltonismo: ΔE 11,8 (claro) e 12,1 (escuro); meta ≥ 8.',
  },
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
