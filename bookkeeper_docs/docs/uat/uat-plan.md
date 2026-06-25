---
sidebar_position: 1
---

# UAT Plan
**Script under test:** `Sync/bookscan_sync.py`
**Test environment:** Dev store — bmbooks-dev.myshopify.com
**DBF source:** `Sync/SABSSAVE/` (local copy of shop machine DBF files)
**Last updated:** April 2026

---

## How to Use This Document

Work through each section in order. For each test case:
- Follow the **Steps** exactly
- Compare actual output against **Expected Result**
- Mark **Pass / Fail / Skip** in the result column
- Add notes for anything unexpected

Do not proceed to production config until every test in sections 1–9 passes.

---

## Pre-Test Checklist

Before running any test cases, confirm the following:

| # | Check | Done? |
|---|---|---|
| P1 | Python 3.x installed (`python --version`) | |
| P2 | Dependencies installed (`pip install -r requirements.txt`) | |
| P3 | `SABSSAVE/` folder contains MASTER.DBF, PUBLISHER.DBF, WEBLIST.DBF, WEBMAINCAT.DBF, WEBSUBCAT.DBF | |
| P4 | `SHOPIFY_STORE_URL` in script = `bmbooks-dev.myshopify.com` | |
| P5 | `SHOPIFY_ACCESS_TOKEN` in script = dev store token | |
| P6 | `DBF_BASE_PATH` in script points to `SABSSAVE/` folder | |
| P7 | `MAX_PRODUCTS` = 20 (leave as-is for UAT) | |
| P8 | Dev store is accessible and empty (or note how many products are already in it) | |
| P9 | `sync_state.json` deleted or does not exist (clean slate for first run) | |

---

## Section 1 — Dry Run

Verify the script can read all DBF files and report what it would sync, without making any API calls.

| ID | Test | Steps | Expected Result | Result | Notes |
|---|---|---|---|---|---|
| TC01 | Dry run executes without errors | Run: `python bookscan_sync.py --dry-run` | Script runs to completion with no Python exceptions | | |
| TC02 | Correct product count logged | Check log output after DBF load | Log shows ~38,013 active web ISBNs | | Exact number may vary with your local DBF copy |
| TC03 | Deduplication logged if duplicates exist | Check log after product load | Log shows "Deduped X duplicate ISBN record(s)" if any found, or silently skips if none | | |
| TC04 | Capped to MAX_PRODUCTS | Check log output | Log shows "MAX_PRODUCTS=20 — capping to first 20 products" | | |
| TC05 | Products listed in dry run output | Check log output | Log lists up to 20 products with ISBN, title, price, stock | | |
| TC06 | No API calls made | Check log — no "Created" or "Updated" lines | Only dry run log lines appear — no Shopify API activity | | |
| TC07 | State file NOT created on dry run | Check folder after run | `sync_state.json` does not exist | | |

---

## Section 2 — First Sync (Full Run, 20 Products)

Run the sync for the first time against the dev store. Verifies create path works end to end.

| ID | Test | Steps | Expected Result | Result | Notes |
|---|---|---|---|---|---|
| TC08 | First run completes without fatal errors | Run: `python bookscan_sync.py` | Script runs to completion. Summary line shows Created: >0, Errors: 0 (or very low) | | |
| TC09 | Products appear in dev store | Open Shopify Admin > Products | 20 products visible in product list | | |
| TC10 | Products created as Draft | Check status of any product in Shopify | Status = Draft (not Active) | | |
| TC11 | State file created after first run | Check folder | `sync_state.json` exists with `last_run` timestamp and 20 ISBN hashes | | |
| TC12 | Log file created | Check folder | `bookscan_sync.log` exists with full run output | | |

---

## Section 3 — Product Field Verification

Pick 2–3 products from the dev store and verify every field maps correctly from Bookscan.

**Test product 1 ISBN:** _________________ (pick one you can look up in Bookscan)
**Test product 2 ISBN:** _________________ (pick one with known stock > 0)
**Test product 3 ISBN:** _________________ (pick one with stock = 0)

