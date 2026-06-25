# BMBooks Action Items

**Last updated:** June 17, 2026

---

## 🚨 Pre-Launch (must do before go-live)

| Task | Owner | Status | Notes |
| --- | --- | --- | --- |
| **Bug: Collection pages show only a handful of products despite thousands assigned** | Lance | ⏳ Verifying | **Root cause (2026-06-17):** Products were `active` but not published to the Online Store sales channel. The sync script creates products with `published_scope: "web"` + `status: "draft"` — draft products don't get published to any channel regardless of `published_scope`. Bulk-activating to "active" in admin changed status but didn't retroactively publish to Online Store. **Fix:** Selected all products in admin → added to Online Store sales channel. After bulk publish, Crime & Thriller went from 9 → 77 products visible; Shopify still propagating — check full count 2026-06-18. **Prevention:** New products created with `AUTO_PUBLISH = True` (since 2026-06-15) are created as `active` with `published_scope: "web"`, which should correctly publish to Online Store. Monitor next sync cycle to confirm new products appear on storefront. |
| **Verify AUTO_PUBLISH = True on shop machine + test** | Lance + Louisa | ⏳ Louisa to test | Local copy updated to `True` (2026-06-15). Confirm shop machine copy also shows `True` via Chrome Remote Desktop. Ask Louisa to add a test product in Bookscan with a price set, then verify it appears in Shopify as `active` (not `draft`) within the next hourly sync run. **Also verify** the new product is published to the Online Store sales channel and appears on the storefront — if not, the sync script needs a `publishablePublish` GraphQL mutation added (see collection page bug fix 2026-06-17). |
| Verify BookHub integration works post-migration | Lance | ⏳ Pre-launch | BookHub (bookhub.co.nz) shows BMBooks on every product page with: map link, price, suburb, stock count, and "Go to Store" link to the product page. Key risk: "Go to Store" links point to WooCommerce URLs — these will 404 after migration if BookHub doesn't update them. Steps: (1) Contact BookHub to understand how they source product data and build "Go to Store" links — ISBN-based or URL-based? (2) Provide Shopify store URL and confirm they can update links before go-live. (3) Confirm price and stock data feed still reaches BookHub from the new platform. |
| Gift cards / vouchers — map physical workflow to Shopify | Lance + Louisa | ⏳ Pending | BMBooks has two voucher types: (1) Own vouchers — physical card, customer buys online or in store, staff create physical voucher, post or hold for collection. (2) Industry book tokens (TOK dept) — redeemable at any participating bookseller. Need to figure out: how customer redeems a physical voucher against an online Shopify order, and whether to keep TOK products on the website or exclude. Follow up with Louisa once she's had time in admin. |
| Confirm founding year | Lance + Louisa | ⏳ Next Louisa session | GBP shows December 1996 — ~29 years old, NOT 65. Confirm with Louisa. Audit: About page, marketing copy, LinkedIn, social bios. |

---

## 🟡 Go-Live Day

| Task | Owner | Status | Notes |
| --- | --- | --- | --- |
| Domain connection | Lance + Abbey | ⏳ Planned | Coordinate with Black Sheep Design |
| Featured images for new collections | Lance | ⏳ Go-live day | Shopify admin → each collection → Collection image. Pick one strong cover per genre (Romance, Horror, Manga, Crime & Thriller, Translated Fiction). |
| Submit sitemap to Bing | Lance | ⏳ Go-live day | Bing Webmaster Tools (bmbooksellers@gmail.com) → Sitemaps → `https://bmbooks.co.nz/sitemap.xml`. AFTER domain pointed to Shopify. Also check AI Performance (BETA) tab. |
| Submit sitemap to Google Search Console | Lance | ⏳ Go-live day | After domain switch: GSC → Sitemaps → confirm sitemap submitted. Check Coverage report — indexed count should climb to ~34k pages within days. |
| Verify schema markup with Rich Results Test | Lance | ⏳ Go-live day | After domain live: search.google.com/test/rich-results → test any product URL. Confirm BookStore + Book + bookGenre schemas detected. |
| Remove store password | Lance | ⏳ Go-live day | Remove password protection once domain is live. |

