# BMBooks Completed Tasks — Archive

Older completed items moved here to keep BMBooks_Action_Items.md lean.

---

| Task | Completed | Notes |
| --- | --- | --- |
| Choose Searchanise plan — Pro | 2026-06-09 | Upgraded to Pro plan (~$295 NZD/month, up to 50k products). Required for full 37k product catalogue indexing. |
| Searchanise install + basic configuration | 2026-06-09 | Installed via Shopify App Store. Instant search dropdown live. Custom CSS: cream bg, navy label text, "Products" label styled, 10 results, title 1.2rem bold, max-height capped. Placeholder: "Search by Title, Author, Keyword or ISBN…". Author metafield (`bookscan.author`) added under Search & Navigation → Preferences → Metafields (Search + Filter). |
| Header search bar — static inline | 2026-06-09 | `snippets/bmbooks-search-bar.liquid` — cream bg `#fdf8f3`, dark text, green submit button. Centred via `1fr 1.5fr 1fr` grid override in `header-row.liquid` (hardcoded `item_column = 'center'`, `item_row = 'top'`). Mobile: full-width row below logo (`header__row--mobile-search`). CSS specificity fix: all input selectors prefixed with `.bmbooks-search-bar`. |
| Typography — Open Sans + Libre Baskerville | 2026-06-09 | Body: Open Sans. Heading/Subheading/Accent: Libre Baskerville. Set via `settings_data.json` (`type_body_font: open_sans_n4`, `type_heading_font/type_subheading_font/type_accent_font: libre_baskerville_n4`). Pulled from staging, pushed to production. |
| Zero-price product handling | 2026-06-09 | `fix_zero_price_drafts.py` run — 104 products set to Draft. Sync now forces zero-price → Draft always; auto-publishes when price goes $0→>$0 and AUTO_PUBLISH=True. `_check_warnings()` updated: "No price — synced as Draft". |
| Bulk-activate products (Draft → Active) | 2026-06-09 | All 37,836 products activated. Store remains password-protected. AUTO_PUBLISH = True set on shop machine — new priced books will auto-publish on sync. |
| Fix duplicate collections | 2026-06-09 | Consolidated: Biography & Memoir (OR: Biography+Biographies, 1,936), Gifts & Stationery (OR: 3 tags, 2,000), Gardening (OR: Gardening+The Garden, 346). Deleted: Politics, Gifts, Stationery, Biographies, The Garden. Nav updated: Gifts & Stationery and Games & Puzzles both promoted to top-level direct links. |
| Department exclusions — confirmed with Louisa | 2026-06-09 | Full exclude list: AAA, FRE, GFS, SPE, XXX, MAG, AUD, CDS, EXP, FUN, KIT, MON, POS, STK, YOG, blank. TOK and VOU removed from exclude — Book Tokens (5) and BMBooks Vouchers (10) now syncing. Binding codes VO + ** added to BINDING_MAP. |
| NZ shipping rates — confirmed with Louisa | 2026-06-09 | Louisa confirmed: keep current setup as-is. No changes needed. |
| Expand STATUS_EXCLUDE to full NOWEB=True set | 2026-06-09 | 20-code NOWEB set. 246 additional books excluded. Deployed to shop machine. |
| Update "available to order" verbiage | 2026-06-09 | "We can order this for you · Allow 1–2 weeks for delivery". Badge colours darkened. |
| Review shipping date estimates at checkout | 2026-06-09 | North Island 2–3 days, South Island 3–5 days, Rural 4–6 days. In Stock badge aligned. |
| Add `bookGenre` to Book schema markup | 2026-06-09 | Loops product tags, filters `_` system tags, outputs as JSON array in Book schema on all product pages. |
| Confirm "You may also like" algorithm | 2026-06-09 | `recommendation_type: "related"` — Shopify native engine. Not random. No change needed. |
| Report: books with no BIC code | 2026-06-09 | 8,735 books (23%). Top gaps: Art (882), Environment (585), Sport (352), Gardening (321). |
| Walk Louisa through order fulfillment workflow | 2026-06-08 | Full walkthrough. Louisa now has admin access. Go-live 1–2 weeks away. |
| Louisa meeting — decisions confirmed | 2026-06-08 | NOWEB expansion, no launch comms needed, anomaly codes, category depth, author format First Last confirmed. |
| Launch communication | 2026-06-08 | No announcement needed — just switch domain. |
| Genre enrichment 1–9 | 2026-06-07/08 | 2,820 books tagged across 15+ genres. 0 errors. 5 smart collections live: Romance (270), Horror (123), Manga (238), Thriller (528), Translated Fiction (29). Crime Fiction → Crime & Thriller (301 redirect, 1,567 books). Tag preservation confirmed. |
| Add editorial descriptions to new collection pages | 2026-06-08 | Romance, Horror, Manga, Crime & Thriller, Translated Fiction — 50–150 words each. |
| Block filter + tag URLs in robots.txt | 2026-06-08 | Already in `robots.txt.liquid`. Confirmed. |
| Noindex `/collections/all` | 2026-06-08 | `Disallow: /collections/all` in `robots.txt.liquid`. Meta noindex also added to `theme.liquid`. |
| Confirm category source of truth with Louisa | 2026-06-08 | MAINCAT/SUBCAT manually entered in Bookscan. |
| Schema markup — LocalBusiness + Book | 2026-06-05 | BookStore + Book schema on all pages. Validated with Rich Results Test. |
| Product page — breadcrumbs | 2026-06-05 | "Home › [Collection] › [Product Title]" live. |
| Mobile UAT — full core storefront | 2026-06-05 | All core pages passing on Playwright + real device. |
| Design polish sprint 1 + 2 | 2026-06-04/05 | Sticky nav, cream background `#fdf8f3`, carousel max 16, scroll progress indicator, collection page image sizing (320px contain left), card gaps 4/32px, title 2-line clamp. Smart nav flicker fix (8px threshold), product page title bold + price 1.6rem, "You may also like" heading bold + max 8, "Book Details" normalised, sticky image jump fixed (clip-path), "Browse Collections" button. |
| Set up Shopify CLI + theme sync | 2026-06-01 | CLI v4.1.0. Staging: 150391423054. Production: 149898395726. |
| Test all email notifications | 2026-06-03 | Templates reviewed. Logo lockup uploaded. |
| Confirm AU flat rate with Louisa | 2026-06-03 | $0 at checkout, manual invoice before dispatch. |
| Confirm BookKeeper hourly sync running | 2026-05-31 | UNC paths confirmed. Running cleanly on shop machine. |
| AI optimization sprint | 2026-05-29 | Bing WMT setup, GBP updated, llms.txt created. Sitemaps queued for go-live day. |
| Toast notifications + richer log detail | 2026-05-27 | winotify toasts on start/complete/error. DETAIL_C/DETAIL_U log lines. Updated popup shows field diffs; Created popup shows full book detail. |
| Build sync GUI (tkinter desktop app) | 2026-05-27 | BookKeeper — tkinter dashboard polling log every 2s. Status dot, progress bar, Created/Updated/Warnings/Errors counts, activity log, Sync Now button. Deployed to Z:\BookKeeper. |
| Set up Windows Task Scheduler on shop machine | 2026-05-27 | Hourly run of `bookscan_sync.py --once`. Fixed 2026-05-30 — changed Program/script to full Python path, changed Start In to UNC path `\\Server\c\BookKeeper` (mapped drives not available to Task Scheduler). |
| Deploy BookKeeper GUI + Sync Now.bat to shop machine | 2026-05-27 | Files in `Z:\BookKeeper` (backed up on network drive). Shortcut on Louisa's desktop. bookkeeper.ico created. |
| Send binding codes email to Louisa | 2026-05-25 | Sent — 28 unknown binding codes, ~390 products affected, top 10 listed. |
| Fix gift card denomination selector | 2026-05-25 | Added variant picker block in theme editor. Fixed label bold + dropdown border via Custom CSS. |
| Confirm Bestsellers tag usage with Louisa | 2026-05-25 | Confirmed — Louisa actively maintains the Bestsellers tag in Bookscan. |
| Complete Post-sync 6 UAT spot-check (TC60–TC69) | 2026-05-23 | All TCs passed except TC65 (image quality — deferred post-launch). |
| Deploy author name fix to shop machine | 2026-05-25 | Authors now display as Firstname Lastname on live store. |
| Add dimension metafields to sync | 2026-05-25 | Height + Width displaying on product page. ISBN typo fix applied. |
| Book categories for navigation | 2026-05-25 | 75 smart collections live. |
| Set up navigation + smart collections | 2026-05-25 | 75 collections created via create_collections.py. |
| Build dropdown navigation menus | 2026-05-25 | Dropdowns live for all 7 nav parents. Labels updated to modern conventions. |
| Build homepage featured collections | 2026-05-25 | 6 sections live: New Releases (Manual), Bestsellers (Best selling), Fiction (Best selling), Kids (Best selling), New Zealand (Newest), Gifts & Stationery (Best selling). |
| Populate Browse footer column | 2026-05-25 | Footer Browse column populated. |
| Verify product field weights | 2026-05-25 | Author + ISBN confirmed in Searchanise. |
| BookData out-of-print ISBN audit | 2026-05-25 | CSV reviewed by Louisa's team. CSTATUS updates applied in Bookscan. |
| Bookscan duplicate ISBN cleanup | 2026-05-25 | Down to 1 duplicate — effectively resolved. |
| Build 8 collections (SEO) | 2026-05-25 | Superseded — 75 collections built with full SEO copy. |
| Bing Webmaster Tools — account setup | 2026-05-29 | Logged in via bmbooksellers@gmail.com. Imported Google Search Console data (bmbooks.co.nz property). Sitemap submission deferred to go-live day. |
| Deploy updated bookscan_sync.py to shop machine | 2026-05-29 | taxable: True backfilled on all 37,337 products / 29,624 variants via fix_taxable.py. variant_id fix also deployed. All future creates/updates will have taxable: true. |
| Test wishlist | 2026-05-29 | Wishlist by Square (Vitals-powered, Vtl- class prefix). Replaced Wishlist Plus by Swym. Product page "Add to Wishlist" button resized to match Add to Cart via Custom CSS (padding 14px 24px, margin-left 137px, max-width 50ch). |
| Fix wishlist heart icon disappearing when cart opens | 2026-05-29 | Resolved by switching from Wishlist Plus by Swym to Wishlist by Square. |
| Set AU flat rate + test AU checkout | 2026-05-28 | $12 NZD placeholder set. AU checkout confirmed — shipping shows, GST correctly excluded for AU address. Refine post go-live using WooCommerce AU order history. |
| Test in-store pickup flow | 2026-05-28 | Flow tested and confirmed working. |
| Investigate Starshipit paid plan for live checkout rates | 2026-05-28 | Not worth it at ~48 orders/month. Starshipit ~$49–75 NZD/month. Keep manual flat rates. Revisit if volumes exceed 200 orders/month. |
| Map WooCommerce publish status to Shopify status in sync | 2026-05-28 | No change needed. Status code exclusion handles "can't purchase" case. inventory_policy: continue is correct for all synced products. |
| Test order — NZ shipping | 2026-05-28 | Order #TNVMKGV8R. Auckland address, North Island $7.99 rate, full checkout confirmed. |
| Fix worldwide browsing / "Unavailable" button | 2026-05-28 | Root cause: Shopify Markets had non-AU countries in International market with no shipping rates → showed Unavailable. Fix: renamed International → Australia (AU only), deleted US sub-market. Worldwide visitors now see Add to Cart. Checkout restricted to NZ + AU only. |
| Connect eShip to Shopify | 2026-05-28 | Fulfillment integration live. Live checkout rates not viable on free eShip plan — manual flat rates kept. Louisa notified. |
| Test gift card purchase flow | 2026-05-28 | Denomination selector working. Full purchase flow verified. |
| Confirm backorder setting source with Louisa | 2026-05-28 | Excluded status codes (OP/RP/RUC) hide the product entirely. Active products with 0 stock stay on site with inventory_policy: continue — Louisa backorders. No sync change needed. |
| BookKeeper GUI — data quality warnings | 2026-05-28 | _check_warnings() fires on Created + Updated: No price, Missing author, Unknown binding. WARN log lines emitted. Orange "Warnings: N" button in GUI. Status dot turns orange. Warning count in completion toast. |
| BookKeeper GUI — persist last-run summary | 2026-05-28 | last_run_summary.json written at sync completion with all 4 item lists (created/updated/warnings/errors) including full detail/diff text. GUI pre-populates all lists on startup — Louisa sees previous sync results whenever she opens BookKeeper. |
| Fix blank "Changed" column in Updated popup | 2026-05-28 | Root fix: updated_list + created_list now stored in last_run_summary.json with diff text. Secondary fix: popup auto-refreshes treeview every 2s while open, resolving live timing gaps. |
| BookKeeper GUI — resizable window | 2026-05-28 | resizable(True, True) + minsize(600, 420). Progress bar stretches with window width. Activity log grows vertically. |
| BookKeeper GUI — onboarding & usability for Louisa | 2026-05-28 | Friendlier status language ("Up to date", "Syncing your books to Shopify...", "Sync issue — see errors below"). Guidance note below counts ("Fix these in Bookscan — they'll clear on the next sync."). "?" help button → plain-English popup. Hover tooltips on all key elements. |
| Sync Now.bat — no console window | 2026-05-28 | Updated to use `pythonw` + `start` command. Command window no longer stays open — BookKeeper launches cleanly. |
| TY binding code mapped | 2026-05-28 | "TY": "Toy/Plush" added to BINDING_MAP. Frank Frog and Duke - Flip Puppy no longer trigger unknown-binding warnings. |
| Order fulfillment documentation | 2026-05-28 | bookkeeper_docs/docs/sync/order-fulfillment.md — manual Shopify + Bookscan workflow, field mapping table, edge cases (partial, cancel, discount), Phase 2 note. |
| Image source logging fix | 2026-05-28 | resolve_image() now returns (dict, label) tuple with actual folder name. Log correctly shows LargeImages / MediumImages / catalog / placeholder instead of always "catalog". |
| Toast notifications + richer log detail | 2026-05-27 | winotify toasts on start/complete/error. DETAIL_C/DETAIL_U log lines. Updated popup shows field diffs; Created popup shows full book detail. |
| Build sync GUI (tkinter desktop app) | 2026-05-27 | BookKeeper — tkinter dashboard polling log every 2s. Status dot, progress bar, Created/Updated/Warnings/Errors counts, activity log, Sync Now button. Deployed to Z:\BookKeeper. |
| Set up Windows Task Scheduler on shop machine | 2026-05-27 | Hourly run of `bookscan_sync.py --once` from `Z:\BookKeeper`. |
| Deploy BookKeeper GUI + Sync Now.bat to shop machine | 2026-05-27 | Files in `Z:\BookKeeper` (backed up on network drive). Shortcut on Louisa's desktop. Confirmed working — green dot, log polling, 0 errors. bookkeeper.ico created. |
| Send binding codes email to Louisa | 2026-05-25 | Sent — 28 unknown binding codes, ~390 products affected, top 10 listed. Asked Louisa to confirm label + whether each should show on site. |
| Fix gift card denomination selector | 2026-05-25 | Added variant picker block in theme editor. Fixed label bold + dropdown border via Custom CSS (`label[for^="Option-"]`, `.variant-option__select`). |
| Run homepage performance audit | 2026-06-12 | Baseline (Chrome DevTools Lighthouse while logged into admin): Performance 67, LCP 5.9s, FCP 2.5s, TBT 110ms, CLS 0.001, TTFB 80ms. Note: preview bar font (GTStandard-MMedium.woff2) inflated LCP — real production score estimated ~72–75. |
| Fix eager-loading bug in card-gallery.liquid | 2026-06-12 | `Theme/snippets/card-gallery.liquid` line 137: `if forloop.first` guard only — fixes original operator-precedence bug (was loading ALL images in sections 1–4 eagerly; now only first image per card eager across all sections). Note: section.index threshold attempts caused carousel images to disappear (lazy images in hidden slideshow containers never loaded). |
| Reduce carousel max_products 16 → 8 | 2026-06-12 | Changed to 8 via Theme Editor (also renamed duplicate "New Releases" to "Bestsellers"). DOM dropped 10,217 → 6,089. Pushed staging → production via CLI (templates/index.json only). |
| Re-run Lighthouse after Tier 1 fixes | 2026-06-12 | LH5 (incognito / real production): **Performance 81, LCP 4.0s, TBT 50ms, CLS 0, FCP 2.0s, DOM 5,846.** LCP at 4.0s boundary — render-blocking compiled CSS 300ms is the bottleneck; cannot be deferred on Shopify. |
| Implement carousel lazy loading + sessionStorage cache | 2026-06-12 | Not needed — score 67 matches original baseline with much better TBT. Diminishing returns. |
| Test search (Searchanise) | 2026-06-15 | Playwright tests run against staging. Author search ✅, ISBN search ⚠️ (mechanism works), Genre search ✅, Search results page ✅ (46 products for "new zealand"), `_cstatus-*` in filters ✅ clean. Tests saved: `UAT/playwright/tests/searchanise.spec.js`. |
| Update "available" label on product page (Louisa feedback) | 2026-06-15 | Changed "We can order this for you · Allow 1–2 weeks for delivery" → "We can order this for you – ETA to be advised". Live on production via `templates/product.json`. |
| Run Searchanise re-indexation | 2026-06-17 | Force re-index completed. Collection filters now unblocked. |
| Update sync interval to 1 hour in bookscan_sync.py | 2026-06-17 | Changed `SYNC_INTERVAL_HOURS = 2` → `1`. Deployed to shop machine. Task Scheduler already set to 1 hour. |
| Fix BINDING_MAP — BO and BB codes (Louisa feedback) | 2026-06-20 | Shop machine had swapped mappings: BB → "Big Book", BO → "Board Book". Corrected to BB → "Board Book", BO → "Boxed". Local script updated 2026-06-15. Existing products fixed via `fix_binding_codes.py`: 921 → "Boxed", 837 → "Board Book", 0 errors. Validated by Lance. |