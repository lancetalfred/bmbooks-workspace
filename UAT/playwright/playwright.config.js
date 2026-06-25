// @ts-check
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 120000,
  retries: 1,
  use: {
    baseURL: 'https://bruce-mckenzie-booksellers.myshopify.com',
    headless: false,
    viewport: { width: 1280, height: 900 },
    screenshot: 'on',
    video: 'retain-on-failure',
  },
  reporter: [['list'], ['html', { open: 'never' }]],
});