---

## 🟢 Post-Activation

| Task | Owner | Status | Notes |
| --- | --- | --- | --- |
| Activate Searchanise collection filters | Lance | ⏳ Ready | Re-indexation complete (2026-06-17). Enable filters: Genre (tags), Format (product type), Price slider, Availability. Exclude `_` prefix system tags from filter display. |
| Review collections after sync goes live | Lance + Louisa | ⏳ Post-activation | Review collection assignments, confirm product counts look right. |
| Review remaining unknown binding codes | Lance + Louisa | ⏳ Post-activation | 26 unknown codes remaining (~360 products). Map to human-readable labels and add to BINDING_MAP in bookscan_sync.py. |
| Fix blank-publisher vendor on no-publisher products | Lance | ⏳ Post-activation | 2,512 products show "Bruce McKenzie Booksellers" as vendor. Theme Liquid already hides this. Sync script fix pending. |
| Improve collections directory page | Lance | ⏳ Post-activation | Set featured images on main nav collections, consider "Browse by Genre" grid on homepage. |
| **Bug: BookKeeper UI — "changed" column blank on updated product link** | Lance | 🐛 Bug | Clicking the changed/updated link correctly identifies the product that changed, but the column showing *what* changed is blank. Should highlight the specific field(s) that differ from the previous sync (e.g. price, title, binding). Investigate what data is available at the point the link is rendered and wire it through to the display. |
| **BookKeeper UI — add View Log button** | Lance | ⏳ Post-activation | Currently pressing "Sync Now" wipes the previous sync info from the UI. To see the log you have to navigate to the BookKeeper folder and open the file manually. Add a View Log button that opens the current log in a read-only pane in the UI. Log must be read-only — no editing or clearing from the UI. |
| Publish new products as `active` (not `draft`) in bookscan_sync.py | Lance | ⏳ Post-activation | Currently all newly created products sync in draft state. Change default to `published`. Guard logic required before publishing: (1) price must be present and > 0; (2) title must not be blank. Define any additional "ready to publish" criteria with Louisa before implementing. |
| BookKeeper UI — draft status alert for Louisa | Lance | ⏳ Post-activation | Add a view in the BookKeeper GUI showing products currently sitting in draft status (count + list). Lets Louisa identify books that failed the publish-ready check and take action. Backend: query Shopify for products where `status = draft` and `vendor` matches sync source. |

---

## 🟠 Post-Go-Live

