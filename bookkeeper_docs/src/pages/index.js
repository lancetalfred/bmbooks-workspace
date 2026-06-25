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
    icon: '⚙️',
    title: 'Setup',
    description: 'Requirements, configuration, and the shop machine installation guide.',
    to: '/setup/requirements',
  },
  {
    icon: '🏗️',
    title: 'Architecture',
    description: 'How the sync works under the hood — DBF files, field mapping, delta logic.',
    to: '/architecture/overview',
  },
  {
    icon: '🔄',
    title: 'Sync',
    description: 'Outbound product sync and the inbound order sync (Phase 2).',
    to: '/sync/outbound',
  },
  {
    icon: '✅',
    title: 'UAT Plan',
    description: '58 test cases covering every aspect of the integration before go-live.',
    to: '/uat/uat-plan',
  },
  {
    icon: '🔧',
    title: 'Troubleshooting',
    description: 'Quick fixes for the most common problems.',
    to: '/troubleshooting',
  },
];

const phases = [
  {
    phase: 'Phase 1',
    label: 'Outbound product sync',
    description: 'Bookscan → Shopify. Products, prices, stock, metafields.',
    status: 'done',
  },
  {
    phase: 'Phase 2',
    label: 'Inbound order sync',
    description: 'Shopify orders → Bookscan stock deduction.',
    status: 'building',
  },
  {
    phase: 'Phase 2',
    label: 'Desktop GUI',
    description: 'Sync Now button, live log, summary stats.',
    status: 'planned',
  },
  {
    phase: 'Phase 2',
    label: 'Cover images',
    description: 'Local server folder + Open Library fallback.',
    status: 'planned',
  },
];

const statusMeta = {
  done:     { label: 'Complete',    className: styles.statusDone },
  building: { label: 'Building',   className: styles.statusBuilding },
  planned:  { label: 'Planned',    className: styles.statusPlanned },
};

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
                <div className={styles.syncArrowLabel}>every 2 hrs</div>
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

        {/* ── PHASE STATUS ── */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Project status</h2>
          <div className={styles.phaseList}>
            {phases.map((p, i) => {
              const meta = statusMeta[p.status];
              return (
                <div key={i} className={styles.phaseItem}>
                  <div className={styles.phaseLeft}>
                    <span className={styles.phaseTag}>{p.phase}</span>
                    <div>
                      <div className={styles.phaseLabel}>{p.label}</div>
                      <div className={styles.phaseDesc}>{p.description}</div>
                    </div>
                  </div>
                  <span className={`${styles.statusBadge} ${meta.className}`}>{meta.label}</span>
                </div>
              );
            })}
          </div>
        </section>

      </main>
    </Layout>
  );
}
