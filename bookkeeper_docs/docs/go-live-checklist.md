---
sidebar_position: 8
---

# Go-Live Checklist

---

## Phase 1 — Before Go-Live (Complete these first)

### Payments & Account
- [x] Louisa uploads Shopify Payments verification docs (Step 5 of 5) — submitted 7 April, approved
- [x] Louisa verifies books@bmbooks.co.nz email — resolved via domain authentication
- [x] Louisa completes 2FA + adds bank account — bank account ANZ ****4200 entered 2026-05-07, daily payouts NZD ✓
- [x] Customer billing statement set — "BMBooks" (19-char Shopify limit; "Bruce McKenzie Books" rejected at 20 chars) ✓
- [ ] Shopify Payments confirmed active — test payout after first real order

### Products & Catalog
- [x] Ebility/Bookscan connector — abandoned. Custom Python sync built as replacement. ✓
- [x] Create custom app in live Shopify store — created via Dev Dashboard (legacy apps deprecated Jan 2026). Token retrieved via get_token.py. ✓
- [x] Create metafield definitions in live store — **6 definitions**: bookscan.author, bookscan.isbn, bookscan.pages, bookscan.publication_date, bookscan.cstatus, bookscan.department. All Single line text. Pages was initially Integer — deleted and recreated as text 2026-05-12 ✓
- [x] Install Python + bookscan_sync.py on shop machine — Python 3.14, script at `C:\BookKeeper\bookscan_sync.py`, reads DBFs from `Z:\bookscan` (mapped drive) ✓
- [x] Set MAX_PRODUCTS = None in bookscan_sync.py — May 2, 2026 ✓
- [x] CSTATUS + DEPARTMENT filters confirmed with Louisa — `STATUS_EXCLUDE = {OP, RP, RUC}`, `DEPARTMENT_EXCLUDE = {AAA, VOU, FRE, TOK}` 2026-05-11 ✓
- [x] Hidden tag + metafield infrastructure for post-launch filterable cleanup — `_cstatus-{code}`, `_dept-{code}` tags 2026-05-11 ✓
- [x] Replace REST `find_by_sku` with GraphQL — fixes duplicate-products bug on full-sync restart 2026-05-12 ✓
- [x] Switch `set_inventory` to GraphQL `inventorySetOnHandQuantities` — REST inventory endpoints returning 404 on this store 2026-05-12 ✓
- [ ] **Bookscan sync complete** — IN PROGRESS as of 2026-05-12, ~43% through, ~30–50h remaining. ~36 duplicates from pre-fix runs to clean up post-sync.
- [ ] **Post-sync 1: Run `dedupe.py`** — clean up ~36 duplicate products from pre-GraphQL-fix runs
- [ ] **Post-sync 2: Diagnose inventory "ghost item" issue** — run `diagnose_inventory.py`, determine fix
- [ ] **Post-sync 3: Fix inventory updates on the ~344 affected products** — approach depends on diagnosis output (likely delete+recreate)
- [ ] **Post-sync 4: UAT spot-check 20 diverse products** — verify titles/prices/stock/vendor/metafields/tags
- [ ] **Post-sync 5: Bulk-activate products (Draft → Active)** — coordinated with Louisa for go-live timing
- [ ] Windows Task Scheduler configured (2-hour automated run) — NOT YET; **must wait until inventory fix is verified** (otherwise scheduled syncs propagate broken inventory state)
- [ ] "Sync Now.bat" created on Louisa's desktop — NOT YET
- [ ] Searchanise Force Re-indexation run — after bulk-activate
- [ ] Product field weights verified (Author, ISBN)
- [x] Metafields confirmed working — all 6 verified on live products 2026-05-12 ✓

### Navigation & Collections
- [x] Louisa confirms book categories — Fiction, Young Adult, Kids, Non-Fiction, The Arts, New Zealand, Gifts & Stationery ✓
- [x] 11 collections built with SEO copy — May 3, 2026 ✓
  - Smart: Fiction, Young Adult, Kids, Non-Fiction, The Arts, New Zealand, Gifts & Stationery, New Releases, Bestsellers
  - Custom (Louisa curates): Staff Picks, NZ Authors
  - All empty until sync runs — will auto-populate Tuesday
- [x] Main navigation menu updated with categories — Fiction, Young Adult, Kids, Non-Fiction, The Arts, New Zealand, Gifts & Stationery. Home removed (logo handles it). May 3, 2026 ✓
- [x] Browse footer column populated — Footer Browse menu created and assigned in theme editor. May 3, 2026 ✓
- [ ] Searchanise Collection filter tree activated — blocked until sync runs
- [x] Search empty state collection set — Fiction. May 3, 2026 ✓

