// Importado sem alterações de antoniomanoell/mapa-brasil, web/src/ajuda.ts, commit ce627fa.

// Botão "?" com uma explicação curta, num popover nativo do navegador (sem biblioteca).

/** HTML do botão e do popover. `texto` é HTML do próprio projeto, não entrada de usuário. */
export function ajuda(id: string, rotulo: string, texto: string): string {
  return `<button type="button" class="ajuda" popovertarget="${id}" aria-label="${rotulo}" title="${rotulo}">?</button>
    <div id="${id}" popover class="ajuda-pop" role="note">${texto}</div>`;
}
