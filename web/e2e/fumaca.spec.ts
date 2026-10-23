import { expect, test, type Page } from '@playwright/test';

async function semRolagemLateral(page: Page) {
  const larguras = await page.evaluate(() => [
    document.documentElement.clientWidth,
    document.documentElement.scrollWidth,
  ]);
  expect(larguras[1]).toBeLessThanOrEqual(larguras[0] as number);
}

test('Início mostra o hemiciclo com as cadeiras classificadas e as fora da ordem', async ({
  page,
}) => {
  await page.goto('./?m=eleitos-2022');
  await expect(page.locator('body')).toHaveAttribute('data-pronto', 'true');
  const cadeiras = await page.locator('#hemiciclo circle.cadeira').count();
  const fora = await page.locator('#fora-da-ordem .fileira-a-parte span').count();
  expect(cadeiras + fora).toBe(513);
  await expect(page.locator('#legenda')).toContainText('Bolognesi');
  await semRolagemLateral(page);
});

test('trocar para eleitos e mover a linha do tempo atualiza a URL', async ({ page }) => {
  await page.goto('./');
  await expect(page.locator('body')).toHaveAttribute('data-pronto', 'true');
  await page.getByRole('button', { name: 'Eleitos', exact: true }).click();
  await expect(page).toHaveURL(/m=eleitos-2026/);
  const range = page.locator('#slider input[type=range]');
  await range.focus();
  await page.keyboard.press('Home');
  await expect(page).toHaveURL(/m=eleitos-1990/);
  await expect(page.locator('#legenda')).toContainText('BLS 1993');
});

test('hemiciclo navegável pelo teclado', async ({ page }) => {
  await page.goto('./?m=2024-02-01');
  await expect(page.locator('body')).toHaveAttribute('data-pronto', 'true');
  await page.locator('#hemiciclo svg').focus();
  await page.keyboard.press('ArrowRight');
  await expect(page.locator('#ficha')).toContainText('fonte: Bolognesi et al., 2022');
});

test('tabela acessível lista todos os deputados', async ({ page }) => {
  await page.goto('./?m=2010-02-01&v=tabela');
  await expect(page.locator('body')).toHaveAttribute('data-pronto', 'true');
  await expect(page.locator('#tabela-deputados tbody tr')).toHaveCount(505);
});

for (const caminho of [
  'evolucao.html',
  'partidos.html',
  'partidos.html?p=pt',
  'metodologia.html',
]) {
  test(`${caminho} carrega sem erro`, async ({ page }) => {
    const erros: string[] = [];
    page.on('pageerror', (e) => erros.push(e.message));
    await page.goto(`./${caminho}`);
    await expect(page.locator('body')).toHaveAttribute('data-pronto', 'true');
    await expect(page.locator('#erro')).toBeHidden();
    expect(erros).toEqual([]);
    await semRolagemLateral(page);
  });
}
