---
sidebar_position: 1
---

# Outbound Sync — Bookscan → Shopify

## What syncs

Every product in Bookscan with `WEBLIST.INACTIVE = False` is eligible for sync, subject to status and department filters below. On each run:

1. MASTER.DBF, PUBLISHER.DBF, WEBLIST.DBF are read and joined on ISBN
2. Products with excluded CSTATUS codes (`OP`, `RP`, `RUC`) are skipped
3. Products in excluded departments (`AAA`, `VOU`, `FRE`, `TOK`) are skipped
4. Duplicate ISBNs are deduplicated (keep highest stock, tiebreak on price)
5. Each product is hashed — if the hash matches the last run, the product is skipped
6. Changed products are pushed to Shopify (create or update)
7. Inventory is set separately via the GraphQL `inventorySetOnHandQuantities` mutation

## Status filter

Bookscan's `CSTATUS` field (in MASTER.DBF) controls which books are eligible for the website. Confirmed by Louisa on 2026-05-11, the script excludes the three codes below:

| Status code | Meaning | Syncs? |
|---|---|---|
| `ACT` | Active | Yes |
| `NYP` | Not Yet Published | Yes |
| `TOR` | To Order | Yes |
| `TOS` | Temporarily Out of Stock | Yes |
| `POD` | Print On Demand | Yes |
| `BO` | Back Order | Yes |
| `OP` | Out of Print | **No** |
| `RP` | Reprinting — available but unknown when | **No** |
| `RUC` | Reprint Under Consideration — effectively OP | **No** |

Louisa's workflow: once the last copy of an `OP`/`RP`/`RUC` book is sold, she changes the status in Bookscan's Title Master. The next sync run will skip it entirely.

Bookscan has additional `NOWEB`-flagged codes (`AD`, `OSI`, `NLA`, `NOR`, `PBA`, etc.) which Louisa has chosen *not* to exclude — the practical impact is small (258 books total, only 6 with stock), and any cleanup can be done post-launch via the hidden tag filter described below.

> **Configurable in `bookscan_sync.py`:** `STATUS_EXCLUDE = {"OP", "RP", "RUC"}`.

## Department filter

Bookscan's `DEPARTMENT` field (note: full word, *not* `DEPT`) categorises products by retail department. The following are excluded from sync:

| Department | Reason |
|---|---|
| `AAA` | "Dept To Be Assigned" — uncategorised products, not retail-ready |
| `VOU` | BMB Vouchers — Shopify handles digital vouchers natively |
| `FRE` | Freight — Shopify checkout handles freight, not a sellable product |
| `TOK` | Tokens — same logic as vouchers |

> **Configurable in `bookscan_sync.py`:** `DEPARTMENT_EXCLUDE = {"AAA", "VOU", "FRE", "TOK"}`.

## Hidden tags for post-launch admin filtering

In addition to the public category tags (e.g. `Fiction`, `Crime Fiction`), every product gets two **hidden** tags:

- `_cstatus-{code}` — e.g. `_cstatus-ACT`, `_cstatus-NYP`
- `_dept-{code}` — e.g. `_dept-FIC`, `_dept-CHI`

The leading `_` is a Shopify convention — most themes (including Horizon) suppress underscore-prefixed tags from customer-facing display. They remain visible and filterable in Shopify Admin.

This enables a simple "filter and bulk-action" workflow when Louisa wants to remove products by status or department later — Products → Filter → Tagged with → `_dept-AAA` → select all → Delete.

The same data also lives in `bookscan.cstatus` and `bookscan.department` metafields for structured queries.

## Product status

All synced products are created as **Draft** in Shopify. They go live via a bulk action in Shopify Admin once the first full sync is verified.

## Out-of-stock behaviour

Products with `ONHAND = 0` are still synced and still purchasable. `inventory_policy: continue` means the storefront shows **"Available to order"** rather than blocking purchase. This matches the existing WooCommerce behaviour.

## Deduplication

Bookscan occasionally has 2–3 records for the same ISBN (slightly different titles, one with real stock, one without). BookKeeper keeps the record with the highest `ONHAND` value. If stock is equal, the record with the higher price wins.

Known duplicate ISBNs: see `Project/BMBooks_Duplicate_ISBNs.csv` (13 groups, low priority).

## Rate limiting

BookKeeper sleeps 0.6 seconds between API calls (~1.6 requests/second), safely under Shopify Basic plan's limit of 2 requests/second.

## Author name formatting

Bookscan stores author names in `LASTNAME FIRSTNAME` order (e.g. `WELLS MARTHA`, `DE VRIES JAN`). BookKeeper's `_format_author()` helper reverses this to `FIRSTNAME LASTNAME` for display:

- `WELLS MARTHA` → `Martha Wells`
- `DE VRIES JAN` → `Jan De Vries` (multi-word last names handled — last space is the split point)
- `WELLS, MARTHA` → `Martha Wells` (comma-delimited format also handled)
- `ANONYMOUS` → `Anonymous` (single-word names left as-is)

Author is included in the product hash, so name corrections automatically trigger a re-sync on the next delta run.

## Cover images

BookKeeper resolves cover images in cascade order:

1. `Z:\bookscan\Catalog\LargeImages\` — 257×400px, best quality
2. `Z:\bookscan\Catalog\MediumImages\` — 128×200px fallback
3. `Z:\bookscan\Catalog\` — 64×100px original Ebility thumbnails
4. Shopify CDN no-cover placeholder (`no_cover.jpg`)

Files are named by ISBN (e.g. `9780571347292.jpg`). Ebility auto-downloads images to the catalog folder when a title is added to the web list. As of May 2026, 25,190 products have LargeImages; 9,209 remain on 64×100 catalog thumbnails pending a Nielsen API integration post-launch.