| ID | Field | Where to Check in Shopify | Expected Value | Actual Value | Pass/Fail |
|---|---|---|---|---|---|
| TC13 | Title | Product > Title | Matches MASTER.TITLE (stripped) | | |
| TC14 | SKU | Product > Variants > SKU | Matches ISBN exactly | | |
| TC15 | Price | Product > Variants > Price | Matches MASTER.SELL_PRICE to 2 decimal places (e.g. $22.99) | | |
| TC16 | Product Type | Product > Product type | Human-readable binding (e.g. "Paperback" not "PB") | | |
| TC17 | Vendor | Product > Vendor | Publisher name from PUBLISHER.DBF, or blank if missing | | |
| TC18 | Description | Product > Description | Matches PUBLISHER.BLURB (or MASTER.MTABSTRACT as fallback), or empty | | |
| TC19 | Tags | Product > Tags | Two tags: main category + sub-category (e.g. "Fiction, Science Fiction and Fantasy") | | |
| TC20 | Weight | Product > Variants > Weight | Weight in grams from PUBLISHER.DBF | | |
| TC21 | Taxable | Product > Variants > Taxable | Unchecked (false) — NZ books are GST-exempt | | |
| TC22 | Requires shipping | Product > Variants | Checked (true) | | |
| TC23 | Author metafield | Product > Metafields > bookscan.author | Author name in Title Case (e.g. "Bradbury Ray" not "BRADBURY RAY") | | |
| TC24 | ISBN metafield | Product > Metafields > bookscan.isbn | Matches ISBN | | |
| TC25 | Pages metafield | Product > Metafields > bookscan.pages | Page count as string, or absent if 0 | | |
| TC26 | Publication date metafield | Product > Metafields > bookscan.publication_date | ISO date string (e.g. "2012-09-18"), or absent if missing | | |

---

## Section 4 — Inventory Verification

| ID | Test | Steps | Expected Result | Result | Notes |
|---|---|---|---|---|---|
| TC27 | In-stock book shows correct quantity | Check Inventory tab for test product 2 (stock > 0) | Inventory = MASTER.ONHAND value | | |
| TC28 | Out-of-stock book shows 0 inventory | Check Inventory tab for test product 3 (stock = 0) | Inventory = 0 | | |
| TC29 | Out-of-stock book allows purchase | Check test product 3 variant settings | inventory_policy = "continue" (shows as "Available to order" on storefront) | | |

---

## Section 5 — Idempotency (No-Change Run)

Run the sync a second time immediately without changing anything in Bookscan. Verifies the delta logic skips unchanged products.

| ID | Test | Steps | Expected Result | Result | Notes |
|---|---|---|---|---|---|
| TC30 | Second run skips all unchanged products | Run: `python bookscan_sync.py` immediately after TC08 | Log shows "Delta: 0 changed, 20 unchanged — skipping unchanged" | | |
| TC31 | No creates or updates on second run | Check log summary | Summary shows Created: 0, Updated: 0, Errors: 0 | | |
| TC32 | State file last_run timestamp updated | Check `sync_state.json` | `last_run` timestamp is newer than after first run | | |

---

## Section 6 — Delta Sync (Change Detection)

Simulate a price or stock change and verify only the changed product is pushed.

| ID | Test | Steps | Expected Result | Result | Notes |
|---|---|---|---|---|---|
| TC33 | Manually edit sync_state.json to simulate a change | Open `sync_state.json`, change the hash value for one ISBN to "changed" | File saved with modified hash | | This simulates Bookscan data changing between runs |
| TC34 | Only the modified product is processed | Run: `python bookscan_sync.py` | Log shows "Delta: 1 changed, 19 unchanged" — only 1 product updated | | |
| TC35 | --full flag overrides delta and processes all | Run: `python bookscan_sync.py --full` | Log shows "Processing all 20 products" — all 20 updated | | |

---

## Section 7 — Edge Cases

These test boundary conditions that could cause silent errors in production.

