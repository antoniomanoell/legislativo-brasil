// Páginas de texto (Metodologia, Sobre): Markdown do próprio projeto. Enquanto o texto tiver a marca
// de rascunho (PROJECT.md, 0.4), a página mostra o aviso.

import { marked } from 'marked';
import { iniciarTema } from './design/tema';

const MARCA_RASCUNHO = '<!-- RASCUNHO: revisar com Antônio -->';
const AVISO =
  '<p class="aviso-rascunho" role="note">Rascunho: este texto ainda não foi revisado pelo mantenedor.</p>';

export function mostrarTexto(texto: string): void {
  iniciarTema();
  const alvo = document.querySelector('#conteudo') as HTMLElement;
  // Texto do próprio projeto, não entrada de usuário.
  alvo.innerHTML =
    (texto.includes(MARCA_RASCUNHO) ? AVISO : '') +
    (marked.parse(texto.replaceAll(MARCA_RASCUNHO, ''), { async: false }) as string);
  document.body.dataset['pronto'] = 'true';
}
