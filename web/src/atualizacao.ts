// Data de geração de cada conjunto de dados (atualizacao.json, gravado pelo pipeline etapa a etapa).
// Cada página mostra, no rodapé, a data dos conjuntos que usa.

import { carregarAtualizacao, type ConjuntoDeDados } from './dados';

const NOMES: Record<ConjuntoDeDados, string> = {
  composicao_camara: 'composição da Câmara',
  composicao_senado: 'composição do Senado',
  votacoes_camara: 'votações da Câmara',
  votacoes_senado: 'votações do Senado',
  governos: 'governos e gabinetes',
  congresso_2027: 'composição prevista para 2027',
};

export async function mostrarAtualizacao(conjuntos: ConjuntoDeDados[]): Promise<void> {
  const alvo = document.querySelector('#atualizacao');
  if (!alvo) return;
  try {
    const datas = await carregarAtualizacao();
    const partes = conjuntos
      .filter((c) => datas[c])
      .map((c) => `${NOMES[c]}, ${(datas[c] as string).split('-').reverse().join('/')}`);
    alvo.textContent = partes.length ? `Dados gerados em: ${partes.join('; ')}.` : '';
  } catch {
    // Sem a data, o rodapé fica sem a linha; o resto da página não depende dela.
  }
}
