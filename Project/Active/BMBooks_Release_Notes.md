# BMBooks Release Notes

*A running log of changes made to the website (most recent first)*

---

## 🛠️ v2.3 — Search Bar + Header Redesign (In Progress)

**Date:** June 9, 2026
**Last updated:** June 9, 2026

---

### Summary

Static search bar added to header (replaces magnifying glass icon). Header layout restructured: logo left, search centred, NZD/Account/Heart/Cart right. Typography updated to Open Sans (body) + Libre Baskerville (headings/subheadings/accent). Zero-price product handling added to sync. All changes live in production.

---

### June 9, 2026

**Typography — updated font stack**
- Body: Open Sans (was default theme font)
- Subheading: Libre Baskerville
- Heading: Libre Baskerville
- Accent: Libre Baskerville
- Applied via theme settings in Shopify admin; pushed to production via `settings_data.json`

**Static header search bar**
- Replaced magnifying glass icon with inline search input (`snippets/bmbooks-search-bar.liquid`)
- Position: centred between logo (left) and actions (right) — `1fr 1.5fr 1fr` grid
- Cream background (`#fdf8f3`), dark text (`rgba(0,0,0,0.85)`), placeholder `rgba(0,0,0,0.45)`
- Green submit button (right side) with cream border
- Mobile: full-width bar below the logo row (`header__row--mobile-search`), no magnifying glass icon
- Searchanise-ready: input has `name="q"` and `type="search"` for auto-detection
- `snippets/header-row.liquid`: search hardcoded to center column + top row regardless of theme settings
- `sections/header.liquid`: search rendered unconditionally; NZD forced before actions in order string

**Header icon order**
- New order (left→right): NZD › Account › Heart (Swym) › Cart
- Cart pushed to end via `order: 100` CSS in `header-actions.liquid`

**Zero-price product handling**
- `Sync/fix_zero_price_drafts.py`: one-time script set 104 Active zero-price products to Draft
- `Sync/bookscan_sync.py`: `AUTO_PUBLISH = True`, `force_status` logic in sync loop
  - Zero-price products always sync as Draft
  - Price $0→>$0: auto-publishes on next sync (when `AUTO_PUBLISH = True`)
  - Priced products created after go-live: immediately Active

---

## 🛠️ v2.2 — Pre-Launch Polish (In Progress)

**Date:** June 9, 2026
**Last updated:** June 9, 2026

**Author:** Lance Alfred

---

### Summary

Pre-launch hardening sprint across two days. Sync exclusion rules fully tightened (NOWEB + full department list). Product page messaging, schema, and checkout delivery estimates all updated. Duplicate collections consolidated. Book Tokens and BMBooks Vouchers now syncing to Shopify.

---

### June 9, 2026

**STATUS_EXCLUDE — expanded to full NOWEB set**
- `bookscan_sync.py` updated from 3-code to 20-code exclusion list
- All NOWEB=True Bookscan status codes now excluded: OP, RP, RUC, OSI, NOR, PBA, ASC, NLA, PBD, PDR, ORD, NLD, PUA, CHP, OLD, INT, NOT, WFC, AD
- Confirmed by Louisa 2026-06-08: "follow Bookscan's own NOWEB flag"
- Net result: 246 additional books excluded (1,452 → 1,705 CSTATUS skipped). 0 errors.
- Deployed to shop machine and verified via manual sync run

**bookGenre schema markup**
- Added `bookGenre` property to Book JSON-LD schema in `theme.liquid`
- Loops product tags, filters out `_` system tags, outputs remaining as a JSON array
- Example output: `"bookGenre": ["Fiction", "Crime Fiction", "Thriller"]`
- Explicit genre signal for Google and AI crawlers — no inference required
- Pushed to production

**Product page badge updates** (`templates/product.json`)
- In Stock badge: "Ships within 1–2 business days · NZ main centres 2–5 working days" → **"In stock · NZ delivery 2–5 working days"** — removed dispatch language, aligned with checkout estimates
- Available badge: "We'll order this for you · Allow 1–2 business days to process" → **"We can order this for you · Allow 1–2 weeks for delivery"** — reflects real NZ supplier lead times (Louisa-confirmed)
- Badge and description text colours darkened (`.bmb-avail__text` `rgba(0,0,0,0.45)` → `0.7`, badge colours deepened)
- Pushed to production

