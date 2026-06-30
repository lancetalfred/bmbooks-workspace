# BMBooks Action Items

**Last updated:** June 30, 2026

---

## 🚨 Pre-Launch (must do before go-live)

*(Migrated to GitHub Issues — see milestone ["Pre-Launch"](https://github.com/lancetalfred/bmbooks-workspace/milestone/1), 5 issues)*

---

## 🟡 Go-Live Day

*(Migrated to GitHub Issues — see milestone ["Go-Live Day"](https://github.com/lancetalfred/bmbooks-workspace/milestone/2), 6 issues)*

---

## 🟢 Post-Activation

*(Migrated to GitHub Issues — see milestone ["Post-Activation"](https://github.com/lancetalfred/bmbooks-workspace/milestone/3), 9 issues)*

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
| **Shift to PR-based workflow** | Lance | ⏳ Planned | Move from direct commits to working through pull requests for future changes. Reason: mirrors real company engineering practice, good portfolio/learning value. Decided 2026-06-30 during ECC research. Once started, ECC's `/code-review` PR mode (fetches via `gh`, posts inline comments, can approve/request-changes) becomes relevant — currently skipped since no PR workflow existed. |
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

**Portfolio framing (decided 2026-07-01):** Position as a **PM who builds** — not a developer who manages, not a PM who delegates. The BMBooks story proves both sides: stakeholder management with Louisa (non-technical business owner), architecture and technical decisions, and hands-on shipping of real production code. Audience is talent recruiters; target roles are PM positions where technical credibility matters. Wait for post-go-live to write the case study — real numbers (products live, sync reliability, before/after) make the story dramatically stronger than pre-go-live screenshots.

| Task | Status | Notes |
| --- | --- | --- |
| Convert CVs to PDF | ⏳ Pending | Both markdown files ready |
| Write cover letters | ⏳ Pending | Need specific role + company |
| Get Louisa's permission to use BMBooks as case study | ⏳ Post go-live | Ask once migration confirmed stable. Without this, can only show the GitHub repo (scrubbed), not the live store or business context. |
| Write BMBooks case study | ⏳ Post go-live | Wait until ~1 month of Shopify data. Story: problem (WooCommerce failing, manual workflows), solution (BookScan→Shopify sync, category audit, CI pipeline), impact (real numbers — products, uptime, orders). Format: short visual deck for recruiters, not a wall of text. |
| Publish LinkedIn post | ⏳ Post go-live | Migration journey — real problems, real numbers. Hook: "I'm a PM who built a production e-commerce sync system for an indie bookstore using AI as a coding partner." |
| Workspace audit + next project setup | ⏳ Post go-live | Full audit of bmbooks-workspace structure, memory files, Claude skills, and tools used. |
| Upload BMBooks project to personal GitHub (portfolio) | ⏳ Post go-live | Already done (private). Decision: make public once Louisa approves. Scrubbing is complete (tokens in .env, PII excluded). |
| Define service offering | ⏳ Future | "E-commerce consultant for independent retailers" |
| Build simple landing page | ⏳ Future | Who you help, what you do, case study link. Keep it minimal until post-go-live story is ready. |
