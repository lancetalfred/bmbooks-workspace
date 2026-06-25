// @ts-check
const { test } = require('@playwright/test');

const STAGING_PARAM = 'preview_theme_id=150391423054';

test('diagnose — search results card selectors', async ({ page }) => {
  await page.goto(`/search?q=new+zealand&${STAGING_PARAM}`);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(4000);

  // Find any links pointing to /products/
  const productLinks = await page.$$eval('a[href*="/products/"]', links =>
    links.slice(0, 5).map(a => {
      const parent = a.parentElement;
      const grandparent = parent ? parent.parentElement : null;
      return {
        aClass: (a.className || '').toString().slice(0, 100),
        parentTag: parent ? parent.tagName : '',
        parentClass: parent ? (parent.className || '').toString().slice(0, 100) : '',
        gpTag: grandparent ? grandparent.tagName : '',
        gpClass: grandparent ? (grandparent.className || '').toString().slice(0, 100) : '',
        href: a.href.slice(-60),
        text: a.textContent?.trim().slice(0, 50),
      };
    })
  );

  console.log('=== PRODUCT LINKS ===');
  productLinks.forEach(l => console.log(JSON.stringify(l)));

  await page.screenshot({ path: 'test-results/diagnose-results-cards.png', fullPage: false });
});