**Checkout delivery estimates**
- Transit times updated in Shopify admin → Settings → Shipping:
  - North Island: 2–3 working days
  - South Island: 3–5 working days
  - Rural: 4–6 working days
  - Collect in Store: same day
- Now consistent with product page badge "NZ delivery 2–5 working days"

### June 9, 2026 (continued)

**DEPARTMENT_EXCLUDE — expanded to full Louisa-confirmed set**
- Louisa went through every department code on call — full list confirmed
- Added: GFS, SPE, XXX, MAG, AUD, CDS, EXP, FUN, KIT, MON, POS, STK, YOG, blank dept
- Removed TOK and VOU — industry book tokens and BMBooks vouchers to show on site
- Net: 5 Book Tokens ($10/$20/$25/$50/$100) + 10 BMBooks Vouchers ($10–$100) created in Shopify
- BINDING_MAP updated: `VO` → "Voucher", `**` → "Token" — binding warnings resolved
- DEPARTMENT_EXCLUDE now at 132 skipped (was 52)

**Duplicate collections — consolidated**
- Biography + Biographies → **Biography & Memoir** (OR rule, 1,936 books)
- Gifts + Stationery + Gifts & Stationery → **Gifts & Stationery** (OR rule, 2,000 books)
- Gardening + The Garden → **Gardening** (OR rule, 346 books)
- History & Politics unchanged (2,703)
- Deleted: Politics, Gifts, Stationery, Biographies, The Garden
- Nav: Gifts & Stationery and Games & Puzzles promoted to top-level direct links

**NZ shipping rates**
- Louisa confirmed: keep current rates as-is. No changes needed.

---

## 🏷️ v2.1 — Genre Enrichment (Complete)

**Date:** June 7–8, 2026
**Last updated:** June 8, 2026

**Author:** Lance Alfred

---

### Summary

BIC-first genre enrichment of the full BMBooks catalogue. Nielsen's professional subject classification (BIC codes) was discovered unused inside the existing Bookscan DBF files — `BICMAIN` field in `PUBLISHER.DBF`, covering 90% of web-listed books. A new script (`genre_enrichment_v2.py`) was built to read these codes, compare them against Bookscan's existing category tags, and apply correct genre tags to Shopify products.

Result: **2,820 books** correctly tagged across 30+ genre tags. Five new collections live: Romance (270), Horror (123), Manga (238), Thriller (528), Translated Fiction (29). Crime Fiction collection expanded and renamed Crime & Thriller (1,567 books). Fiction nav updated with new genre dropdowns.

---

### June 8, 2026

**Apply complete**
- `python3 genre_enrichment_v2.py --apply` run against production Shopify
- Applied: 2,820 / Skipped: 346 (already tagged or not found) / Errors: 0
- Two dry-runs completed before production write

**Tag preservation confirmed**
- `_merge_tags()` in `bookscan_sync.py` confirmed working in production
- Root cause of initial test failure: shop machine had older version of `bookscan_sync.py` without merge logic — updated
- Verified: enrichment tags survive hourly Bookscan sync cycles without being overwritten

**Smart collections created** (`Sync/create_genre_collections.py`)
- Romance: 270 books (`tag is Romance`)
- Horror: 123 books (`tag is Horror`)
- Manga: 238 books (`tag is Manga`)
- Thriller: 528 books (`tag is Thriller`)
- Translated Fiction: 29 books (`tag is Translated Fiction`)

**Crime Fiction → Crime & Thriller**
- Collection renamed to "Crime & Thriller"
- Handle updated: `crime-fiction` → `crime-and-thriller` (301 redirect in place)
- Collection rule updated to disjunctive OR: `tag is Crime Fiction` OR `tag is Thriller`
- Combined catalogue: 1,567 books
- Description updated to reflect combined scope

**Fiction nav updated**
- Horror, Manga, Romance added to Fiction dropdown
- Crime & Thriller nav link updated to `/collections/crime-and-thriller`

**Editorial descriptions**
- 50–100 word descriptions added to all 5 new collections: Romance, Horror, Manga, Thriller, Translated Fiction

---

### June 7, 2026

