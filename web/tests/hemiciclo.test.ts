import { describe, expect, it } from 'vitest';
import { cadeirasPorFileira, fileirasPara, hemiciclo } from '../src/charts/hemiciclo';

describe('hemiciclo', () => {
  it.each([1, 81, 503, 513])('gera exatamente %i cadeiras', (n) => {
    expect(hemiciclo(n)).toHaveLength(n);
    expect(cadeirasPorFileira(n, fileirasPara(n)).reduce((a, b) => a + b, 0)).toBe(n);
  });

  it('não gera cadeiras para n = 0', () => {
    expect(hemiciclo(0)).toEqual([]);
  });

  it('fileiras externas têm mais cadeiras', () => {
    const porFileira = cadeirasPorFileira(513, 14);
    for (let i = 1; i < porFileira.length; i++) {
      expect(porFileira[i]).toBeGreaterThanOrEqual(porFileira[i - 1] as number);
    }
  });

  it('ordena da esquerda para a direita', () => {
    const cadeiras = hemiciclo(513);
    for (let i = 1; i < cadeiras.length; i++) {
      expect(cadeiras[i]?.angulo).toBeLessThanOrEqual(cadeiras[i - 1]?.angulo as number);
    }
  });

  it.each([81, 503, 513])('cadeiras não se sobrepõem (n = %i)', (n) => {
    const cadeiras = hemiciclo(n);
    let menor = Infinity;
    for (let i = 0; i < cadeiras.length; i++) {
      for (let j = i + 1; j < cadeiras.length; j++) {
        const a = cadeiras[i];
        const b = cadeiras[j];
        if (!a || !b) continue;
        menor = Math.min(menor, Math.hypot(a.x - b.x, a.y - b.y));
      }
    }
    expect(menor).toBeGreaterThan(2 * (cadeiras[0]?.r as number));
  });

  it('cabe no semicírculo de raio 1', () => {
    for (const c of hemiciclo(513)) {
      expect(Math.hypot(c.x, c.y)).toBeLessThanOrEqual(1 + 1e-9);
      expect(c.y).toBeGreaterThanOrEqual(-1e-9);
    }
  });
});
