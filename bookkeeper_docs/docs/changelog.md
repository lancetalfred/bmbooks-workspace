---
sidebar_position: 99
---

# Changelog

## Phase 1 — Outbound Sync

### May 28, 2026 — GST fix, AU shipping, taxable backfill script

**bookscan_sync.py — taxable: True on all variants**
- Fixed incorrect `"taxable": False` setting — NZ books are NOT GST-exempt (the comment was wrong). Changed to `"taxable": True`
- Required alongside enabling NZ GST in Shopify tax settings so that AU/international customers automatically see ex-GST prices at checkout
- All new creates and updates from this point forward will have `taxable: true`

**Sync/fix_taxable.py — one-off backfill script**
- New script: iterates all ~34,500 existing Shopify products and sets `taxable: true` on every variant that currently has it as false
- Safe to re-run (skips already-taxable variants), handles 429 rate limiting with Retry-After backoff
- ~5 hour runtime at 0.5s/request — run overnight via `caffeinate -i python3 fix_taxable.py`

**Shopify tax configuration**
- NZ GST enabled at 15% in Settings → Taxes and duties → New Zealand
- "Include sales tax in product price and shipping rate" enabled globally
- Result: NZ customers see GST-inclusive prices; AU/international customers see ex-GST price automatically at checkout (~13% lower). No more manual payment adjustments by Louisa for AU orders.

**AU shipping — flat rate set**
- Removed DHL Express carrier-calculated rate (not available on Basic monthly plan)
- Added $12 NZD manual flat rate as placeholder
- AU checkout confirmed working — shipping shows, GST correctly excluded
- Rate to be refined using WooCommerce AU order history

### May 27, 2026 — Toast notifications, richer log detail, order fulfillment doc

**Windows toast notifications**
- `bookscan_sync.py` now fires a Windows toast notification at sync start, sync complete, and on errors (⚠ with error count)
- Uses `winotify` (added to `requirements.txt`) with `bookkeeper.ico` as the notification icon
- Wrapped in `try/except` — silent no-op on Mac or if winotify is absent; sync continues regardless

**Richer log detail — Created and Updated items**
- `sync_state.json` extended: now stores a `fields` dict alongside `hashes` — a snapshot of key fields per ISBN for diff comparison (~10MB for full catalog, acceptable)
- New log lines emitted after each Created/Updated event:
  - `DETAIL_C [isbn] Author: ... | Publisher: ... | Price: $X | Stock: N` — all synced fields for new products
  - `DETAIL_U [isbn] Price: $X → $Y | Stock: N → M` — only changed fields for updates (diff against previous snapshot)
- First run after this update: Updated items show "no field changes detected" (no previous snapshot). Diffs appear from the second run onwards.
- `bookkeeper_gui.py` updated: DETAIL lines parsed silently (not shown in activity log), detail stored against the matching ISBN in Created/Updated lists
- Created popup: ISBN / Title / **Details** columns
- Updated popup: ISBN / Title / **Changed** columns

**New doc: order fulfillment**
- `bookkeeper_docs/docs/sync/order-fulfillment.md` — technical reference for the manual order workflow until Phase 2 is live
- Covers: Shopify fulfillment steps, Bookscan web sale entry, field mapping table, in-store pickup, edge cases, Phase 2 note

### May 27, 2026 — BookKeeper deployed to shop machine; automated sync live