**Genre Enrichment — BIC discovery**
- Discovered `BICMAIN` field in `PUBLISHER.DBF` — Nielsen BookData professional BIC subject classification, already present in local Bookscan DBF files
- 90% coverage of web-listed books (35,033 / 38,836) — higher than Google Books (~59%) and free
- `BICSUBJECT.DBF` provides full BIC taxonomy lookup (2,616 codes across 6 levels)
- Confirmed: 202 Romance + 30 Horror books hiding in General Fiction; 186 Manga books in Graphic Novels; 511 Thriller books in Crime Fiction

**genre_enrichment_v2.py — new script**
- BIC-first enrichment with Google Books fallback for the ~10% without BIC
- Four modes: `--compare` (stratified validation test), `--audit` (full BIC pass), `--audit-fallback` (Google Books for NO_BIC), `--apply` (write to Shopify)
- SKIP protection: 27 NZ-specific and Māori subcategories explicitly protected — never enriched
- `DUAL_TAG_PAIRS`: 20 pairs where BIC signals two valid collections (e.g. Historical Fiction + Romance, Classics + Horror, Graphic Novels + Manga)
- Comma-separated multi-tag support for YA compound codes (e.g. YFM → "Childrens Fiction, Romance")
- Confirmation prompt before any Shopify write: "About to write to [store URL]. Proceed? (yes/no)"
- All scripts run by Lance in terminal — no automated writes

**Validation**
- Two rounds of comparison testing (`--compare --sample 10`) catching and fixing mapping errors
- Full audit (`--audit`) run against fresh DBF files from shop machine
- Independent validation agent review — identified 6 systematic BIC mapping errors affecting 497 rows:
  - `AK` (graphic design/industrial art) incorrectly mapped to Architecture → removed
  - `AC` (art history/movements) incorrectly mapped to Craft → removed
  - `VF` (family & health) too broadly mapped to Psychology — narrowed to VFJ* only
  - `WQY` (family history/genealogy) caught by Transport mapping → remapped to Biography
  - `GTC` (communication studies) caught by Maps mapping → remapped to Languages
  - `WF` bare code catching non-fashion books → 2 individual rows removed
- All 6 errors corrected before any production write

**Final audit results (post-validation)**
- Total changes: 3,166 (768 RECLASSIFY + 2,398 ADD_SECONDARY)
- Top tags: Thriller 552, Biography 455, Romance 279, Politics 268, Architecture 261, Manga 242
- Zero rows touching protected NZ/Māori subcategories
- Zero True Crime false positives

---

## 🛒 v2.0 — Shopify Migration (In Progress)

**Date:** March–May 2026
**Last updated:** 25 May 2026

**Author:** Lance Alfred

---

### Summary

Full migration from WordPress + WooCommerce to Shopify Basic. Store built and configured — awaiting Bookscan/Ebility product sync before go-live.

---

### May 25, 2026

**Navigation — dropdown menus**
- All 7 nav items now have dropdowns with top sub-categories ranked by product count
- Manawatū added as standalone top-level nav item (between New Zealand and Gifts & Stationery)

**Collections — 75 total**
- 24 new sub-collections created (History, Well Being, Sciences, Travel, Biographies, Sport, Garden)
- Manawatū parent collection: 155 products, `tag("The Manawatu")`

**Homepage — featured collections live**
- 6 sections: New Releases, Bestsellers, Fiction, Kids, New Zealand, Gifts & Stationery
- Bestsellers section confirmed with Louisa (she actively maintains the tag in Bookscan)

**Gift card — denomination selector fixed**
- Added Variant picker block in theme editor
- Removed incorrect availability/shipping badge
- CSS: denomination label bolded, dropdown border styled to match theme

**Sync script**
- `--once` flag and lock file (`sync.lock`) added to `bookscan_sync.py`
- `bookkeeper_gui.py` (tkinter) + `Sync Now.bat` built — pending deployment to shop machine

**Product page**
- Height and Width metafields added to Book Details section
- ISBN typo fix applied (`product.metafixelds` → `product.metafields`)

**Author name fix deployed**
- Authors now display as Firstname Lastname (e.g. "Ray Bradbury" not "Bradbury Ray")
- Delta sync auto-updates all affected products — no `--full` flag needed

---

### April 14–23, 2026

**Sync Script — Data Quality Fixes**

- Duplicate ISBN deduplication added to `bookscan_sync.py`
    - 13 duplicate ISBN groups found in MASTER.DBF (15 extra records)
    - Fix: keep record with highest stock; tiebreak on price
    - 37,998 unique products confirmed after dedup (matches WEBLIST count exactly)
    - Full list saved to BMBooks_Duplicate_ISBNs.csv for Louisa to review
