# BMBooks Workspace

WooCommerce → Shopify migration for [Bruce McKenzie Booksellers](https://bmbooks.co.nz), an independent bookstore at 37 George Street, Palmerston North, New Zealand. Built and maintained with [Claude Code](https://claude.com/claude-code).

**Status:** Pre-go-live. Storefront is built, themed, and synced — waiting on the store owner to confirm a launch date.

## What this is

A full e-commerce migration: ~34,500 products synced hourly from the store's BookScan inventory system (Windows/DBF-based) into Shopify, a custom-themed storefront, genre/category enrichment pulling from BIC bibliographic codes and Google Books, and the tooling to keep it all running without a dedicated engineering team behind it.

## Repo layout

| Path | What's there |
|---|---|
| `Sync/` | Python sync engine — BookScan DBF → Shopify GraphQL, hourly. Genre enrichment, image handling, one-off data-fix scripts. |
| `Shopify_Theme/` | The storefront theme (Liquid, sections, blocks, assets). |
| `Tools/` | Operational scripts and reference docs — CI/git helpers, the category management dashboard, GitHub issue migration tooling, a Python review checklist. |
| `Project/Active/` | Live working docs — action items backlog, release notes, performance baseline. |
| `Project/Archive/` | Decisions and completed work, including ADRs. |
| `Reports/` | Generated audit output (gitignored where it contains customer data). |
| `bookkeeper_docs/` | Docusaurus site documenting the sync tooling for the non-technical store owner. |
| `UAT/` | Pre-launch acceptance testing tooling. |

## Workflow

Feature branches off `main`, PRs with a lightweight template, CI on every PR (secret scanning via gitleaks, Python lint via ruff). Task tracking is split: near-term work lives in [GitHub Issues](../../issues) (milestones = project phases), the long-tail backlog stays in `Project/Active/BMBooks_Action_Items.md` until it's close enough to be worth migrating. Full convention documented in `CLAUDE.md`.

## Why this exists

This project doubles as a real-world case study in running a small but production e-commerce migration almost entirely through an AI coding agent — sync architecture, category taxonomy audits against industry standards (BIC/Thema/BISAC), security hardening, and now a proper team-style GitHub workflow, all developed in direct collaboration with the store owner rather than for her.
