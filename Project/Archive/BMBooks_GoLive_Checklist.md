# BMBooks Go-Live Checklist

---

## Phase 1 — Before Go-Live (Complete these first)

### Payments & Account
- [x] Louisa uploads Shopify Payments verification docs (Step 5 of 5) — submitted 7 April, pending Shopify review
- [x] Louisa verifies books@bmbooks.co.nz email — resolved via domain authentication
- [x] Louisa completes 2FA + adds bank account — confirmed April 2026
- [ ] Shopify Payments confirmed active — test payout

### Products & Catalog
- [x] Ebility/Bookscan connector — abandoned. Custom Python sync built as replacement. ✓
- [x] Create custom app in live Shopify store — created via Dev Dashboard (legacy apps deprecated Jan 2026). Token retrieved via get_token.py. ✓
- [x] Create metafield definitions in live store — all 6 created 2026-05-12: bookscan.author, bookscan.isbn, bookscan.pages (Single line text — not Integer), bookscan.publication_date, bookscan.cstatus, bookscan.department ✓
- [x] Install Python + bookscan_sync.py on shop machine — Python 3.14 + dependencies installed 2026-05-12 via Chrome Remote Desktop ✓
- [x] Set MAX_PRODUCTS = None in bookscan_sync.py — done May 2, 2026 ✓
- [x] Bookscan sync complete — ~36,800 products uploaded 2026-05-15. Dedupe in progress (40 duplicates). Product count discrepancy under investigation. ✓
- [ ] Searchanise Force Re-indexation run
- [ ] Product field weights verified (Author, ISBN)
- [x] Metafields confirmed working — bookscan.author, bookscan.isbn, bookscan.pages, bookscan.publication_date ✓

### Navigation & Collections
- [ ] Louisa confirms book categories
- [ ] 8 collections built with SEO copy (Manga, Children's, NZ Authors, New Releases, Fiction, Non-Fiction, Staff Picks, Bestsellers)
- [ ] Main navigation menu updated with categories
- [ ] Browse footer column populated
- [ ] Searchanise Collection filter tree activated
- [ ] Search empty state collection set

### Gift Cards
- [x] Set up Shopify gift cards — denominations: $30, $40, $50, $60, $80, $100 (data-driven — $90 never sold, $10/$20 negligible) ✓

### Homepage
- [ ] Featured collection section activated
- [ ] Hero photo replaced (Kirstin shoot)
- [x] Brand colour confirmed by Louisa (#1A0A2E)

### Design & Branding
- [ ] Full wordmark logo from Abbey
- [ ] Cover image added to Settings > Brand
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
- [ ] Set up package profiles in Settings → Shipping → Packages (2–3 profiles: small paperback, standard hardback, large/multiple) — DHL uses volumetric weight for international, inaccurate dimensions = inaccurate rates
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
- [ ] Set up URL redirects — old WordPress product/category URLs → Shopify equivalents (Online Store > Navigation > URL Redirects)
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
- [ ] Set up Google Merchant / Shopping
- [ ] Begin SEO backlinks campaign (City Library, PNCC directory, Booksellers NZ, NZ Book Month)
- [ ] Ask Louisa about POS system for in-store sales — explore Shopify POS as unified option