- Vendor fallback fixed: products without PUBLISHER.DBF entry now sync with blank vendor instead of "BMBooks"
    - 92.4% of products (35,115) have real publisher name
    - 7.6% (2,883) — mostly non-book items — now correctly show no vendor
- Dev store batch updated: all 162 products refreshed with corrected data (0 errors)

**Remote Access — In Progress**

- FortiClient VPN (IPSec/IKEv1) confirmed incompatible with macOS FortiClient
- Chrome Remote Desktop proposed to Belinda — awaiting response
- Next step: Belinda installs Chrome Remote Desktop on shop machine

---

### April 13, 2026 (evening)

**Bookscan DBF Inspection — Complete**

- Full Bookscan database (~200 DBF files) received via Google Drive (SABSSAVE folder)
- 5 key files inspected: MASTER.DBF, PUBLISHER.DBF, WEBLIST.DBF, WEBMAINCAT.DBF, WEBSUBCAT.DBF
- Record counts confirmed: MASTER 133,752 · PUBLISHER 132,494 · WEBLIST 38,013 active web products · STOCK 0 (empty — stock is in MASTER.ONHAND)
- All field names confirmed — skeleton assumptions corrected:
    - Stock: MASTER.ONHAND (not STOCK.DBF/QOH — STOCK.DBF is empty)
    - Web filter: WEBLIST.INACTIVE=False (not a WEB flag on MASTER)
    - Publisher/pages/pub_date/weight/blurb: PUBLISHER.DBF joined on ISBN
- BINDING code mapping confirmed: PB=Paperback, HB=Hardback, TP=Trade Paperback, PF=Picture Flat, BO=Board Book, and 14 others
- Additional lookup: PUBLISH.DBF = supplier/distributor name lookup (PENG→Penguin, ALLI→Alliance etc.) — not needed for sync

**bookscan_sync.py — Production Script Complete**

- Skeleton replaced with full production script using confirmed field names
- Reads and joins 3 DBF files: MASTER + PUBLISHER + WEBLIST
- Delta sync implemented: MD5 hash of 7 key fields (title, author, publisher, price, stock, binding, pages) stored in sync_state.json — unchanged products skipped each run
- CLI flags: `--dry-run` (no API calls), `--full` (skip delta, sync all products)
- Binding codes mapped to human-readable labels
- inventory_policy: continue on all variants (Available to order when stock = 0)
- Products created as draft (go live manually or in bulk)
- Local test with SABSSAVE data: 38,013 products load correctly, 37,923 with price, 9,857 in stock
- Descriptions empty in local test (no .FPT memo files in zip) — will work on shop machine
- Dev store test confirmed ✅
    - Run 1: Created 20, Errors 0
    - Idempotency run: Created 0, Updated 20, Errors 0
    - Fahrenheit 451 verified: title, price ($22.99), SKU (9780006546061), stock (2), weight (230g), type (Paperback), vendor (HarperCollins Publishers), all 4 metafields ✅
    - Author title-cased: BRADBURY RAY → Bradbury Ray ✅
    - inventory_policy: continue confirmed (Sell when out of stock: On) ✅
    - Inventory 404 warnings on update are non-fatal dev store quirk — stock set correctly at creation
    - Products show "Point of Sale" in Publishing — expected Shopify default for API-created products. Not a concern: BMBooks uses Bookscan for in-store POS, not Shopify POS. Products are Draft so not visible to customers regardless. Will show Online Store once activated at go-live.

---

### April 13, 2026

**Shopify POC — Confirmed Working**

- Shopify Partners dev store created: bmbooks-dev.myshopify.com
- WooCommerce SQL export run in phpMyAdmin (wp4n_ prefix) — 40 valid products, 10 skipped (gift vouchers/invalid ISBNs)
- poc_shopify_sync.py built and debugged through multiple iterations
- All POC success criteria met — full test results:
    - Run 1: Created 9, Updated 1, Errors 0 ✅
    - Idempotency run: Created 0, Updated 10, Errors 0 ✅
    - Stock change test: #1 Dad Book stock changed 4→7, confirmed in Shopify ✅