| Task | Owner | Status | Notes |
| --- | --- | --- | --- |
| Show author in Searchanise instant search dropdown | Lance | ⏳ Post go-live | "Additional product field" only shows standard Shopify fields — not metafields. Needs Searchanise template editor (Pro) or custom JS injection. |
| Searchanise instant search — dropdown gap | Lance | ⏳ Post go-live | Gap between search bar and dropdown (header background shows through). CSS-only fixes attempted 2026-06-17 (`align-items: flex-end`, `padding-block-end: 0`) — didn't close the gap; caused search bar to shift. Reverted. Likely needs Searchanise dropdown DOM inspection (`#snize-instant-search-results`) to find the right target. Low priority. |
| Homepage hero — illustrated storefront | Lance | ⏳ Post go-live | Replace photo hero with watercolour + ink illustration of 37 George Street storefront. (A) AI-generated — 30–60 min; (B) commission illustrator — $150–400 NZD. |
| Logo lockup — finalise wordmark | Lance | ⏳ Post go-live | 3 options on Desktop (logo-option-a/b/c.png). |
| Fix wishlist heart disappearing after Add to Cart | Lance | ⏳ Post go-live | Vtl app conflict — doesn't block purchases. |
| Remove share button from wishlist page | Lance | ⏳ Post go-live | Needs selector inspection while logged in with wishlist items. |
| Personalise login/account page | Lance | ⏳ Post go-live | Explore New Customer Accounts personalisation options. |
| About Us + Visit Us — fix subheadings | Lance | ⏳ Post go-live | "Opening Hours" etc. are `<p>` tags — change to `<h2>` in admin page editor. |
| Check all page links | Lance | ⏳ Post go-live | Footer, navigation, 404 page audit. |
| Non-branded keyword SEO rollout | Lance | ⏳ Post go-live | Collection SEO copy already written — apply post-sync. |
| SEO backlinks campaign | Lance | ⏳ Post go-live | PNCC directory, City Library, Booksellers NZ, NZ Book Month. |
| Shopify Product Taxonomy | Lance | ⏳ Post go-live | Add `--taxonomy` flag to `genre_enrichment_v2.py`. BIC codes map cleanly to Shopify's Standard Product Taxonomy — zero extra API calls. **Why bother:** tax (NZ) and search (Searchanise) are unaffected, and custom metafields (author, ISBN, etc.) already cover what taxonomy metafields would add. The only real value is **cross-channel sales** — Shopify maps its taxonomy directly to Google's product taxonomy, so if Google Shopping or Meta Shops are ever activated, correctly categorised books get better placement and eligibility. Don't use Shopify Magic — the BIC-based automation is more accurate and consistent across 34k products. |
| Add editorial descriptions to major collection pages | Lance | ⏳ Post go-live | Fiction, Non-Fiction, Children's, NZ Fiction, Biography — add 50–150 words each. |
| BreadcrumbList schema on collection pages | Lance | ⏳ Post go-live | Live on product pages — add to collection pages for Google search snippet breadcrumbs. |
| Build Browse by Genre directory page | Lance | ⏳ Post go-live | `/pages/browse-genres` with H1, grid of ~20 collections + descriptions. |
| Standardise tag taxonomy | Lance | ⏳ Post go-live | Document naming convention before adding more smart collections. |
| Category management dashboard | Lance | ⏳ In progress | Standalone HTML + Python proxy dashboard showing main categories → sub-categories with live Shopify product counts, audit status, and industry alignment. Two views: Louisa (clean) and Lance (technical). Files: `Tools/category_dashboard.py` + `Tools/category_dashboard.html`. Token via env var `SHOPIFY_ACCESS_TOKEN`. Created during category audit 2026-06-20. |
| Romance sub-genres Level 3 | Lance | ⏳ Post go-live (3mo) | Contemporary Romance 167 (`FRD`), Historical Romance 53 (`FRH`). Create as L3 sub-collections. |
| Science Fiction standalone collection | Lance | ⏳ Post go-live (6mo) | 334 Sci-Fi + 564 Fantasy currently combined. Split once enrichment data is stable. |
| Investigate AU calculated shipping (plan upgrade) | Lance | ⏳ Post go-live | AU customers pay $0 then get manual invoice — sometimes cancel, losing commission. Carrier-calculated rates require plan upgrade. |
| Return 404/410 for out-of-print products | Lance | ⏳ Post go-live | Verify sync archives products when CSTATUS → OP/RP/RUC. |
| Review Bookscan web export mapping | Lance + Louisa | ⏳ Post go-live | Confirm WEBLIST.DBF fields still correct source of truth. |
| Clean up WEBLIST orphans | Louisa | ⏳ Post go-live | ISBNs active in WEBLIST but missing from MASTER. Pull fresh DBFs, re-run orphan query. |
| Quarterly BookData audit for Louisa's team | Lance | ⏳ Quarterly (first ~2026-08) | Re-run BookData OOP audit; share new CSV with Louisa's team. |
| Bookscan category review + Romance/Horror SUBCATs | Lance + Louisa | ⏳ Post go-live | Romance and Horror don't exist as Bookscan SUBCATs. Discuss with Louisa. |
| **BookScan cleanup: History vs Politics subcat overlap** | Louisa | ⏳ Post go-live | **Problem:** ~2,732 products under History And Politics maincat have BOTH the "History" and "Politics" subcat tags. This means splitting into separate History and Politics collections shows near-identical results. **Action for Louisa:** Review products in BookScan's History And Politics maincat and assign each to either History OR Politics (or both only where genuinely relevant). **Follow-up after cleanup:** (1) Create standalone "Politics" smart collection (tag=Politics); (2) Add both "History" and "Politics" tags to Non-Fiction umbrella collection rules. Identified during category audit 2026-06-20. |
| **Flag for Louisa: Audio products — keep or remove from web?** | Louisa | ⏳ Post go-live | 9 Audio Books + 58 Music CDs currently tagged but not browsable (no collection, not in any umbrella). Audio is not a book category and likely not relevant for online sales. Louisa to decide: (1) remove from WEBLIST in BookScan so they stop syncing, or (2) keep and create a collection. Identified during category audit 2026-06-20. |
| **BookScan restructure: realign maincats to industry standards** | Louisa + Lance | ⏳ Post go-live | BookScan's maincat groupings don't match how customers browse or how any other bookstore categorises. Standalone collections already exist so customers can browse directly — this is about fixing the umbrella groupings. **Changes needed in BookScan:** (1) Move "Food And Beverage" (1,199 products) out of Well Being — should be standalone or under a new "Lifestyle" maincat; (2) Move "Business" (535), "Economics" (174), "Philosophy" (322) out of Sciences — Business & Economics should be its own maincat, Philosophy under Humanities; (3) Move "Religion" (207) out of History And Politics — standalone everywhere in the industry; (4) Move "Humour" (151) out of Well Being — standalone at Whitcoulls/Waterstones. Once maincats are reassigned in BookScan, the sync will apply correct maincat tags and umbrella collections will group properly. Identified during category audit 2026-06-20. |
| Set up post-launch agent-team monitoring | Lance | ⏳ Post go-live | Claude Code agent teams: sync log watcher, order anomaly watcher, site health watcher. |
| Post-go-live monitoring setup — multi-dimensional | Lance | ⏳ Post go-live | Multi-agent monitoring across: (1) Engineering — Core Web Vitals regression alerts, Lighthouse CI on key pages; (2) Infrastructure — sync health, Shopify API error rates, DBF change detection post-FRANZ release; (3) Design/CX — broken images, layout shifts, 404s on nav links, checkout funnel drop-offs. Agents run in parallel across dimensions rather than one person checking everything manually. |
| Download UpdraftPlus full site backup | Lance | ⏳ Post go-live | Save to local storage before cancelling hosting. |
| Cancel Shanti/FRANZ hosting contract | Lance | ⏳ Post go-live | Minimum 3 months after go-live confirmed stable. Monitor June 15 FRANZ release for DBF structure changes. |
| Set up password manager for BMBooks credentials | Lance + Louisa | ⏳ Post go-live | 1Password or Bitwarden. Move API token from hardcoded script to .env file on shop machine. |
| Analyse WooCommerce analytics reports | Lance | ⏳ Post go-live | Export order history as baseline for Shopify performance comparison. |
| Integrate BIC tagging into bookscan_sync.py | Lance | ⏳ Post go-live (after enrichment proven stable) | Have hourly sync read BICMAIN and apply genre tags automatically for new stock. Must carry SKIP list + DUAL_TAG_PAIRS from genre_enrichment_v2.py. |
| Audit product weight + dimensions for carrier-calculated shipping | Lance | ⏳ Future | Only relevant if upgrading plan. |
| Convert parent category collections to hub pages | Lance + Louisa | ⏳ Future | BookHero model: rich editorial hub pages with sub-category carousels, staff picks. |
| Explore Shopify POS | Lance | ⏳ Future | Would unify online + in-store gift card redemption and inventory. |

