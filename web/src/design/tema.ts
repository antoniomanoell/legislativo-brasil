// Importado sem alterações de antoniomanoell/mapa-brasil, web/src/tema.ts, commit ce627fa.

// Tema claro/escuro. Segue o sistema até a pessoa escolher no botão; a escolha fica no navegador.
// Um script no <head> de cada página aplica a escolha salva antes da primeira pintura.

export type Tema = 'claro' | 'escuro';

const CHAVE = 'tema';
const escuroNoSistema = matchMedia('(prefers-color-scheme: dark)');

const ICONE_LUA =
  '<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true"><path d="M15.5 12.6A6.5 6.5 0 0 1 7.4 4.5a6.5 6.5 0 1 0 8.1 8.1z" fill="currentColor"/></svg>';
const ICONE_SOL =
  '<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true"><circle cx="10" cy="10" r="3.6" fill="currentColor"/><path d="M10 1.8v2.4M10 15.8v2.4M1.8 10h2.4M15.8 10h2.4M4.2 4.2l1.7 1.7M14.1 14.1l1.7 1.7M4.2 15.8l1.7-1.7M14.1 5.9l1.7-1.7" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>';

export function temaAtual(): Tema {
  const escolhido = document.documentElement.dataset['tema'];
  if (escolhido === 'claro' || escolhido === 'escuro') return escolhido;
  return escuroNoSistema.matches ? 'escuro' : 'claro';
}

/** Valor de uma variável de cor do CSS no tema atual (o mapa e os gráficos leem daqui). */
export function cor(nome: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(nome).trim();
}

/** Liga o botão de tema (se houver) e avisa quem precisa redesenhar quando o tema muda. */
export function iniciarTema(aoMudar?: (tema: Tema) => void): void {
  const botao = document.querySelector<HTMLButtonElement>('#tema');
  const atualizarBotao = () => {
    if (!botao) return;
    const escuro = temaAtual() === 'escuro';
    botao.innerHTML = escuro ? ICONE_SOL : ICONE_LUA;
    botao.setAttribute('aria-label', escuro ? 'Usar tema claro' : 'Usar tema escuro');
    botao.title = botao.getAttribute('aria-label') as string;
  };
  atualizarBotao();
  botao?.addEventListener('click', () => {
    const novo: Tema = temaAtual() === 'escuro' ? 'claro' : 'escuro';
    document.documentElement.dataset['tema'] = novo;
    try {
      localStorage.setItem(CHAVE, novo);
    } catch {
      // Sem armazenamento (navegação privada): a escolha vale só nesta página.
    }
    atualizarBotao();
    aoMudar?.(novo);
  });
  escuroNoSistema.addEventListener('change', () => {
    if (document.documentElement.dataset['tema']) return;
    atualizarBotao();
    aoMudar?.(temaAtual());
  });
}