| ID | Test | Steps | Expected Result | Result | Notes |
|---|---|---|---|---|---|
| TC36 | Product with $0 price syncs without error | Find an ISBN in SABSSAVE with SELL_PRICE = 0, confirm it syncs | Product created with price $0.00, no crash | | |
| TC37 | Product with 0 stock syncs and allows ordering | Find ISBN with ONHAND = 0 | Product created, inventory = 0, inventory_policy = continue | | |
| TC38 | Product with no description syncs | Find ISBN where BLURB and MTABSTRACT are empty | Product created with empty body_html, no crash | | |
| TC39 | Product with no publisher syncs | Find ISBN where PUBLISHER.DBF has no publisher name | Vendor field is blank (not "BMBooks"), no crash | | |
| TC40 | Product with unknown binding code | Find ISBN with binding code not in BINDING_MAP (if any) | product_type = raw binding code (passes through), no crash | | |
| TC41 | Product with no category tags | Find ISBN where WEBMAINCAT/WEBSUBCAT resolve to nothing (if any) | Tags field is empty string, no crash | | |
| TC42 | Author name correctly title-cased | Check a product where AUTHOR is all-caps in DBF | bookscan.author metafield shows Title Case, not ALL CAPS | | |
| TC43 | Duplicate ISBNs: higher stock wins | Inspect `sync_state.json` or log for duplicate ISBN handling | Dedup log line appears; product with higher stock value was used | | Verify using BMBooks_Duplicate_ISBNs.csv for known duplicates |

---

## Section 8 — Error Handling

Verify the script is resilient to individual failures.

| ID | Test | Steps | Expected Result | Result | Notes |
|---|---|---|---|---|---|
| TC44 | Inventory 404 is non-fatal | Check log for any inventory warnings from TC08 run | Warning logged as "Inventory update non-fatal: ..." — sync continued normally | | Dev store can trigger this — expected behaviour |
| TC45 | Individual product error doesn't stop batch | Manually set ACCESS_TOKEN to a bad value for 1 second mid-run, or check log from a run with known errors | Error logged for that product, sync continues to next product | | May be easier to verify by reviewing log from TC08 if any errors occurred |
| TC46 | State file still saved when errors occur | After a run with errors, check sync_state.json | File exists and contains hashes for products that succeeded | | |

---

## Section 9 — Log File Review

| ID | Test | Steps | Expected Result | Result | Notes |
|---|---|---|---|---|---|
| TC47 | Log captures full run history | Open `bookscan_sync.log` | All runs appended chronologically with timestamps | | |
| TC48 | Log includes per-product lines | Review log | Each Created/Updated/Error line includes ISBN and title | | |
| TC49 | Summary line present at end of each run | Review log | Each run ends with "Sync complete — Created: X Updated: X Errors: X" | | |

---

## Section 10 — Production Config Checklist

**Only complete this section after all above tests pass.**

This is the changelist required before pointing the script at the live store.

| # | Change | File | From | To | Done? |
|---|---|---|---|---|---|
| PC1 | Store URL | `bookscan_sync.py` line 36 | `bmbooks-dev.myshopify.com` | `bruce-mckenzie-booksellers.myshopify.com` | |
| PC2 | Access token | `bookscan_sync.py` line 37 | Dev store token | Live store custom app token | |
| PC3 | DBF base path | `bookscan_sync.py` line 41 | `/Users/lalfred/.../SABSSAVE` | `Z:\bookscan` | |
| PC4 | Remove product cap | `bookscan_sync.py` line 57 | `MAX_PRODUCTS = 20` | `MAX_PRODUCTS = None` | |
| PC5 | Delete state file | `sync_state.json` | Exists from UAT runs | Deleted — clean slate for first live run | |
| PC6 | Create metafield definitions in live store | Shopify Admin > Settings > Custom data > Products | Not created | 4 definitions: bookscan.author, bookscan.isbn, bookscan.pages, bookscan.publication_date | |
| PC7 | Create custom app in live store | Shopify Admin > Apps > Develop apps | Not created | App with scopes: write_products, read_products, write_inventory, read_inventory, read_locations | |
| PC8 | Confirm live store location ID resolves | Run a dry run against live store | First location returned is "Bruce McKenzie Booksellers" | | |

---

## Sign-Off

| Run | Date | Tester | Created | Updated | Errors | Result |
|---|---|---|---|---|---|---|
| UAT Run 1 (dry run) | | | n/a | n/a | n/a | |
| UAT Run 2 (first sync) | | | | | | |
| UAT Run 3 (idempotency) | | | 0 | 0 | 0 | |
| UAT Run 4 (delta sync) | | | 0 | 1 | 0 | |
| UAT Run 5 (full flag) | | | 0 | 20 | 0 | |
| Production Run 1 | | | | | | |

**UAT approved for production:** ☐ Yes &nbsp;&nbsp; Date: ___________
