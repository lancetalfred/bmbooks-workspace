// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'BookKeeper for Shopify',
  tagline: 'Bookscan → Shopify sync for Bruce McKenzie Booksellers',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  url: 'https://your-site.example.com',
  baseUrl: '/',

  organizationName: 'bmbooks',
  projectName: 'bookkeeper-for-shopify',

  onBrokenLinks: 'throw',

  themes: [
    [
      '@easyops-cn/docusaurus-search-local',
      {
        hashed: true,
        indexDocs: true,
        indexBlog: false,
        docsRouteBasePath: '/',
        searchBarPosition: 'right',
        highlightSearchTermsOnTargetPage: true,
      },
    ],
  ],

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          routeBasePath: '/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      colorMode: {
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'BookKeeper for Shopify',
        style: 'dark',
        logo: {
          alt: 'BMBooks logo',
          src: 'img/logo.jpg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'mainSidebar',
            position: 'left',
            label: 'Docs',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              { label: 'Overview',       to: '/intro' },
              { label: 'Architecture',   to: '/architecture/overview' },
              { label: 'Setup',          to: '/setup/requirements' },
              { label: 'UAT Plan',       to: '/uat/uat-plan' },
              { label: 'Changelog',      to: '/changelog' },
            ],
          },
          {
            title: 'BMBooks',
            items: [
              { label: 'bmbooks.co.nz',  href: 'https://bmbooks.co.nz' },
              { label: 'Shopify Admin',  href: 'https://bruce-mckenzie-booksellers.myshopify.com/admin' },
            ],
          },
        ],
        copyright: `BookKeeper for Shopify — Bruce McKenzie Booksellers`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['python', 'bash', 'json'],
      },
    }),
};

export default config;
