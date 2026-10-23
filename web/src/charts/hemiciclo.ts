// Geometria do hemiciclo (PROJECT.md, seção 8): N cadeiras em fileiras semicirculares concêntricas,
// cada fileira com cadeiras proporcionais ao comprimento do arco. As cadeiras saem ordenadas por
// ângulo, da esquerda para a direita, para que cada grupo (partido) ocupe uma "fatia" contínua.
// Só geometria: cor, ordem dos partidos e interação ficam com quem desenha.

export interface Cadeira {
  /** Centro, num semicírculo de raio 1: x de -1 a 1, y de 0 (base) a 1 (topo). */
  x: number;
  y: number;
  /** Raio da bolinha, na mesma unidade. */
  r: number;
  /** Fileira, de 0 (a mais interna) a fileiras - 1. */
  fileira: number;
  /** Ângulo em radianos, de π (extrema esquerda) a 0 (extrema direita). */
  angulo: number;
}

/** Raio da fileira mais interna, como fração do raio externo. */
const RAIO_INTERNO = 0.4;

/** Número de fileiras para N cadeiras: cresce com √N (513 → 14; 81 → 5). */
export function fileirasPara(n: number): number {
  return Math.max(1, Math.round(Math.sqrt(n) * 0.6));
}

/** Raios das fileiras, igualmente espaçados entre RAIO_INTERNO e 1. */
function raios(k: number): number[] {
  if (k === 1) return [1];
  return Array.from({ length: k }, (_, i) => RAIO_INTERNO + ((1 - RAIO_INTERNO) * i) / (k - 1));
}

/** Cadeiras por fileira, proporcionais ao raio (comprimento do arco) e somando exatamente n.
 * O arredondamento usa o método dos maiores restos. */
export function cadeirasPorFileira(n: number, k: number): number[] {
  const rs = raios(k);
  const soma = rs.reduce((a, b) => a + b, 0);
  const exatas = rs.map((r) => (n * r) / soma);
  const base = exatas.map(Math.floor);
  let faltam = n - base.reduce((a, b) => a + b, 0);
  const ordem = exatas
    .map((v, i) => ({ i, resto: v - Math.floor(v) }))
    .sort((a, b) => b.resto - a.resto || b.i - a.i);
  for (const { i } of ordem) {
    if (faltam === 0) break;
    base[i] = (base[i] as number) + 1;
    faltam--;
  }
  return base;
}

/** Posições das n cadeiras, da esquerda para a direita. */
export function hemiciclo(n: number, k = fileirasPara(n)): Cadeira[] {
  if (n <= 0) return [];
  const rs = raios(k);
  const porFileira = cadeirasPorFileira(n, k);
  // Espaço disponível por cadeira: o menor entre o passo radial e o passo ao longo do arco.
  const passoRadial = k > 1 ? (1 - RAIO_INTERNO) / (k - 1) : 1;
  let passoArco = Infinity;
  porFileira.forEach((m, i) => {
    if (m > 1) passoArco = Math.min(passoArco, (Math.PI * (rs[i] as number)) / (m - 1));
  });
  const r = 0.42 * Math.min(passoRadial, passoArco);

  const cadeiras: Cadeira[] = [];
  porFileira.forEach((m, fileira) => {
    const raio = rs[fileira] as number;
    for (let j = 0; j < m; j++) {
      const angulo = m === 1 ? Math.PI / 2 : Math.PI * (1 - j / (m - 1));
      cadeiras.push({
        x: raio * Math.cos(angulo),
        y: raio * Math.sin(angulo),
        r,
        fileira,
        angulo,
      });
    }
  });
  // Esquerda para a direita; no mesmo ângulo, de dentro para fora.
  return cadeiras.sort((a, b) => b.angulo - a.angulo || a.fileira - b.fileira);
}
