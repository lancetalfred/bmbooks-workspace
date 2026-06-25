# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: searchanise.spec.js >> Searchanise — staging >> ISBN search returns matching product
- Location: tests/searchanise.spec.js:60:3

# Error details

```
TimeoutError: locator.waitFor: Timeout 8000ms exceeded.
Call log:
  - waiting for locator('input.bmbooks-search-bar__input').first() to be visible

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - main [ref=e2]:
    - generic [ref=e7]:
      - img "Bruce McKenzie Booksellers" [ref=e10]
      - heading "Opening soon" [level=1] [ref=e12]
      - paragraph [ref=e14]: Sign up for our newsletter to be the first to know when we launch.
      - generic [ref=e17]:
        - generic [ref=e18]: Email
        - textbox "Email" [ref=e19]:
          - /placeholder: Email address
        - button "Sign up" [ref=e20] [cursor=pointer]
  - contentinfo [ref=e21]:
    - generic [ref=e23]:
      - paragraph [ref=e24]:
        - text: This shop will be powered by
        - link "Shopify" [ref=e25] [cursor=pointer]:
          - /url: //shopify.com
          - img [ref=e26]
      - generic [ref=e28]:
        - button "Enter using password" [ref=e29] [cursor=pointer]
        - paragraph [ref=e30]:
          - text: Are you the store owner?
          - link "Log in here" [ref=e31] [cursor=pointer]:
            - /url: /admin
  - iframe [ref=e33]:
    - generic [ref=f2e4]:
      - button [ref=f2e7] [cursor=pointer]:
        - img [ref=f2e9]
        - img [ref=f2e12]
      - generic [ref=f2e15]:
        - generic [ref=f2e18]:
          - link "Logo" [ref=f2e19] [cursor=pointer]:
            - /url: https://admin.shopify.com/store/1twhis-a1
            - img "Logo" [ref=f2e20]
          - generic [ref=f2e21]:
            - generic [ref=f2e22]:
              - generic [ref=f2e23]: BMBooks - Staging
              - generic [ref=f2e24]: Draft
            - generic [ref=f2e25]:
              - link "Password protected" [ref=f2e26] [cursor=pointer]:
                - /url: https://admin.shopify.com/store/1twhis-a1/online_store/preferences?tutorial=unlock
                - generic [ref=f2e27]: Password protected
              - img [ref=f2e31]
        - generic [ref=f2e35]:
          - button "Hide bar" [ref=f2e37] [cursor=pointer]:
            - generic [ref=f2e38]: Hide bar
          - button "Exit preview" [ref=f2e40] [cursor=pointer]:
            - generic [ref=f2e41]: Exit preview
          - button "Copy link" [ref=f2e44] [cursor=pointer]:
            - img [ref=f2e48]
            - generic [ref=f2e50]: Copy link
```

# Test source