**BookKeeper folder moved to Z:\ (network drive)**
- All BookKeeper files relocated from `C:\BookKeeper\` to `Z:\BookKeeper\` for backup resilience — survives local HDD failure
- `sync_state.json` carried across — delta sync state preserved, no full re-sync required

**bookscan_sync.py — path hardening**
- `STATE_FILE` and `LOG_FILE` changed from relative paths to absolute (`os.path.dirname(__file__)`) — consistent with `LOCK_FILE`. Prevents incorrect file placement when Task Scheduler runs from a different working directory
- Lock file cleanup moved into `try/finally` — guaranteed removal even if sync crashes mid-run. Previously the lock file could persist indefinitely after an unhandled exception, leaving the GUI stuck on "Running"

**BookKeeper GUI confirmed working on shop machine**
- `bookkeeper_gui.py` deployed to `Z:\BookKeeper\` — first live test passed: green dot, delta sync mode, log polling, Created/Updated/Errors counts, clean idle state after completion
- `Sync Now.bat` shortcut placed on Louisa's desktop
- `bookkeeper.ico` generated (`create_icon.py` + Pillow) — BMBooks purple background, Shopify green sync arrows, "BK" monogram

**Windows Task Scheduler configured**
- Task: `BookKeeper Sync` — runs `python Z:\BookKeeper\bookscan_sync.py --once` every hour
- `--once` flag ensures the script runs and exits cleanly (no internal scheduler loop conflicting with Task Scheduler)

### May 25, 2026 — Navigation, collections, homepage, gift card, BookKeeper GUI

**Navigation — dropdown menus live**
- 7 top-level nav items now have sub-category dropdowns: Fiction, Children's, Non-Fiction, The Arts, New Zealand, Manawatū, Gifts & Stationery
- Sub-categories ranked by product count (top ~6 per parent)
- Built via Shopify Admin → Content → Menus (no theme code required — Horizon renders dropdowns natively)

**Collections — expanded to 75**
- 24 new sub-collections added to `create_collections.py` and created via API
- Covers History & Politics, Well Being, Sciences, Travel, Biographies, Sport, The Garden sub-categories
- **Manawatū parent collection** added (`/collections/manawatu`, `tag("The Manawatu")`) — 155 products; standalone nav item between New Zealand and Gifts & Stationery

**Homepage — featured collections built**
- 6 sections: New Releases (Manual), Bestsellers (Best selling sort), Fiction, Kids, New Zealand (Newest), Gifts & Stationery
- Bestsellers tag confirmed active: Louisa maintains this tag in Bookscan — `tag("Bestsellers")` smart collection auto-populates

**Gift card — fixed and styled**
- Denomination selector (dropdown) now working — added Variant picker block in theme editor
- Removed availability/shipping status message (was showing incorrect "We'll order this" badge)
- Custom CSS: `label[for^="Option-"]` targets denomination label for bold styling; `.variant-option__select` for border

**Custom CSS — full current ruleset:**
```css
.footer-content .menu__heading__default { font-weight: 700; font-size: 1em; }
.add-to-cart-button { max-width: 50ch; }
.resource-list__carousel .card-gallery { aspect-ratio: 700 / 1077 !important; }
.resource-list__carousel .product-media__image { object-fit: cover !important; width: 100%; height: 100%; }
.variant-option__select { border-color: rgba(0,0,0,0.4); border-width: 1.5px; border-radius: 4px; }
label[for^="Option-"] { font-weight: 700; color: #1A0A2E; }
```

**bookscan_sync.py — minor additions**
- `--once` flag: runs sync once and exits (no scheduler loop) — for Task Scheduler and GUI use
- Lock file (`sync.lock`): created at start of `run_sync()`, deleted on completion — prevents concurrent runs

**New files: BookKeeper GUI**
- `Sync/bookkeeper_gui.py`: tkinter dashboard — status dot, sync mode label (delta/full), progress bar, clickable Created/Updated/Errors counts (drill-down popup shows ISBN + title per item), activity log, Sync Now button with lock-file guard
- `Sync/Sync Now.bat`: double-click launcher for Louisa's desktop (`cd /d Z:\BookKeeper && python bookkeeper_gui.py`)
- **Status**: Built and syntax-verified. Log polling not yet confirmed working on Mac (macOS system Tk rendering issue). Deploy to shop machine for final test.

**Emails sent to Louisa**
- Binding codes: 28 unknown codes, ~390 products, top 10 listed with guesses. Asked Louisa to confirm label + whether each should show on site.

### May 19, 2026 — Product page design improvements + author name fix

- **Bug:** Bookscan stores author names as `LASTNAME FIRSTNAME` (e.g. `WELLS MARTHA`). The previous `.title()` call capitalised correctly but didn't reorder — customers saw "Wells Martha" on product pages.
- **Fix:** Replaced `.title()` with `_format_author()` helper in `bookscan_sync.py`. Logic: split on last space → treat final token as first name, remainder as last name. Multi-word last names (`DE VRIES JAN` → `Jan De Vries`) and comma-delimited format (`WELLS, MARTHA`) both handled. Single-word names (`ANONYMOUS`) returned as-is.
- **Deployment:** Copy updated `bookscan_sync.py` to `C:\BookKeeper\` on the shop machine. Author is included in `product_hash()`, so the next regular delta sync will automatically detect and push corrected names for all affected products — no `--full` flag needed.

**Product page — live Shopify improvements:**
- Layout/spacing fixed via product information section settings in Horizon theme editor
- Wishlist button restyled to secondary via Wishlist Plus app Advanced Settings (colour overrides in app dashboard)
- Built-in Horizon Inventory block tested — does not work for BMBooks. When `inventory_policy: continue` and stock = 0, it shows "In Stock" (incorrect). Decision: replace with Custom Liquid block.

**Availability row design (mockup):**
- `Memo/product-page-mockup.html` updated with BookHero-inspired availability row: status badge (left) + shipping info + icon (right), all on one line.
- In Stock: green badge (#EAF5EE / #2D7A4F) · "Ready to ship · Ships within 1–2 business days · NZ main centres 2–5 working days"
- Available to Order: yellow badge (#FFFCE0 / #8A6B00) · "We'll order this for you · Allow 1–2 business days to process · NZ main centres 2–5 working days"
- Pending: Louisa sign-off on "Available to Order" copy + supplier lead time confirmation → then implement as Custom Liquid block on live store.

### May 14–15, 2026 — Production backfill complete; dedupe in progress

- **All products uploaded.** Shopify admin shows 37,577 products (includes ~40 duplicates from restart cycles; dedupe running).
- **sync_state.json issue discovered:** The shop machine's `sync_state.json` was not preserved across the multiple interrupted runs. On restart, the script correctly reported "Mode: delta sync" but found no prior hashes, so processed all 36,822 products as updates rather than skipping unchanged ones. This is safe (idempotent) but slow — the full reprocess was stopped early once Shopify confirmed all products were already uploaded. `sync_state.json` will repopulate correctly on the next completed run.
- **`start /b` approach adopted** for running the sync manually: `start /b python bookscan_sync.py` launches the script as a background process that survives Chrome Remote Desktop session disconnects. Previous runs were killed when the CRD session dropped (cmd window closed = process dies). From now on, use `start /b` for any manual run; check progress by tailing the log.
- **Shopify product count discrepancy:** Shopify admin shows 37,577 but the dedupe script's API query returned 34,532 (gap of ~3,045). Under investigation — likely archived products not returned by default `GET /products.json`. Full CSV export from Shopify admin being analysed to confirm.
- **Dedupe dry run (May 15):** 40 extra products across 32 SKUs — the early CDs that were created 3× before the GraphQL `find_by_sku` fix landed. `dedupe.py --execute` running now.
- **BookKeeper GUI planned** (`bookkeeper_gui.py`): tkinter dashboard to replace `Sync Now.bat`. Features: live sync status (RUNNING/IDLE/STOPPED UNEXPECTEDLY), progress bar + time-to-completion, Created/Updated/Error counts, error list, Sync Now button with duplicate-run protection, 30-second health check loop, Windows notifications on completion/error/unexpected stop. Auto-refreshes via log file polling every 2 seconds. Survives CRD disconnects. Replaces the simple `.bat` shortcut originally planned. Requires `psutil`.

### May 12, 2026 — Production backfill in progress
- Chrome Remote Desktop access to shop machine granted (Belinda)
- Python 3.14 + dependencies (dbfread, requests, schedule) installed on shop machine
- Script deployed to `C:\BookKeeper\bookscan_sync.py`; reads DBFs from `Z:\bookscan` (mapped drive)
- 6 Shopify metafield definitions created in live store: bookscan.author, bookscan.isbn, bookscan.pages, bookscan.publication_date, **bookscan.cstatus**, **bookscan.department**
- Dry run on shop machine confirmed: 36,766 web products, 1,585 skipped via CSTATUS, 55 skipped via DEPARTMENT
- **Production run started 07:50 NZ** — ~308 non-book products synced, then 391 consecutive 422 errors at the 9780008xxxx range
- Root cause #1: `bookscan.pages` was defined as Integer type but the script sends it as a string. Shopify silently rejected every payload containing a Pages metafield. **Fix:** deleted and recreated the definition as Single line text (Shopify doesn't allow type changes in place).
- Root cause #2: `find_by_sku` was using Shopify REST `/variants.json?sku=` which doesn't actually filter server-side — it returns the 50 most-recently-created variants and matches Python-side. For a store with >50 variants this silently misses older products and creates duplicates on every full-sync restart. **Fix:** rewrote `find_by_sku` to use GraphQL `productVariants(query: "sku:...")` which filters reliably server-side.
- Root cause #3: REST `inventory_levels/set.json` and `connect.json` both return 404 on this store. Switched `set_inventory` to GraphQL `inventorySetOnHandQuantities` with `inventoryActivate` fallback.
- Root cause #4 (open): GraphQL inventory mutations return *"The specified inventory item could not be found"* on the ~344 products created during the buggy early runs — the variant exists, `inventoryItem.id` field returns a gid, but the gid doesn't resolve. Diagnosis deferred until post-backfill via `Sync/diagnose_inventory.py`. Non-fatal — affects only the Update path on pre-existing products; new products created via `create_product` get inventory set inline and work correctly.
- ~40 duplicate products accumulated across multiple restart cycles before the GraphQL find_by_sku fix landed (confirmed by dedupe dry run May 15: 40 extra across 32 SKUs). Cleanup script `Sync/dedupe.py` written and ready to run post-sync.
- New scripts: `Sync/dedupe.py` (find + delete duplicate SKUs, keeps most-recently-updated), `Sync/diagnose_inventory.py` (read-only; queries variant + inventoryItem state for known-failing SKUs)
- Production run continuing — currently ~43% through. Expected completion ~36–50h from now. All 422 errors gone. GraphQL find_by_sku holding; no new duplicates being created.

### May 11, 2026 — Sync hardening + Louisa sign-off
- Louisa email responses (Questions A–D from the 2026-05-07 draft):
  - **A**: Exclude `OP`, `RP`, `RUC` only (more permissive than the full NOWEB-flag rule)
  - **B**: Spot-check pending
  - **C**: Anomaly records — pending sign-off; will handle post-sync via tag/admin filter
  - **D**: Confirmed `VOU`, `FRE`, `TOK`, `AAA` department exclusions (no response yet on `GFS`, `SPE`, `XXX`, `MAG`, blank-dept)
- `AD` code investigation — 1,159 books, only 240 active in WEBLIST, only **6 with stock**. Sample compiled for Louisa.
- Field-name bug caught in analysis: the code was querying `DEPT` (a phantom field) instead of `DEPARTMENT`. Corrected — every NOWEB-flagged record was returning "blank department" before the fix, leading to a false correlation. Confirmed AAA has 2,754 records, blank-department has only 145 (none active in WEBLIST).
- Follow-up email drafted asking Louisa about extending the rule to follow Bookscan's NOWEB flag across all 16 codes (Question E)
- `bookscan_sync.py` updates:
  - `STATUS_EXCLUDE = {"OP", "RP", "RUC"}` — confirmed status filter
  - `DEPARTMENT_EXCLUDE = {"AAA", "VOU", "FRE", "TOK"}` — confirmed department filter
  - Added `_cstatus-{code}` and `_dept-{code}` hidden tags (underscore prefix suppresses customer-facing display per Shopify convention) — enables Louisa's "filter and bulk-delete" workflow in admin for post-launch cleanup
  - Added `bookscan.cstatus` and `bookscan.department` metafields (mirror of the hidden tags)
- **Architectural reversal**: removed the OOP CSV blocklist from `bookscan_sync.py` (added May 7). Louisa's team is now manually triaging the BookData OOP audit per-book — setting CSTATUS to `OP` for genuine OOP, leaving as `ACT` for residual-stock copies. The CSV is retained at `Sync/BMBooks_OutOfPrint.csv` as a working document for her team but is no longer consulted by the script. Trade-off accepted: ~445 residual-stock OOP books will sync to Shopify and may briefly display "Available to order" when their last copy sells.
- Action items file: dedupe pass to consolidate duplicate entries

### May 7, 2026 — Status code + department audit, OOP cleanup CSV
- Comprehensive email to Louisa (`Memo/2026-05-07_louisa-email-draft.md`) — full CSTATUS table mapped to Bookscan's NOWEB flag, 140 anomaly records identified, department exclusion table, real-book examples per code so Louisa can spot-check against Bookscan
- Corrections from May 6 call (after data audit against fresh MASTER): `ATT → ACT`, `NYPA → NYP`, **`RMC → RUC`**, `MLIP` and `TLE` not found in data
- Master record count: before purge 133,752 → after purge 117,282 (−12%, almost all old `ACT` records)
- BookData OOP audit cross-referenced against new MASTER:
  - 3,258 OOP ISBNs flagged
  - 448 hard-deleted from MASTER (~14%)
  - 885 re-statused to OP (would be caught by planned CSTATUS filter)
  - **1,463 still marked ACT** in Bookscan + active in WEBLIST (the residual gap)
  - Of those 1,463: **445 have stock on hand** — confirmed by Louisa as residual store copies (genuinely OOP titles where 1–2 physical copies remain), not real reorders
- `Reports/BMBooks_OOP_Still_Active_2026-05-07.csv` generated (1,463 rows) for Louisa's interns to spot-check
- `bookscan_sync.py` updates (later reversed 2026-05-11):
  - Added OOP CSV blocklist filter with `OOP_BLOCKLIST_PATH` config
  - Added `--list-blocked` audit flag with CSTATUS-grouped summary + "possible reorder" candidates flagged
- Shopify Payments bank account received from Louisa: ANZ Bank ****4200, daily payouts, NZD
- Customer billing statement name: "Bruce McKenzie Books" (20 chars) rejected by Shopify's 19-char limit → set to **"BMBooks"**
- Return & Refund + Shipping policies signed off in Shopify
- Cancelled scope: full wordmark logo (sticking with B monogram), high-res store photo (placeholder retained)

### May 6, 2026
- e-Bility release notes reviewed (v5.00.65a → 6.00.02g) — key findings:
  - `CSTATUS` field in MASTER.DBF confirmed as Bookscan's status field
  - Status codes that must be excluded from sync: `OP` (out of print), `RP` (reprinting), `RMC` (under consideration)
  - Department filter needed: `AAA` (variable pricing — Louisa's request). Additional departments TBC via email.
  - Additional available fields not yet synced: series, illustrator, dimensions, web keywords
- Louisa call — status code workflow confirmed:
  - Louisa changes status to OP in Title Master once last copy of a book is sold
  - RP = reprinting, available later but unknown when — same behaviour as OP on website
  - RMC = under consideration for reprint, basically OP — same behaviour as OP
- Status filter and department filter not yet implemented in bookscan_sync.py — pending CSTATUS field verification on shop machine and Louisa's email confirming full list
- Phase 1 sync paused mid-run — Louisa running Bookscan purge of zero-stock/unordered books
  - 469 partial draft products created (no images) — to be deleted from Shopify Admin before restart
  - Task Scheduler and Sync Now.bat not yet set up — to do immediately after successful restart

### May 5, 2026
- First full sync running on shop machine — 38,490 products, cover images from Z:\bookscan\catalog
- Phase 2 architecture confirmed via live DBF inspection on shop machine:
  - WEBORDHD.DBF + WEBORDLN.DBF confirmed as the correct write targets (not MASTER.ONHAND)
  - Both tables currently empty — WooCommerce middleware is gone, this is what Louisa fills manually
  - Shopify order fields map cleanly to both tables
  - Writing to these tables lets Bookscan process orders natively — NielsenBookScan, EDI, financials all work correctly
  - DBF write library needed: `dbf` (pip install dbf)
- inbound.md rewritten with confirmed architecture and full field mapping
- Chrome Remote Desktop permanent access established on shop machine (bmbooksellers@gmail.com)

### May 3, 2026
- Lance added mobile to bmbooksellers@gmail.com 2FA — live store now accessible independently
- PC06 metafield definitions created via API (`create_metafields.py`) — bookscan.author, bookscan.isbn, bookscan.pages, bookscan.publication_date
- Shopify Payments confirmed accepting payments; payouts pending bank account (Louisa to provide account number Tuesday)
- Package profiles created: small paperback, standard hardback, large/multiple (dimensions to confirm with Louisa pre-go-live)
- 11 collections created with SEO copy via API (`create_collections.py`): 9 smart (Fiction, Young Adult, Kids, Non-Fiction, The Arts, New Zealand, Gifts & Stationery, New Releases, Bestsellers) + 2 custom (Staff Picks, NZ Authors)
- Main navigation updated: 7 category items, Home removed
- Footer Browse menu created and assigned
- Homepage: New Releases, Fiction, Kids, Staff Picks collection sections added (carousel, Heading 3)
- Search empty state set to Fiction
- 9 URL redirects created for WordPress category → Shopify collection mapping
- BMBooks_The_Story.md created — project narrative for job interviews and posts

### April 30, 2026
- Louisa order fulfillment workflow confirmed via conversation:
  - Every Shopify order requires Louisa to manually enter a full **web sale** in Bookscan — customer name, delivery address, and every order line. Not just a stock adjustment: a complete sale record.
  - Current stock flow: customer buys online → Louisa manually enters web sale in Bookscan → 2-hour outbound sync picks up reduced stock → Shopify updates
  - International orders frequently fall through on WooCommerce (no calculated rates at checkout) — Shopify + DHL fixes this
  - Bookscan has an existing **import mechanism** (used for title imports) — potential lower-risk path for Phase 2 sales import vs. direct DBF writes
- Phase 2 inbound sync priority escalated: the manual order re-keying is the #1 ongoing daily cost; it grows with online order volume
- Architecture note: inbound sync must create proper Bookscan **sale records** (not just deduct ONHAND directly) to preserve NielsenBookScan reporting and Bookscan financials
- inbound.md updated to reflect full scope of current manual process and the import mechanism discovery

### May 2, 2026
- UAT S7–S13 completed (dev store)
  - Edge cases (TC35–TC40): all PASS — $0 price, 0 stock, no description, no publisher, unknown binding, duplicate ISBN dedup
  - Error handling (TC41–TC43): all PASS — inventory 404 non-fatal, batch continues after error, state file saved
  - Log file (TC44–TC46): all PASS — history, per-product lines, summary line
  - End-to-end purchase (TC47–TC52): TC47 conditional pass (title search works; author/ISBN need Searchanise), TC48–TC50 deferred to live store (shipping not configured on dev), TC51–TC52 PASS (test order + confirmation email)
  - TC53–TC55 deferred to Phase 2 (inbound order sync not yet built)
  - Searchanise (TC56–TC58) deferred to live store; TC59 PASS (smart collection auto-populates from tags)
  - Production config (PC01–PC08): PC01, PC02, PC04, PC07, PC08 PASS; PC06 pending (metafields); PC03, PC05 pending shop machine
- Live store custom app created via Dev Dashboard (legacy custom apps deprecated Jan 1 2026)
- `get_token.py` created — one-time OAuth script to retrieve permanent shpat_ token
- `bookscan_sync.py` updated: SHOPIFY_STORE_URL → live store, MAX_PRODUCTS → None
- Production dry run confirmed: 37,998 products, 0 errors against live store
- Shopify account clarification: live store = bmbooksellers@gmail.com; dev store = lance.t.alfred@gmail.com
- Category navigation structure finalised (Option 3 revised — benchmarked against Whitcoulls + Booktopia): Fiction, Young Adult, Kids, Non-Fiction, The Arts, New Zealand, Gifts & Stationery
- Smart collections decision: Bookscan MAINCAT/SUBCAT tags auto-assign products; editorial collections (Staff Picks, NZ Authors, etc.) curated by Louisa
- "Sync Now.bat" desktop shortcut planned for shop machine (manual sync trigger for Louisa)
- Walk Louisa through order fulfillment workflow added as pre-go-live action item
- Known gaps identified: 390 products with unknown binding codes (pass through as-is, review with Louisa); vendor defaults to store name when publisher blank (post-UAT bulk update needed)

### April 28–30, 2026
- Cover image sync added to `bookscan_sync.py` — reads from Z:\bookscan\catalog\ (Ebility auto-downloads on web-list assignment)
- `published_scope: "web"` fix — products were defaulting to POS-only
- `check_isbn.py` created — reusable UAT field verification script
- Publication date format changed to DD/MM/YYYY
- No-cover placeholder uploaded to Shopify CDN
- UAT TC08–TC34 completed and passed

### April 23, 2026
- Session context migrated to VS Code workspace
- Docusaurus documentation site scaffolded (BookKeeper for Shopify)

### April 13–14, 2026
- `bookscan_sync.py` production-ready — confirmed against dev store
- Auto-tagging added: products tagged with WEBMAINCAT + WEBSUBCAT
- Deduplication added: duplicate ISBNs resolved by highest stock
- Vendor fallback fixed: blank vendor instead of "BMBooks" for missing publishers
- Dev store batch test: 162 products refreshed, all fields verified
- Author name fixed: BRADBURY RAY → Bradbury Ray (.title() applied)

### April 13, 2026 (evening)
- Bookscan DBF structure fully mapped (MASTER, PUBLISHER, WEBLIST, WEBMAINCAT, WEBSUBCAT)
- Field mapping confirmed: stock in MASTER.ONHAND, publisher/blurb/pages in PUBLISHER.DBF
- `bookscan_sync.py` rewritten as production script with 3-file join and delta sync
- Local test: 38,013 products loaded, 37,923 with price, 9,857 in stock
- Dev store confirmed: Fahrenheit 451 verified with all 4 metafields

### April 12, 2026
- Bookscan architecture mapped via screen share
- Decision confirmed: custom Python sync script (Option B) — Shanti bypassed entirely
- `shopifylibrary.dll` confirmed absent from shop machine
- Shopify POC confirmed working: `poc_shopify_sync.py` tested against dev store

### April 9, 2026
- Shopify gift cards configured: $30, $40, $50, $60, $80, $100
- DHL international shipping confirmed on Basic plan
- WooCommerce order history exported: 2,396 orders, $137,344 NZD

### April 8, 2026
- BookData out-of-print audit: 37,076 ISBNs checked, 3,258 out-of-print identified
- WooCommerce customer export: 2,123 customers

### April 7, 2026
- Louisa call: Shopify Payments docs submitted, brand colour #1A0A2E confirmed
- Email domain authentication (DKIM/SPF/DMARC) added to Cloudflare

## Phase 0 — Shopify Store Setup

### March–April 2026
- Horizon theme configured: #1A0A2E, Playfair Display / Open Sans
- All pages created: Homepage, About Us, Visit Us, Contact Us
- Shipping zones configured: NZ + International DHL
- Searchanise Search & Filter installed and configured
- Email templates branded
- Google Analytics connected
- Google Business Profile updated
