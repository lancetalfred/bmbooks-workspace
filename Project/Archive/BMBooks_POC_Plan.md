# BMBooks — Shopify Sync POC Plan

**Created:** April 13, 2026
**Author:** Lance Alfred

---

## Safety — does this affect the live WooCommerce site?

**No. The live WooCommerce site is completely untouched throughout this entire POC.**

| Step | What it does | Affects live site? |
|---|---|---|
| SQL query in phpMyAdmin | Reads data only — pure `SELECT` query | No |
| CSV export | Downloads query results as a file | No |
| Python script | Connects to Shopify API only — no WooCommerce connection | No |

The SQL query is a `SELECT` statement — it only reads, never writes. The live site
won't know the query ran. This is identical to what we did when extracting ISBNs
for the BookData audit.

The Python script has no connection to WooCommerce or the A2 Hosting server at
any point. It only talks to the Shopify dev store.

**One rule when in phpMyAdmin:** only run queries that start with `SELECT`.
If what you're about to run doesn't start with `SELECT`, stop and check first.

---

## What this POC proves

Before building the full Bookscan → Shopify sync, we need to confirm that the
Shopify integration works end-to-end. This POC uses existing WooCommerce product
data (already accessible via cPanel) to test the full pipeline without needing
the Bookscan DBF files.

**If this works, we know:**
- Our Python script can successfully create and update products in Shopify
- Field mapping is correct (title, ISBN, price, stock, author, description)
- Inventory levels sync correctly
- The approach is production-ready — we just swap the data source from CSV to DBF

**What this is NOT:**
- A live production sync
- Connected to the Bookscan database (that comes after)
- Running on a schedule (that comes after)

---

## Architecture

```
phpMyAdmin (cPanel)
       │
       │  SQL export → CSV
       ▼
poc_shopify_sync.py
       │
       │  Shopify Admin API
       ▼
Shopify Dev Store
(not the live site)
```

---

## Prerequisites

### 1. Shopify Partners account
- Go to partners.shopify.com
- Sign in or create an account (free)
- This gives access to unlimited free development stores

### 2. Shopify dev store
- In Shopify Partners: Stores → Create development store
- Name: `bmbooks-dev` (or similar)
- Purpose: Test sync integration
- This is completely separate from the live store — nothing here affects bmbooks.co.nz

### 3. Shopify Admin API access token (dev store)
- In the dev store: Settings → Apps and sales channels → Develop apps
- Create app → name it "Bookscan Sync POC"
- Admin API scopes needed:
  - `write_products` — create and update products
  - `read_products` — check if product exists
  - `write_inventory` — update stock levels
  - `read_inventory` — read inventory item IDs
  - `read_locations` — get the store location ID
- Install app → copy the Admin API access token (shown once only)

### 4. Python environment
- Python 3.9+
- Install dependencies:
  ```
  pip install -r requirements.txt
  ```
  Dependencies: `dbfread`, `requests`, `schedule`

### 5. WooCommerce product export (CSV)
- See Step 1 below

---

## Step-by-Step Instructions

### Step 1 — Export products from WooCommerce database

1. Log into cPanel (A2 Hosting)
2. Open **phpMyAdmin**
3. Select the BMBooks database from the left panel
4. Click the **SQL** tab
5. Open `Sync/woocommerce_export.sql` and paste the contents
6. Confirm `LIMIT 50` is in place (start small)
7. Click **Go**
8. Click **Export** → Format: CSV → **Go**
9. Save the file as `products.csv` in the `Sync/` folder

**Database table prefix:** `wp4n_` — tables are `wp4n_posts` and `wp4n_postmeta`
(Default WordPress uses `wp_` but this install uses `wp4n_`)

**What to check in the CSV:**
- Does it have rows? (should be 50)
- Are ISBNs in the `isbn` column?
- Are titles readable?
- Do the `author`, `publisher` columns have data, or are they empty?

> If `author` and `publisher` are empty, those fields may be stored as
> WooCommerce attributes rather than post meta. Update the SQL query to
> join `wp_term_relationships` — see note at bottom of SQL file.

---

### Step 2 — Configure the POC script

Open `Sync/poc_shopify_sync.py` and fill in the two config lines at the top:

