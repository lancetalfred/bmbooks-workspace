---
sidebar_position: 1
slug: /intro
---

# BookKeeper for Shopify

**BookKeeper for Shopify** is a custom Python integration that keeps Bruce McKenzie Booksellers' Shopify store in sync with their Bookscan point-of-sale system.

## What it does

| Direction | What syncs | How often |
|---|---|---|
| Bookscan → Shopify | Products, prices, stock levels, descriptions, cover images | Every 2 hours (delta only) |
| Shopify → Bookscan | Online orders deducted from inventory | Every 2 hours *(Phase 2)* |

## Why it exists

Bruce McKenzie Booksellers uses **Bookscan** as their in-store POS and product catalog (~38,000 products). Bookscan stores all data in FoxPro DBF files (`MASTER.DBF`, `PUBLISHER.DBF`, `WEBLIST.DBF`). The official Shopify connector from Barcode Solutions was never delivered, so BookKeeper is a custom replacement built to run directly on the shop machine.

## Key design decisions

- **Runs on the shop machine** — no cloud server, no external dependencies
- **Delta sync** — only products that changed since the last run are pushed, keeping API usage low
- **Draft products** — all synced products are created as `draft` in Shopify; go-live is a manual bulk action
- **Available to order** — out-of-stock books still allow purchase (`inventory_policy: continue`)
- **GST-exempt** — all products are set `taxable: false` (NZ books are GST-exempt)

## Tech stack

- **Python 3** + `dbfread`, `requests`, `schedule`
- **Shopify Admin REST API** (2024-01)
- **Windows Task Scheduler** for automated 2-hour runs

## Project status

| Phase | Status |
|---|---|
| Phase 1 — Outbound product sync | ✅ Production ready |
| Phase 2 — Inbound order sync | 🔧 In development |
| Phase 2 — Desktop GUI | 🔧 Planned |