---

## 🔵 Low Priority / Polish

| Task | Owner | Status | Notes |
| --- | --- | --- | --- |
| Icon order: NZD › Account › Heart › Cart | Lance | ⏳ Low priority | CSS `order: 100` on `.cart-drawer` attempted. Swym injects heart dynamically after cart-drawer. Full fix deferred post go-live. |
| Remove Swym Wishlist remnants from theme | Lance | ⏳ Pending | Online Store → Customize → App Embeds → toggle off Swym. Also check config/settings_data.json for leftover keys. |
| Review remaining email templates | Lance | ⏳ Pending | Brand consistency check. |
| Cover image for Brand settings | Lance | ⏳ Pending | Waiting on high-res store photo. |
| Transfer GA ownership to Louisa | Lance | ⏳ Future | When Louisa ready. |
| Deploy BookKeeper docs site | Lance | ⏳ Post go-live | Docusaurus → Cloudflare Pages → `help.bmbooks.co.nz`. ~45 min. |
| Document Catalogues module for Louisa | Lance | ⏳ Quick win | Half-page note on using Bookscan Catalogues for price audits. |
| Update Google Reviews count on product page badge | Lance | ⏳ Periodic | Hardcoded 4.8 stars / 221 reviews — update when count changes. |
| High-res book cover images | Lance | ⏳ Post go-live | 9,209 products on low-res thumbnails. Best path: Fiddler capture of Bookscan's Nielsen call. |
| Goodreads inline book ratings | Lance | ⏳ Future | API deprecated 2020 — revisit when reliable option available. |