```python
SHOPIFY_STORE_URL    = "bmbooks-dev.myshopify.com"   # your dev store URL
SHOPIFY_ACCESS_TOKEN = "shpat_xxxxxxxxxxxxxxxxxxxx"  # from Step 3 above
```

Leave these as-is for now:
```python
BATCH_SIZE = 10      # start with 10 products
DRY_RUN    = True    # always dry run first
```

---

### Step 3 — Dry run (no Shopify calls made)

```bash
python poc_shopify_sync.py products.csv
```

With `DRY_RUN = True`, the script reads the CSV and prints what it *would* send
to Shopify — without making any API calls.

**Expected output:**
```
2026-04-13 14:00:00 [INFO] BMBooks Shopify POC
2026-04-13 14:00:00 [INFO] Read 50 products from CSV
2026-04-13 14:00:00 [INFO] Processing 10 of 50 products (batch size: 10)
2026-04-13 14:00:00 [INFO] DRY RUN — showing what would be sent to Shopify:
2026-04-13 14:00:00 [INFO]   [9780143108030] The Luminaries — $24.99 — stock: 3
2026-04-13 14:00:00 [INFO]   [9780143566175] Mister Pip — $19.99 — stock: 1
...
2026-04-13 14:00:00 [INFO] Set DRY_RUN = False to push to Shopify
```

**If something looks wrong** (missing titles, weird prices, empty fields) —
fix the SQL query and re-export before going further.

---

### Step 4 — Live run against dev store

Once the dry run output looks correct:

1. In `poc_shopify_sync.py`, set `DRY_RUN = False`
2. Run again:
   ```bash
   python poc_shopify_sync.py products.csv
   ```

**Expected output:**
```
2026-04-13 14:05:00 [INFO] Created  [9780143108030] The Luminaries
2026-04-13 14:05:00 [INFO] Created  [9780143566175] Mister Pip
...
2026-04-13 14:05:00 [INFO] POC complete — Created: 10  Updated: 0  Errors: 0
```

---

### Step 5 — Verify in Shopify dev store

Log into the dev store and check:

| Check | Expected | Result |
|---|---|---|
| Products appear in Products list | 10 products visible | ✅ 10 products |
| Titles are correct | Match WooCommerce | ✅ Exact match |
| ISBNs appear as SKU on each variant | e.g. 9781529962697 | ✅ Confirmed |
| Prices are correct | Match WooCommerce | ✅ $40.00 confirmed |
| Inventory quantity set | Matches stock column from CSV | ✅ 1, 4, 2 in stock visible |
| Author appears in metafields | Under product > Metafields | ✅ 9/10 products (1 has corrupt title data) |
| ISBN in metafields | bookscan.isbn | ✅ 10/10 |
| Pages in metafields | bookscan.pages | ✅ 7/10 (some books lack pages in description) |
| Publication date in metafields | bookscan.publication_date | ✅ 8/10 |
| Publisher appears as Vendor | In product details | ⚠️ Shows store name "BMBooks Dev" — publisher not in postmeta, embedded in description HTML. Not extracted. Post-POC fix. |
| Product type set | Binding (Paperback, Hardback etc.) | ✅ Hardback, Paperback, Picture Flat, Trade Paper |
| Products created as Draft | Not published | ✅ All Draft |
| Weight correct | Matches CSV | ✅ 303g confirmed |
| "Sell when out of stock" | On (Available to order) | ✅ inventory_policy: continue added |

---

### Step 6 — Run again (idempotency test)

Run the script a second time **without changing anything**.

```bash
python poc_shopify_sync.py products.csv
```

**Expected output:**
```
Updated  [9780143108030] The Luminaries
Updated  [9780143566175] Mister Pip
...
POC complete — Created: 0  Updated: 10  Errors: 0
```

This confirms the script handles existing products correctly — it updates rather
than creating duplicates. This is critical for the production sync.

---

### Step 7 — Test a stock change

1. In the CSV, manually change the stock number for one product
2. Run the script again
3. Check in Shopify — did the inventory level update?

**Result:** ✅ PASSED — changed #1 Dad Book stock from 4 → 7. Shopify showed 7 (both Available and On-hand) after next run.

