---
sidebar_position: 1
---

# Architecture Overview

## Sync architecture

```
┌─────────────────────────────────┐
│         Shop Machine            │
│  (Windows PC, always on)        │
│                                 │
│  Z:\bookscan\                   │
│  ├── MASTER.DBF   (products)    │
│  ├── PUBLISHER.DBF (pub data)   │
│  ├── WEBLIST.DBF  (web filter)  │
│  ├── WEBMAINCAT.DBF (categories)│
│  └── WEBSUBCAT.DBF (sub-cats)   │
│                                 │
│  bookscan_sync.py               │
│  ├── reads DBF files            │
│  ├── delta check (MD5 hash)     │
│  └── pushes to Shopify API      │
│                                 │
│  Windows Task Scheduler         │
│  └── runs every 2 hours         │
└────────────────┬────────────────┘
                 │ HTTPS
                 ▼
┌─────────────────────────────────┐
│   Shopify Admin API (2024-01)   │
│   bruce-mckenzie-booksellers    │
│   .myshopify.com                │
└─────────────────────────────────┘
```

## DBF file roles

| File | Records (post May 7 purge) | Purpose |
|---|---|---|
| `MASTER.DBF` | 117,282 | Main product catalog — title, author, price, stock, binding, CSTATUS, DEPARTMENT |
| `PUBLISHER.DBF` | 116,369 | Publisher details — publisher name, pages, pub date, weight, blurb |
| `WEBLIST.DBF` | 38,467 active | Web filter — ISBNs with `INACTIVE=False` are listed on the website |
| `WEBMAINCAT.DBF` | — | Category lookup (e.g. `1 → "Fiction"`) |
| `WEBSUBCAT.DBF` | — | Sub-category lookup (e.g. `4 → "Crime Fiction"`) |

The three files are joined on ISBN to build a complete product record.

## Filtering

After joining, the script applies three filters in order:

1. **WEBLIST membership** — only ISBNs in `WEBLIST` with `INACTIVE=False` proceed
2. **`STATUS_EXCLUDE`** — products with `CSTATUS` in `{OP, RP, RUC}` are skipped
3. **`DEPARTMENT_EXCLUDE`** — products with `DEPARTMENT` in `{AAA, VOU, FRE, TOK}` are skipped

After filtering: ~36,000 products eligible for sync to Shopify.

## Field mapping — Bookscan → Shopify

| Bookscan field | DBF file | Shopify destination |
|---|---|---|
| `ISBN` | MASTER | `variants[0].sku` **+** `bookscan.isbn` metafield |
| `TITLE` | MASTER | `title` |
| `AUTHOR` | MASTER | `bookscan.author` metafield (title-cased: `BRADBURY RAY → Bradbury Ray`) |
| `SELL_PRICE` | MASTER | `variants[0].price` |
| `ONHAND` | MASTER | `inventory_quantity` (via GraphQL `inventorySetOnHandQuantities`) |
| `BINDING` | MASTER | `product_type` (mapped via binding code table) |
| `CSTATUS` | MASTER | `_cstatus-{code}` hidden tag **+** `bookscan.cstatus` metafield |
| `DEPARTMENT` | MASTER | `_dept-{code}` hidden tag **+** `bookscan.department` metafield |
| `PUBLISHER` | PUBLISHER | `vendor` |
| `BLURB` | PUBLISHER | `body_html` |
| `PUB_DATE` | PUBLISHER | `bookscan.publication_date` metafield (DD/MM/YYYY) |
| `PAGES` | PUBLISHER | `bookscan.pages` metafield |
| `WEIGHT` | PUBLISHER | `variants[0].weight` (grams) |
| `WEBMAINCAT` + `WEBSUBCAT` | WEBLIST → lookup | `tags` (customer-facing category names) |

All products are created with `status: draft` until a manual bulk activation.

## Binding code map

| Code | Label | Code | Label |
|---|---|---|---|
| PB | Paperback | CD | CD |
| HB | Hardback | MP | Map |
| TP | Trade Paperback | SP | Spiral |
| BO | Board Book | BC | Box Set |
| PF | Picture Flat | CL | Calendar |
| BB | Big Book | VI | Video |
| PT | Picture Trade | BM | Bookmark |
| ST | Stapled | FC | Flash Cards |
| | | PS | Poster |
| | | SI | Single Item |

Unknown codes pass through as-is to `product_type` (see action item to review with Louisa post-sync).

## Delta sync

On every run, BookKeeper computes an MD5 hash of 8 key fields per product:

```
title | author | publisher | price | stock | binding | pages | tags
```

The `tags` field is the comma-joined list, which includes the hidden `_cstatus-{code}` and `_dept-{code}` tags — so a change to a product's CSTATUS or DEPARTMENT changes the tags string, changes the hash, and triggers an update on the next sync.

Hashes are stored in `sync_state.json`. On the next run, only products whose hash has changed are pushed to Shopify. This keeps API usage minimal — a typical 2-hour run touches only a handful of products (estimated 5–15 min per cycle).

Use `--full` to override delta and push all products.

## Shopify API path choices

The script uses both REST and GraphQL — each chosen where it works most reliably on this store:

| Operation | API path | Why |
|---|---|---|
| Product create | REST `POST /products.json` | Atomic create with image upload + variant + metafields |
| Product update | REST `PUT /products/{id}.json` | Mature REST endpoint |
| Find by SKU | **GraphQL** `productVariants(query: "sku:...")` | REST `/variants.json?sku=` doesn't actually filter server-side; GraphQL does. Critical for idempotency on `--full` restarts. |
| Set inventory | **GraphQL** `inventorySetOnHandQuantities` | REST `/inventory_levels/set.json` and `/connect.json` both return 404 on this store. GraphQL with `inventoryActivate` fallback is reliable. |
| Get location | REST `GET /locations.json` | Trivial, REST is fine |
