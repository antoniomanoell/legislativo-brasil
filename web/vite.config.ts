import { resolve } from 'node:path';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        index: resolve(import.meta.dirname, 'index.html'),
        evolucao: resolve(import.meta.dirname, 'evolucao.html'),
        governos: resolve(import.meta.dirname, 'governos.html'),
        votacoes: resolve(import.meta.dirname, 'votacoes.html'),
        deputados: resolve(import.meta.dirname, 'deputados.html'),
        partidos: resolve(import.meta.dirname, 'partidos.html'),
        metodologia: resolve(import.meta.dirname, 'metodologia.html'),
        sobre: resolve(import.meta.dirname, 'sobre.html'),
        estilo: resolve(import.meta.dirname, 'estilo.html'),
      },
    },
  },
  test: {
    include: ['tests/**/*.test.ts'],
  },
});