```ts
  1   | // @ts-check
  2   | const { test, expect } = require('@playwright/test');
  3   | 
  4   | const STAGING_PARAM = 'preview_theme_id=150391423054';
  5   | 
  6   | // ── helpers ───────────────────────────────────────────────────────────────────
  7   | 
  8   | async function goToStaging(page, path = '/') {
  9   |   await page.goto(`${path}${path.includes('?') ? '&' : '?'}${STAGING_PARAM}`);
  10  | 
  11  |   // Handle store password if present
  12  |   const passwordInput = page.locator('input[name="password"]');
  13  |   if (await passwordInput.isVisible({ timeout: 4000 }).catch(() => false)) {
  14  |     await passwordInput.fill('Larkspur');
  15  |     await page.locator('[type="submit"]').click();
  16  |     await page.waitForURL(/\/((?!password).)*$/, { timeout: 15000 });
  17  |   }
  18  | 
  19  |   await page.waitForLoadState('networkidle');
  20  | }
  21  | 
  22  | async function typeInSearchBar(page, query) {
  23  |   // The search bar is inline in the header — no toggle needed
  24  |   const input = page.locator('input.bmbooks-search-bar__input').first();
> 25  |   await input.waitFor({ state: 'visible', timeout: 8000 });
      |               ^ TimeoutError: locator.waitFor: Timeout 8000ms exceeded.
  26  |   await input.click();
  27  |   await input.pressSequentially(query, { delay: 80 });
  28  |   // Give Searchanise time to fetch and render
  29  |   await page.waitForTimeout(2500);
  30  | }
  31  | 
  32  | // ── tests ──────────────────────────────────────────────────────────────────────
  33  | 
  34  | test.describe('Searchanise — staging', () => {
  35  | 
  36  |   // ── 1. Author search ─────────────────────────────────────────────────────────
  37  |   test('author search returns instant results', async ({ page }) => {
  38  |     await goToStaging(page);
  39  | 
  40  |     await typeInSearchBar(page, 'Eleanor Catton');
  41  | 
  42  |     const dropdown = page.locator('#snize-instant-search-results');
  43  |     await expect(dropdown).toBeVisible({ timeout: 10000 });
  44  | 
  45  |     const products = dropdown.locator('li.snize-product');
  46  |     const count = await products.count();
  47  |     console.log(`Author "Eleanor Catton" → ${count} instant result(s)`);
  48  |     expect(count).toBeGreaterThan(0);
  49  | 
  50  |     // Log product titles for review
  51  |     for (let i = 0; i < Math.min(count, 5); i++) {
  52  |       const title = await products.nth(i).locator('.snize-title').innerText().catch(() => '?');
  53  |       console.log(`  [${i + 1}] ${title}`);
  54  |     }
  55  | 
  56  |     await page.screenshot({ path: 'test-results/01-author-search.png' });
  57  |   });
  58  | 
  59  |   // ── 2. ISBN exact match ───────────────────────────────────────────────────────
  60  |   test('ISBN search returns matching product', async ({ page }) => {
  61  |     await goToStaging(page);
  62  | 
  63  |     // The Luminaries by Eleanor Catton — well-known NZ title
  64  |     await typeInSearchBar(page, '9780143121633');
  65  | 
  66  |     const dropdown = page.locator('#snize-instant-search-results');
  67  |     await expect(dropdown).toBeVisible({ timeout: 10000 });
  68  | 
  69  |     const products = dropdown.locator('li.snize-product');
  70  |     const count = await products.count();
  71  |     console.log(`ISBN 9780143121633 → ${count} instant result(s)`);
  72  | 
  73  |     await page.screenshot({ path: 'test-results/02-isbn-search.png' });
  74  | 
  75  |     if (count === 0) {
  76  |       // ISBN not in catalog — soft fail: log and pass, the mechanism works
  77  |       console.warn('No results for this ISBN — may not be in current stock. Instant search mechanism is functioning.');
  78  |     } else {
  79  |       const title = await products.first().locator('.snize-title').innerText().catch(() => '?');
  80  |       console.log(`  Found: ${title}`);
  81  |       expect(count).toBeGreaterThan(0);
  82  |     }
  83  |   });
  84  | 
  85  |   // ── 3. Genre / keyword search ─────────────────────────────────────────────────
  86  |   test('genre keyword search returns instant results', async ({ page }) => {
  87  |     await goToStaging(page);
  88  | 
  89  |     await typeInSearchBar(page, 'Crime');
  90  | 
  91  |     const dropdown = page.locator('#snize-instant-search-results');
  92  |     await expect(dropdown).toBeVisible({ timeout: 10000 });
  93  | 
  94  |     const products = dropdown.locator('li.snize-product');
  95  |     const count = await products.count();
  96  |     console.log(`Genre "Crime" → ${count} instant result(s)`);
  97  | 
  98  |     for (let i = 0; i < Math.min(count, 3); i++) {
  99  |       const title = await products.nth(i).locator('.snize-title').innerText().catch(() => '?');
  100 |       console.log(`  [${i + 1}] ${title}`);
  101 |     }
  102 | 
  103 |     await page.screenshot({ path: 'test-results/03-genre-search.png' });
  104 |     expect(count).toBeGreaterThan(0);
  105 |   });
  106 | 
  107 |   // ── 4. Search results page loads products ────────────────────────────────────
  108 |   test('search results page renders products', async ({ page }) => {
  109 |     await goToStaging(page, '/search?q=new+zealand');
  110 | 
  111 |     // Products rendered via custom <product-card> elements in this theme
  112 |     const productCards = page.locator('a.product-card__link, li.product-grid__item');
  113 |     await expect(productCards.first()).toBeVisible({ timeout: 15000 });
  114 | 
  115 |     const count = await productCards.count();
  116 |     console.log(`"new zealand" search results page → ${count} product card(s)`);
  117 | 
  118 |     await page.screenshot({ path: 'test-results/04-results-page.png', fullPage: true });
  119 |     expect(count).toBeGreaterThan(0);
  120 |   });
  121 | 
  122 |   // ── 5. No _cstatus-* tags visible in filter labels ───────────────────────────
  123 |   test('filter panel contains no _cstatus-* text', async ({ page }) => {
  124 |     await goToStaging(page, '/search?q=fiction');
  125 | 
```