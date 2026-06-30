import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';
import styles from './index.module.css';

const cards = [
  {
    icon: '📖',
    title: "Louisa's Guide",
    description: 'What BookKeeper does, what you need to do, and what happens automatically.',
    to: '/louisa-guide',
  },
  {
    icon: '🔄',
    title: 'What syncs',
    description: 'What products appear on the website, what fields sync, and how often.',
    to: '/sync/outbound',
  },
  {
    icon: '📦',
    title: 'Order Fulfillment',
    description: 'How to process online orders in Shopify and enter them in Bookscan.',
    to: '/sync/order-fulfillment',
  },
  {
    icon: '🔧',
    title: 'Troubleshooting',
    description: 'Quick fixes for the most common problems.',
    to: '/troubleshooting',
  },
  {
    icon: '🚀',
    title: 'Go-Live Day',
    description: 'Steps for the day the site goes live.',
    to: '/go-live-checklist',
  },
  {
    icon: '🖥️',
    title: 'Shop Machine',
    description: 'How to restart the sync, deploy updates, and recover from errors.',
    to: '/setup/shop-machine',
  },
];


export default function Home() {
  return (
    <Layout title="Home" description="BookKeeper for Shopify — Bookscan sync documentation">
      {/* ── HERO ── */}
      <div className={styles.hero}>
        <div className={styles.heroInner}>
          <div className={styles.heroText}>
            <div className={styles.heroEyebrow}>Bruce McKenzie Booksellers</div>
            <h1 className={styles.heroTitle}>BookKeeper<br/>for Shopify</h1>
            <p className={styles.heroSubtitle}>
              Keeps the Shopify store in sync with Bookscan automatically —
              products, prices, stock levels, and cover images.
            </p>
            <div className={styles.heroStats}>
              <div className={styles.stat}><span className={styles.statNum}>38,013</span><span className={styles.statLabel}>products</span></div>
              <div className={styles.statDivider}/>
              <div className={styles.stat}><span className={styles.statNum}>2 hr</span><span className={styles.statLabel}>sync cycle</span></div>
              <div className={styles.statDivider}/>
              <div className={styles.stat}><span className={styles.statNum}>Delta</span><span className={styles.statLabel}>only changed</span></div>
            </div>
            <div className={styles.heroCta}>
              <Link className={styles.btnPrimary} to="/intro">Read the docs</Link>
              <Link className={styles.btnSecondary} to="/louisa-guide">Louisa's guide</Link>
            </div>
          </div>
          <div className={styles.heroVisual}>
            <div className={styles.syncDiagram}>
              <div className={styles.syncBox}>
                <div className={styles.syncIcon}>📦</div>
                <div className={styles.syncBoxLabel}>Bookscan</div>
                <div className={styles.syncBoxSub}>Shop machine</div>
              </div>
              <div className={styles.syncArrow}>
                <div className={styles.syncArrowLine}/>
                <div className={styles.syncArrowLabel}>every hour</div>
                <div className={styles.syncArrowLine}/>
              </div>
              <div className={styles.syncBox}>
                <div className={styles.syncIcon}>🛍️</div>
                <div className={styles.syncBoxLabel}>Shopify</div>
                <div className={styles.syncBoxSub}>bmbooks.co.nz</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <main className={styles.main}>

        {/* ── QUICK NAV ── */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Documentation</h2>
          <div className={styles.cardGrid}>
            {cards.map(card => (
              <Link key={card.to} to={card.to} className={styles.card}>
                <div className={styles.cardIcon}>{card.icon}</div>
                <div className={styles.cardTitle}>{card.title}</div>
                <div className={styles.cardDesc}>{card.description}</div>
              </Link>
            ))}
          </div>
        </section>


      </main>
    </Layout>
  );
}