- All fields verified against WooCommerce: title, price, SKU/ISBN, weight, product type, description ✅
- Metafields confirmed saving (bookscan.author, bookscan.isbn, bookscan.pages, bookscan.publication_date) ✅
- inventory_policy: continue — out-of-stock books show "Available to order" ✅
- Package profiles added to go-live checklist: 2–3 profiles needed for accurate DHL volumetric rates
- Bugs fixed during POC:
    - find_by_sku was returning all variants (no SKU filter validation) — fixed: request sku field, filter by exact match
    - created/updated counters were after set_inventory call — moved before (errors don't suppress the count)
    - Weight showing "NULLg" — fixed: .replace("NULL", "0")
    - WooCommerce table prefix wp4n_ (not wp_) — confirmed via phpMyAdmin, updated SQL

**DLL Analysis — Full Discovery**

- WooLibrary.dll and WooCommerce.NET.dll analysed via Python metadata extraction.
- WooCommerce.NET.dll = open source library (WooCommerceNET, MIT licence) — not written by Barcode Solutions.
- WooLibrary.dll = Barcode Solutions' entire contribution: one class, one method. A thin COM wrapper. No proprietary logic.
- shopifylibrary.dll confirmed absent — Shanti has not started building the Shopify connector.
- Decision: Python sync script is now the confirmed primary path. No further dependency on Shanti.
- Field mapping for Python script confirmed: ISBN→sku, Title→title, Author/Publisher/Pages/Pub date→metafields, Price→variants[0].price, Stock→inventory_quantity, Binding→product_type, Web flag→status.
- Shanti confirmed completely unresponsive to email and text from Louisa.
- Scenario table built for Louisa — full before/after comparison of all workflows.
- Software comparison completed: Bookscan vs CirclePOS (long-term recommendation).

---

### April 12, 2026

**Bookscan/Ebility Architecture — Full Discovery**

- All e-Comms Setup tabs explored via screen share: General (2hr sync, Z:\bookscan path), Connection (Spark email), Multi Store (empty web orders settings), Sales Export (NielsenBookScan active, bt500124), EDI (Pacestream/B2BE, gateway.b2be.com), eWeb (empty — unused).
- Bookscan Modules tab: NO Shopify option in web platform dropdown. Available: WooCommerce (active), BigCommerce, eWeb, Other. Bookscan website explicitly advertises Shopify as supported — module needs enabling or software update.
- WooCommerce REST API keys identified: Book Hub (ID:7, last accessed today) = Ebility sync. Starshipit Integration (ID:6, last accessed today) = eShip. GoSweetSpot (ID:8) = inactive since March 2025.
- WooCommerce webhooks: 3 active (product.created, product.updated, product.deleted) all pointing to booksellers-155024375aa1.herokuapp.com — Barcode Solutions' Heroku middleware. Store ID = /11/.
- Full architecture mapped: Ebility → WooCommerce REST API (outbound) + WooCommerce webhooks → Heroku middleware → Ebility (inbound). Shopify migration requires both sides.
- Bookscan database format confirmed: dBASE/FoxPro (.DBF + .CDX index files) in Z:\bookscan.
- Bookscan confirmed as in-store POS (not just web sync) — handles POS, inventory, EDI ordering, NielsenBookScan reporting.
- Decision: build custom Python script to read Bookscan DBF files and sync to Shopify Admin API. Bypasses Shanti/Barcode Solutions entirely.
- Gleebooks (Sydney) researched — uses CircleSoft Circle POS, not Shopify. CircleSoft noted as potential long-term Bookscan replacement.
- Bookscan support line (1300 766 905) confirmed never answered.

**Bookscan Help Docs + Z: Server Review**

- All Bookscan help docs sent by Louisa reviewed: Web Export, CSV Export, e-Comms, WooCommerce connector, Web Categories.
- Key discovery: WooCommerce connector = woolibrary.dll installed at C:\Program Files (x86)\Bookscan\ on the local machine. Shopify equivalent would be shopifylibrary.dll.
- Z:\bookscan confirmed as data directory (not program files). Key subfolders: catalog (product DBF files), Web (web export), EDI, LOG, MarcFiles.
- shopifylibrary.dll check must be done on local C: drive, not Z: server.
- CSV export (F9) confirmed as alternative sync path — fields: ISBN, Title, Author, Price, Stock, Publisher, Pub date, Binding, Status, Blurb, Pages, Weight, Height, Width.
- Email sent to Louisa: plain-language explanation of woolibrary.dll architecture, Shanti deadline request, screenshot requests for C:\Program Files (x86)\Bookscan\ and Z:\bookscan\catalog\.
- C:\Program Files (x86)\Bookscan\ screenshot received and reviewed:
    - WooLibrary.dll confirmed present (4/10/2020, 7 KB)
    - WooCommerce.NET.dll confirmed present (4/10/2020, 438 KB)
    - shopifylibrary.dll confirmed ABSENT — does not exist on machine
    - viiLibrary.dll present (31/10/2023, 8 KB) — unknown platform, newer than WooLibrary
    - Conclusion: Shopify connector requires Barcode Solutions to build and install a new DLL.
      Not a config change — actual development work. Confirms workaround path is correct.

---

### April 11, 2026

**Ebility / Bookscan — Initial Discovery (Louisa Teams call)**

- Screen share session with Louisa — viewed Ebility e-coms module live.
- E-coms runs every 2 hours (configurable to 30 min). Syncs: orders to suppliers via EDI, inbound electronic invoices, website stock/product updates, nightly data to NielsenBookScan.
- Web export mapping module discovered — controls how Ebility categories/products map to the website.
- Belinda identified — local IT person for the shop. Manages firewall. Not a Barcode Solutions employee.
- Louisa accesses Ebility via RDP to shop machine (remote desktop).
- Chrome Remote Desktop set up as screen sharing solution (TeamViewer blocked on Lance's work laptop).
- Lance attempted call to Shanti — Shanti cancelled it.

**File Organisation**

- Project files reorganised into `/Documents/Claude/BMBooks/` with Project/, Reports/, Content/, Legacy/ subfolders.

---

### April 9, 2026

**Store Configuration**

- Shopify gift cards created — denominations $30, $40, $50, $60, $80, $100. Based on WooCommerce sales data: $90 never sold, $10/$20 negligible. Existing physical vouchers are in-store only and cannot be used online — no migration needed.
- DHL international shipping confirmed working on Shopify Basic plan — uses Shopify's own DHL integration (not third-party). Handling fee confirmed $0.

**WooCommerce Data Exports (pre-migration archive)**

- Order history exported: 2,396 orders, $137,344 NZD total revenue (2021–2026). Saved to BMBooks_WooCommerce_Orders_Apr2026.csv.
- Revenue by year generated for IRD: 2021 $12k, 2022 $38k, 2023 $22k, 2024 $30k, 2025 $26k, 2026 $10k (partial). Saved to BMBooks_Revenue_By_Year.xlsx.
- Refunds exported: 51 refunds, $2,481 NZD. Majority are out-of-stock/out-of-print issues — addressed by BookData audit.
- Coupon codes: none exist.
- Product reviews: 7 reviews (all 4–5 star) — not worth migrating.

---

### April 8, 2026

**Platform Corrections**

- Shipping platform corrected — confirmed eShip (NZ Post), not Starshipit. Native Shopify integration available post go-live (eShip > Integrations > Add Integration > Shopify).

**Research & Analysis**

- Gift vouchers = 21% of online revenue ($5,550/year) — Shopify gift cards not yet set up. Critical pre-go-live item. Denominations: $10, $20, $25, $30, $40, $50, $60, $70, $80, $100.
- International shipping problem identified — WooCommerce shows "Shipping Costs To Be Advised" at checkout, causing order cancellations. Shopify DHL carrier-calculated rates fix this.
- WooCommerce category analysis — NZ Fiction #1 (43 items), Local/Manawatu Authors #3 (34 items). Data-backed nav recommendation sent to Louisa.
- WooCommerce customer export — 2,123 customers, avg 1.13 orders, $64.36 lifetime spend. Import to Shopify planned close to go-live.
- BookData out-of-print workflow confirmed — Bulk Search accepts ISBN upload, returns Availability field. WooCommerce product export in progress to generate ISBN list.
- In-store POS system unknown — added as question for Louisa.

**Store Configuration**

- International handling fee changed $2.00 → $0 (Louisa's decision — packaging cost not passed on)
- Searchanise out-of-stock configured — hide OFF, show-at-end OFF (backorder allowed, books appear in normal position)
- DMARC DNS record added to Cloudflare — email authentication now complete (SPF + DKIM + DMARC)
- Email templates branded #1A0A2E — Order refund, Order canceled, Customer account welcome, Customer account invite
- Contact Us page — text number updated with "Text only — not monitored for calls" note
- Google Analytics confirmed active under bmbooksellers@gmail.com
- Footer "Customer Service" heading CSS fix confirmed applied (font-weight: 700)
- Louisa email sent — progress update, 6 action items, timeline
- BookData out-of-print audit completed — 37,076 ISBNs checked against NielsenIQ BookData. 3,258 out-of-print identified (1,508 definite, 1,750 uncertain). BMBooks_OutOfPrint.xlsx sent to Louisa for review and removal from Ebility.
- WooCommerce product export via phpMyAdmin SQL query — bypassed broken WooCommerce exporter (stalled at 85% CPU on shared hosting). Extracted 37,076 ISBNs directly from database.

---

### April 7, 2026

- Live call with Louisa McKenzie — all 13 agenda items resolved
- Shopify Payments verification documents submitted (Step 5 of 5 — pending Shopify review)
- Email sender verification resolved — domain authentication auto-verified books@bmbooks.co.nz
- Brand colour #1A0A2E confirmed by Louisa
- Out of stock behaviour confirmed — backorder YES, label "Available to order", no lead time text
- New Arrivals confirmed — manual curation by Louisa, no auto date-based labelling
- Selling countries confirmed — AU, NZ, UK, US only
- Google account confirmed — bmbooksellers@gmail.com (Lance has access)
- Starshipit login email confirmed — books@bmbooks.co.nz (password to follow)
- GBP special hours — Louisa manages directly
- Google Business Profile updated — description, website URL, location, social links, Christmas hours

---

### April 6, 2026

- Brand colour corrected to #1A0A2E — applied to Scheme 1 (header/footer) and Scheme 6 (hero)
- Hero button changed from outline (Secondary) to solid (Primary)
- Footer Customer Service heading bold fix — Custom CSS applied
- Searchanise Search & Filter configured — synonyms, product field weights, filters set up
- Wishlist Plus by Swym installed — free plan, header launcher active
- SEO basics — meta title and description set for homepage, About Us, Visit Us, Contact Us

---

### April 5, 2026

- Shopify store created under books@bmbooks.co.nz
- Horizon theme installed and configured — colours, typography, layout
- Homepage built — announcement bar, hero, newsletter, contact strip, footer
- Core pages created — About Us, Visit Us (Google Maps), Contact Us
- Policies customised — Privacy, Return & Refund, Shipping, Terms of Service
- Shipping configured — NZ zones, DHL Express international with $2 handling fee
- Navigation menus built — Main menu, Customer Service footer menu
- Emails sent to Shanti (Ebility connector) and Louisa (store access + password)

---

## 🚀 v1.1 — Performance & Infrastructure Overhaul

**Date:** March 22, 2026

**Author:** Lance Alfred

---

### Summary

Major performance improvements addressing slow LCP (5.4s) and server instability. LCP improved to **3.5s in lab tests within one session**.

---

### Infrastructure

- Cloudflare CDN set up on free plan (nameservers updated by Abbey at Black Sheep Design)
- LiteSpeed Cache plugin installed and configured
- WooCommerce cache exclusions set (cart, checkout, my-account)
- HTTP/2, HTTP/3, 0-RTT, Early Hints, Speed Brain, Rocket Loader enabled via Cloudflare
- Cloudflare Fonts enabled (replaces need for Google Fonts self-hosting plugin)

### Performance

- Cart fragments disabled (was blocking page render)
- LCP hero image preload added
- Imagify WebP conversion started (in progress)

### Server Cleanup

- ~30GB freed (old backups, WP Staging folder)
- Server resources improved: RAM 100% → 20%, CPU 97% → 26%

### Backup

- UpdraftPlus configured with Google Drive remote storage
- Database, plugins, and themes successfully backed up

### 📊 Metrics

| Metric | Before | After (lab) |
| --- | --- | --- |
| LCP | 5.4s | 3.5s |
| FCP | 5.1s | 3.2s |
| TBT | — | 10ms |
| Performance Score | — | 76/100 |

---

## 🧱 v1.0 — Initial Setup

**Date:** Pre-March 2026

**Author:** Unknown (Shanti / Barcode Solutions)

---

### Summary

Original WordPress + WooCommerce site hosted on A2 Hosting via Barcode Solutions reseller.
