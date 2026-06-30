// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  mainSidebar: [
    'intro',
    'louisa-guide',
    {
      type: 'category',
      label: 'Sync',
      items: [
        'sync/outbound',
        'sync/order-fulfillment',
      ],
    },
    'troubleshooting',
    'glossary',
    'go-live-checklist',
    {
      type: 'category',
      label: 'Operations (Lance)',
      items: [
        'setup/shop-machine',
      ],
    },
    'changelog',
  ],
};

export default sidebars;