---

## Success Criteria

The POC is successful when:

- [x] 10 products created in dev store with correct data
- [x] Running script twice updates, not duplicates — **Confirmed: Created: 0  Updated: 10  Errors: 0**
- [x] Stock level changes are reflected in Shopify — **Confirmed at creation time via inventory_quantity in variant**
- [x] No errors in the log — **Confirmed: 0 errors**

**POC CONFIRMED COMPLETE — 13 April 2026**

Note: inventory_quantity in the variant payload sets stock at creation time. The REST `inventory_items` API returns 404 for existing products (timing/dev store issue). For production, inventory updates will use the variant ID on update calls. This does not affect the POC proof point.

---

## Bugs Found and Fixed During POC

| Bug | Symptom | Fix |
|---|---|---|
| Wrong table prefix | `#1146 - Table 'wp_posts' doesn't exist` | Confirmed prefix is `wp4n_` via phpMyAdmin — updated SQL |
| Weight showing "NULLg" | Weight field contained string "NULL" | `.replace("NULL", "0")` in CSV reader |
| find_by_sku returning wrong products | All 10 "updated" the same product | Added `sku` to fields, filter by exact SKU match |
| Counters never incremented | Created/Updated always 0 even on success | Moved counter increment before `set_inventory` call |
| Inventory not setting on existing products | inventory_quantity ignored on PUT | Variant replacement approach — new variant gets inventory_quantity at creation |
| "Sell when out of stock: Off" | Books with 0 stock showed as unavailable | Added `inventory_policy: continue` to variant |
| Metafields not visible in Shopify admin | Author/ISBN/pages not showing | Created metafield definitions at Settings → Custom data → Products |

---

## What Happens Next

| Step | Action | Status |
|---|---|---|
| Swap data source | Replace CSV reader with DBF reader | ✅ Done — bookscan_sync.py reads MASTER + PUBLISHER + WEBLIST. 38,013 products load correctly. |
| Add delta sync | Only process changed records — full 37k sync = 12 hrs, delta = 2–5 min | ✅ Done — hash of 7 key fields stored in sync_state.json |
| Test against dev store | --dry-run then live run against bmbooks-dev.myshopify.com | ✅ Done — Created: 20, Updated: 20 (idempotency), Errors: 0. All fields confirmed. |
| Add inbound order sync | Poll Shopify for new orders → deduct stock from Bookscan DBF (Phase 2) | ⏳ Phase 2 |
| Build sync GUI | tkinter desktop app — "Synchronize Now" button, live activity log, summary stats | ⏳ Phase 2 |
| Install on shop machine | Python + Windows Task Scheduler for automated 2-hour background sync | ⏳ Next — Chrome Remote Desktop session with Louisa (~20 min) |
| Deploy to live store | Create custom app in live store, update 2 config lines, run | ⏳ Pending |
| Cover images | Phase 2 — assess Open Library API vs Bookscan catalog folder approach | ⏳ Phase 2 |

---

## Files

| File | Location | Purpose |
|---|---|---|
| POC sync script | `Sync/poc_shopify_sync.py` | Reads CSV, pushes to Shopify |
| SQL export query | `Sync/woocommerce_export.sql` | Extracts products from WooCommerce DB |
| Production script | `Sync/bookscan_sync.py` | Full sync — DBF source, scheduler included |
| DBF inspector | `Sync/inspect_dbf.py` | Reveals DBF field names once files received |
| Dependencies | `Sync/requirements.txt` | Python packages |

---

## Notes

**Why not use the live Shopify store for the POC?**
The live store is being prepared for go-live. Pushing 10 draft products to it
is low risk, but a dev store keeps things clean and avoids any chance of
confusing Louisa with test products appearing in the admin.

**Why WooCommerce data and not DBF files?**
We had immediate access to the WooCommerce database via cPanel. The DBF files
required access to the shop's local server, which was arranged on 13 April 2026 —
Louisa uploaded the full SABSSAVE folder (~200 DBF files) to Google Drive.
The field mapping proved identical — the source data just came from a different place.

**GST / tax setting**
All product variants have `taxable: False`. Books in New Zealand are GST-exempt.
This matches the current WooCommerce setup.
