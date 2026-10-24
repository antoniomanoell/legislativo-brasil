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
  await expect(page.locator('#ficha')).not.toBeEmpty();
  await expect(page.locator('#ficha')).not.toContainText('fonte:');
  await expect(page.locator('#legenda')).toContainText('Bolognesi et al., 2022');
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

test('base formal na foto de 2010, com siglas da época e destaque no hemiciclo', async ({
  page,
}) => {
  await page.goto('./?m=2010-02-01&b=1');
  await expect(page.locator('body')).toHaveAttribute('data-pronto', 'true');
  const linha = page.locator('#linha-base');
  await expect(linha).toContainText('gabinete Lula 2-3');
  await expect(linha).toContainText('PRB');
  await expect(linha).not.toContainText('REPUBLICANOS');
  expect(await page.locator('#hemiciclo circle.esmaecida').count()).toBeGreaterThan(0);
});

test('Governos põe cada gabinete no governo certo', async ({ page }) => {
  await page.goto('./governos.html');
  await expect(page.locator('body')).toHaveAttribute('data-pronto', 'true');
  await expect(page.locator('#gov-temer')).toBeAttached();
  const temer = page.locator('section', { has: page.locator('#gov-temer') });
  await expect(temer).toContainText('Temer-1');
  const dilma2 = page.locator('section', { has: page.locator('#gov-dilma2') });
  await expect(dilma2).not.toContainText('Temer-1');
});

test('votação de mérito da PEC 6/2019 em destaque, com hemiciclo pelo voto', async ({ page }) => {
  await page.goto('./votacoes.html?ano=2019&d=1');
  await expect(page.locator('body')).toHaveAttribute('data-pronto', 'true');
  const linha = page.locator('#linhas tr', { hasText: '370 × 124' });
  await expect(linha).toContainText('PEC 6/2019');
  await linha.getByRole('link').click();
  await expect(page.locator('body')).toHaveAttribute('data-pronto', 'true');
  await expect(page.locator('.placar')).toContainText('Sim 370');
  const cadeiras = await page.locator('#hemiciclo circle.cadeira').count();
  const fora = await page.locator('#fora .fileira-a-parte span').count();
  expect(cadeiras + fora).toBe(370 + 124 + 1); // Sim + Não + abstenção (sem Artigo 17 nesta votação)
});

test('perfil de deputado com presença e votos', async ({ page }) => {
  await page.goto('./deputados.html?q=tiririca');
  await expect(page.locator('body')).toHaveAttribute('data-pronto', 'true');
  await page.getByRole('link', { name: 'Tiririca' }).click();
  await expect(page.locator('body')).toHaveAttribute('data-pronto', 'true');
  await expect(page.locator('#conteudo')).toContainText('Presença');
  await expect(page.locator('#votos tbody tr').first()).toBeVisible();
});

test('impeachment de 2016 com o voto de cada deputado e a fonte', async ({ page }) => {
  await page.goto('./votacoes.html?v=impeachment-2016&a=2016');
  await expect(page.locator('body')).toHaveAttribute('data-pronto', 'true');
  await expect(page.locator('.placar')).toContainText('Ausentes: 2');
  await expect(page.locator('#conteudo')).toContainText('Diário da Câmara dos Deputados');
  const cadeiras = await page.locator('#hemiciclo circle.cadeira').count();
  const fora = await page.locator('#fora .fileira-a-parte span').count();
  expect(cadeiras + fora).toBe(367 + 137 + 7);
});