---

## 🔧 Phase 2 & 3 — Future Development

| Task | Owner | Status | Notes |
| --- | --- | --- | --- |
| Build inbound order sync | Lance | ⏳ Phase 2 | Poll Shopify orders → deduct stock in Bookscan DBF. Replaces Barcode Solutions/FRANZ middleware. |
| Investigate DBF write safety | Lance | ⏳ Phase 2 | File locking test while Bookscan is running. Prerequisite for inbound order sync and back-population. |
| Write enriched genre categories back to Bookscan | Lance + Louisa | ⏳ Phase 2 | Write genre tags back to WEBLIST.DBF so normal sync pipeline carries them automatically. Requires Louisa to create Romance/Horror/Manga/Thriller SUBCATs. |
| Bookscan upstream bibliographic-refresh automation | Lance | ⏳ Phase 3 | TitlePage nightly + Nielsen periodic refresh. |
| Vendor query to FRANZ Technologies | Lance | ⏳ Phase 3 | Report Writer CLI + Bookscan.exe CLI args. Also: flag Shopify connector opportunity. |
| Investigate Bookscan plugin / regasm extension | Lance | ⏳ Future | `woolibrary.dll` .NET assembly — long-term strategic option. |

---

## 🚀 Post-Migration — Lance's Next Chapter

| Task | Status | Notes |
| --- | --- | --- |
| Convert CVs to PDF | ⏳ Pending | Both markdown files ready |
| Write cover letters | ⏳ Pending | Need specific role + company |
| Get Louisa's permission to use BMBooks as case study | ⏳ Post go-live | Ask once migration confirmed stable |
| Write BMBooks case study | ⏳ Post go-live | Wait until 1 month of Shopify data available |
| Publish LinkedIn post | ⏳ Post go-live | Migration journey — real problems, real numbers |
| Workspace audit + next project setup | ⏳ Post go-live | Full audit of bmbooks-workspace structure, memory files, Claude skills, and tools used. |
| Upload BMBooks project to personal GitHub (portfolio) | ⏳ Post go-live | **Must scrub before upload:** Move API token to `.env`, exclude log/CSV/DBF files, get Louisa's permission. |
| Define service offering | ⏳ Future | "E-commerce consultant for independent retailers" |
| Build simple landing page | ⏳ Future | Who you help, what you do, case study link |
