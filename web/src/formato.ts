// Formatação em pt-BR. `formatarNumero` e `esc` iguais aos do mapa (web/src/format.ts).

const cache = new Map<number, Intl.NumberFormat>();

/** Formata um número em pt-BR (vírgula decimal, ponto de milhar) com casas fixas. */
export function formatarNumero(valor: number, casasDecimais: number): string {
  let fmt = cache.get(casasDecimais);
  if (!fmt) {
    fmt = new Intl.NumberFormat('pt-BR', {
      minimumFractionDigits: casasDecimais,
      maximumFractionDigits: casasDecimais,
    });
    cache.set(casasDecimais, fmt);
  }
  return fmt.format(valor);
}

/** Escapa texto para interpolar em HTML. */
export function esc(texto: string): string {
  return texto.replace(
    /[&<>"']/g,
    (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c] as string,
  );
}

export function pct(parte: number, total: number): string {
  return `${formatarNumero((100 * parte) / total, 1)}%`;
}
