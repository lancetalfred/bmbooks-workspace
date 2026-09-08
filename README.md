# BMBooks Workspace

WooCommerce → Shopify migration for Bruce McKenzie Booksellers — my mother‑in‑law's independent bookshop on the same Palmerston North street for nearly 30 years. Built solo end‑to‑end (architecture, data migration, storefront), with an AI‑assisted engineering workflow — in direct collaboration with the owner.

**Status:** Pre‑go‑live. Storefront is built, themed, and syncing hourly; launch pending the owner's window.

## Highlights

- ~38K products synced from a 133K‑record DBF source via custom Python + Shopify GraphQL; dry run 37,998 with 0 errors
- Six book metafields (author, ISBN, pages, publication_date, status, department) defined via Admin API; fixed 422s by changing page‑count type
- Genre enrichment at scale: BIC‑based mapping with AI generation + independent AI audit; 2,820 titles re‑tagged and validated pre‑launch
- Theme and UX: customized Horizon theme; 75 SEO‑structured collections; owner‑friendly desktop status app
- UAT: NZ checkout test order, Bogus Gateway, order confirmation emails; staging→production workflow documented

## The problem

A 38,000‑book catalog lived in a 1980s DBF format, bridged to the web by a single vendor who stopped responding. Their WooCommerce "integration" was a thin HTTP wrapper around an open‑source library, and the promised Shopify connector didn't exist. There was nothing to wait for.

## What I built

- **Sync engine from scratch**: DBF → Shopify GraphQL, hourly delta sync, image handling, data‑fix scripts; dry run 37,998/0 errors
- **Data model**: six book metafields (author, ISBN, pages, publication_date, status, department); resolved 422 errors from strict typing
- **Taxonomy**: BIC‑driven genre enrichment with verified mappings; 2,820 titles re‑tagged and validated before production
- **Storefront**: customized Horizon theme; 75 collections with structured SEO; Searchanise instant search and synonyms
- **Ops tooling**: desktop status GUI for the owner; release notes, backlog, and UAT checklists in repo

## AI usage — where it actually helped

Built with Claude Code inside VS Code. AI generated the bulk genre mappings; a second, independent AI audit flagged six systematic errors before anything touched production. Also accelerated script scaffolding and performance debugging.

## Tech stack

Shopify (Horizon theme, Liquid, GraphQL Admin API) · Python (DBF parsing, sync engine) · GitHub Actions (secret scanning via gitleaks, Python lint via ruff) · Docusaurus (internal ops docs) · Claude Code

## Repo layout

| Path | What's there |
|---|---|
| `Sync/` | Sync engine, genre enrichment, supporting scripts |
| `Shopify_Theme/` | Storefront theme — Liquid, sections, blocks |
| `Project/Active/` | Live working docs — action items, release notes |
| `Project/Archive/` | Decisions and completed work |
| `Tools/` | CI/git helpers, GitHub issue migration tooling |
| `bookkeeper_docs/` | Docs site for the store owner |
| `UAT/` | Pre‑launch acceptance testing |

## Workflow

Feature branches off `main`, PRs with a lightweight template, CI on every PR (secret scanning via gitleaks, Python lint via ruff). Task tracking is split: near‑term work lives in [GitHub Issues](../../issues) (milestones = project phases), the long‑tail backlog stays in `Project/Active/BMBooks_Action_Items.md`. Full convention documented in `CLAUDE.md`.

## Go‑live plan (what's left)

- Owner's DNS window → cutover
- Customer import at launch
- 301 redirect mapping and post‑launch 404/SEO monitoring
- GMC intentionally deferred; reviews not migrated by design

## Why this exists

This project is a real‑world case study in running a production small‑business e‑commerce migration almost entirely through an AI coding agent — architecture and data migration, category taxonomy work audited against industry standards (BIC/Thema/BISAC), security hardening, and a proper team‑style GitHub workflow — all developed in direct collaboration with the store owner.