### Gift Cards
- [x] Set up Shopify gift cards — denominations: $30, $40, $50, $60, $80, $100 (data-driven — $90 never sold, $10/$20 negligible) ✓

### Homepage
- [x] Featured collection sections activated — New Releases, Fiction, Kids, Staff Picks (carousel layout, Heading 3). Empty until sync runs Tuesday. May 3, 2026 ✓
- [x] Hero photo — Kirstin shoot deferred indefinitely; placeholder retained (won't do 2026-05-07) ✓
- [x] Brand colour confirmed by Louisa (#1A0A2E)

### Design & Branding
- [x] Full wordmark logo — decided to stick with the B monogram (won't do 2026-05-07) ✓
- [x] Cover image for Settings > Brand — placeholder retained (was waiting on high-res photo which is no longer happening) ✓
- [x] Footer Customer Service heading size fix (CSS — confirmed applied)

### Policies & Legal
- [x] Louisa signs off Return & Refund Policy — signed off 2026-05-07 ✓
- [x] Louisa signs off Shipping Policy — signed off 2026-05-07 ✓

### Contact & Messaging
- [x] Add "Text only — this number is not monitored for calls" note to Contact Us page

### Testing
- [ ] Place a real test order (NZ shipping)
- [ ] Place a test order (international — DHL quote appearing, $0 handling fee)
- [ ] Verify DHL Express rates for single book to UK, US, AU are reasonable before go-live
- [x] Set up package profiles — 3 profiles created (small paperback, standard hardback, large/multiple) May 3, 2026 ✓
- [ ] Confirm package dimensions with Louisa before go-live — current dimensions are estimates, update to match actual satchels/boxes used for packing
- [ ] Test gift card purchase flow
- [ ] Test in-store pickup flow
- [ ] Test wishlist
- [ ] Test search (Searchanise)
- [ ] Review full site on mobile
- [ ] Test all email notifications (order confirmation, shipping, pickup)
- [x] Check all page links working (footer, navigation) ✓
- [x] Check 404 page ✓

---

## Phase 2 — Cutover Day (With Abbey)

- [ ] Remove Shopify password protection (Online Store > Preferences)
- [ ] Ask Abbey to update bmbooks.co.nz nameservers to Shopify
- [ ] Confirm SSL certificate active on bmbooks.co.nz (Shopify handles automatically)
- [x] Set up URL redirects — 9 category redirects created May 3, 2026 ✓. Product-level redirects (38k) to be handled separately closer to cutover day.
- [ ] Keep WordPress site live until Shopify confirmed working
- [ ] Verify domain resolving correctly in browser
- [ ] Test checkout on live domain

---

## Phase 3 — Post Go-Live (First 2 weeks)

### Day 1
- [ ] Connect Google Analytics (bmbooks.co.nz GA4 property)
- [ ] Submit new sitemap to Google Search Console (Settings > sitemap.xml)
- [ ] Announce on Instagram and Facebook
- [ ] Email Louisa confirming live

### Week 1
- [ ] Monitor for 404 errors in Google Search Console
- [ ] Connect eShip (NZ Post) to Shopify — eShip > Integrations > Add Integration > Shopify (login: books@bmbooks.co.nz)
- [x] Transfer Cloudflare — staying in Lance's Gmail, not transferring ✓
- [x] Move UpdraftPlus backup to bmbooksellers@gmail.com — not needed, migrating away from WordPress ✓

### Week 2–4 (when stable)
- [x] Export full WooCommerce order history CSV — 2,396 orders, $137,344 NZD ✓
- [ ] Download UpdraftPlus full site backup to local storage
- [x] Export WooCommerce financial reports (revenue by year) — BMBooks_Revenue_By_Year.xlsx ✓
- [ ] Cancel Shanti hosting contract (minimum 3 months post go-live)
- [ ] Clean up C: drive on shop machine — 43GB used by Outlook mail cache (OST/PST). Discuss with Louisa — move PST to Z: or archive old email. Low priority.
- [ ] Set up Google Merchant / Shopping
- [ ] Begin SEO backlinks campaign (City Library, PNCC directory, Booksellers NZ, NZ Book Month)
- [ ] Ask Louisa about POS system for in-store sales — explore Shopify POS as unified option
