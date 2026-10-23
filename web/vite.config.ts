import { resolve } from 'node:path';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        index: resolve(import.meta.dirname, 'index.html'),
        evolucao: resolve(import.meta.dirname, 'evolucao.html'),
        estilo: resolve(import.meta.dirname, 'estilo.html'),
      },
    },
  },
  test: {
    include: ['tests/**/*.test.ts'],
  },
});
