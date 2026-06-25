# BMBooks Genre Enrichment — Solution Plan
**Created:** June 5, 2026  
**Updated:** June 7, 2026 — Architecture changed after discovering BICMAIN data in existing DBF files  
**Status:** Version B selected. Primary source updated from Google Books API → BICMAIN in PUBLISHER.DBF. Awaiting 3-way comparison test run before building enrichment script.  
**Running convention:** Scripts are run by Lance in terminal. Claude provides commands; does not run scripts unless debugging a specific error. This keeps token usage low and gives Lance direct control over what hits Shopify.

---

## The Problem

BMBooks has ~38,800 books (and non-book items) web-listed in Shopify. Genre classification comes from Bookscan's WEBLIST MAINCAT/SUBCAT fields, manually entered by staff over many years. Those tags populate the smart collections customers browse.

Three known gaps:
1. **Romance and Horror don't exist as Bookscan subcategories** — those books sit untagged in "General Fiction". Confirmed by inspecting the DBF: 202 Romance books and 30 Horror books are misclassified as General Fiction today.
2. **Category quality has drifted** — Food & Drink is under Well Being, Business is under Sciences, Biographies vs Biography naming inconsistency, and Louisa confirmed the setup hasn't been audited in years.
3. **Non-book items** (Stationery, Gifts, Games, Vouchers, Audio) have their own category structure that is separate from the bibliographic classification systems — enrichment does not apply to these, but the test should confirm this cleanly.

---

## What Changed — The Nielsen Discovery (June 7, 2026)

The original plan used Google Books API as the enrichment source. During a DBF inspection we found that **Nielsen BookData's BIC subject classification is already stored in PUBLISHER.DBF** — no separate integration required.

### What is BICMAIN?
`PUBLISHER.DBF` has a `BICMAIN` field containing the BIC (Book Industry Communication) subject code for each title. BIC is the professional bibliographic classification standard used by Nielsen and UK/AU/NZ publishers — the same source publishers submit to when registering a new title. It is more authoritative than Google Books for NZ/AU stock.

### Coverage comparison

| Source | Web-listed book coverage | Type | Cost / limits |
|---|---|---|---|
| Bookscan SUBCAT | 100% | Manual staff entry, quality varies | None |
| **BICMAIN (PUBLISHER.DBF)** | **90% (35,033 / 38,836)** | Nielsen professional classification | **Free — local DBF read** |
| Google Books API | ~59% (from 2 sample runs) | BISAC auto-mapping | Free, 10k requests/day |

### Why this matters
- No API key needed, no rate limits, no 4-night overnight crawl
- BIC has exactly the genre codes we need: Romance (`FR`/`FRD`/`FRH`), Horror (`FK`), Crime (`FF`), Thriller (`FH`), SciFi (`FL`), Fantasy (`FM`), Historical Fiction (`FV`)
- The `BICSUBJECT.DBF` file already in SABSSAVE contains the full BIC taxonomy (2,616 codes with names) — we can look up any code's human-readable description locally

### Updated architecture

```
For each web-listed book:
  1. Read Bookscan SUBCAT (existing tag)
     │
     ├─ SUBCAT is specific (Crime Fiction, NZ Fiction, etc.)
     │   → Keep as-is. BIC used only to verify, not override.
     │
     └─ SUBCAT is vague or missing (General Fiction, blank)
         │
         ├─ BICMAIN present in PUBLISHER.DBF?
         │   YES → Map BIC code → BMBooks tag, apply
         │   NO  → Fall back to Google Books API by ISBN
         │         Got result? → Map BISAC → BMBooks tag, apply
         │         No result?  → Flag for manual review
         │
Tag applied to Shopify. Preserved on all future syncs by _merge_tags().
```

Google Books fallback covers the remaining ~10% (~3,800 books). This is a targeted batch, not a full catalogue crawl — manageable in a single run rather than 4 overnight sessions.

---

## Full Category Scope

The test and enrichment covers **all** MAINCAT/SUBCAT combinations in WEBLIST. Non-book categories are included in the test to confirm BIC behaviour (expected: no BIC codes → no enrichment → correct).

| MAINCAT | SUBCATs | BIC applies? |
|---|---|---|
| Fiction | General Fiction, Classics, Crime Fiction, Science Fiction and Fantasy, Graphic Novels, Teen Fiction, Poetry, NZ Fiction, Historical Fiction, Plays | ✅ Yes — primary enrichment target |
| Biographies | Biography, New Zealand Biography, Essays | ✅ Yes |
| Children | Childrens Fiction, Childrens Picture Books, NZ Picture Books, Childrens Non Fiction, Books For Babies, Activities, Study And Education, Novelty Books | ✅ Yes |
| History And Politics | History, NZ History, Religion, Mythology, Politics, True Crime, NZ Sociology, Sociology, NZ Military | ✅ Yes |
| Well Being | Food And Beverage, Psychology, Health, New Age, Childrens Well Being, Gender, Family, Humour | ✅ Yes — Food & Beverage misclassification likely visible here |
| Sciences | Environment, General Science, Business, Philosophy, NZ Environment, Economics, NZ Sciences, Computing | ✅ Yes — Business miscategorised under Sciences likely visible |
| The Arts | Art, Craft, Music And Performing Arts, Fashion, Design, Photography, NZ Art, Architecture | ✅ Yes |
| Sport | General Sport And Fitness, Cycling, Rugby | ✅ Yes |
| Travel | Travel Guides, Travel Literature, Languages, New Zealand Travel, Maps, Atlases And Globes | ✅ Partial — Maps/Atlases may have no BIC |
| The Garden | Gardening, NZ Gardening | ✅ Yes |
| Motoring | Transport, Formula One | ✅ Partial |
| Reference | General, Dictionaries, Thesaurus | ✅ Yes |
| Te Ao Maori | Maori Studies and History, Maori Picture Books, Maori Language, Maori Art | ⚠️ Limited — NZ-specific, BIC may not cover well |
| The Manawatu | Our Authors, Books About Palmy | ⚠️ Local NZ — BIC unlikely to cover |
| Audio | Music CDs, Audio Books | ⚠️ Audio Books: possible. CDs: no. |
| Christmas | Christmas Books, Stocking Fillers, Christmas Card Packs, Christmas Cooking, Advent Calendars | ⚠️ Seasonal — enrich books, skip non-books |
| **Stationery Puzzles And Gifts** | Stationery, Games and Puzzles, Gifts, Calendars And Diaries | ❌ Not books — BIC not applicable, skip |
| **Vouchers** | Bruce McKenzie Booksellers Vouchers, NZ Booksellers Tokens | ❌ Not books — skip |
| Featured | Bestsellers, New Arrivals, Forthcoming | ℹ️ Merchandising tags — not enriched |
| Unknown | — | ℹ️ Audit separately |

---

## Level 3 Exception Analysis (June 7, 2026)

The research showed both Readings and Booktopia surface certain genres at Level 3 or as standalone collections beyond the standard 2-level hierarchy. All candidates were cross-referenced against BIC counts in the actual BMBooks catalogue.

| Candidate | BIC count in catalogue | Verdict | Rationale |
|---|---|---|---|
| **Manga** | 186 | ✅ **Exception — standalone collection** | Distinct audience and search term. BIC: `FXA`. Currently sits inside "Graphic Novels" but customers search for Manga specifically. |
| **Horror** | 133 | ✅ **Exception — standalone L2** | Already planned. Not sub-genre of Fantasy (as Booktopia does) — standalone for BMBooks. BIC: `FK`, `FKC`. |
| **Contemporary Romance** | 167 | ✅ **L3 under Romance (post-launch)** | Booktopia has 4 Romance sub-genres. Once Romance collection is established, split by BIC `FRD`. |
| **Historical Romance** | 53 | ✅ **L3 under Romance (post-launch)** | BIC `FRH`. Sufficient volume, distinct search demand. |
| **Thriller / Suspense** | 583 | ✅ **L2 split from Crime Fiction (post-enrichment)** | 583 books currently tagged "Crime Fiction" have BIC `FH` (Thriller/Suspense). Booktopia separates Crime & Mystery from Thrillers. This is an L2 split, not a sub-genre — someone looking for Reacher novels vs Rebus novels is browsing differently. Needs special handling: enrichment flags these as MISMATCH (BIC disagrees with Bookscan), then manual review before creating the collection. |
| **Science Fiction** | 334 | ✅ **L2 split from Fantasy (post-launch, 6mo)** | Currently combined as "Science Fiction and Fantasy" (334 SciFi + 564 Fantasy = 898 combined). Both exceed threshold. Separate search demand. Readings keeps them together; Booktopia separates. Split when enrichment data is clean. |
| **Fantasy** | 564 | ✅ **L2 split from SciFi (post-launch, 6mo)** | See above. |
| **Translated Fiction** | 36 | ⚠️ **Nice-to-have (post-launch)** | Readings does this as an editorial statement. Only 36 books — borderline threshold. BIC: `FYT`. |
| **Paranormal Romance** | 0 (no BIC code) | ❌ **Skip for now** | Booktopia L3, but BIC has no code for it. Would need keyword/manual tagging. Revisit post-launch. |
| **Rural Romance** | 0 (no BIC code) | ❌ **Skip for now** | AU/NZ marketing term only. No BIC equivalent. Revisit post-launch. |

### Thriller/Suspense — special handling note
The enrichment script's default logic only enriches books with vague/missing Bookscan subcats. A book already tagged "Crime Fiction" by Bookscan won't be auto-reclassified even if BIC says `FH` (Thriller). The comparison test `--compare` will surface these as MISMATCH rows. The plan for the Thriller split:
1. Comparison test reveals how many "Crime Fiction" books BIC classifies as `FH`
2. Lance reviews the list — are these genuinely thrillers, or is BIC wrong?
3. If correct: add "Thriller" as an additional tag (don't remove "Crime Fiction") so books can appear in both collections
4. Create Thriller smart collection once tagging is complete

---

## BIC → BMBooks Tag Mapping (draft)

Maps BIC codes to existing BMBooks Bookscan subcategory names (the tags that populate smart collections). New tags (Romance, Horror, Manga, Thriller) need new smart collections after enrichment runs.

### Fiction
| BIC code | BIC name | → BMBooks tag |
|---|---|---|
| FR, FRD, FRH | Romance / Adult romance / Historical romance | `Romance` ⭐ new |
| FK, FKC | Horror & ghost stories / Classic horror | `Horror` ⭐ new |
| FF, FFC, FFH | Crime & mystery / Classic / Historical mysteries | `Crime Fiction` |
| FH, FHD, FHP | Thriller / Espionage / Political thriller | `Thriller` ⭐ new (see note above) |
| FL, FLC, FLS | Science fiction / Classic / Space opera | `Science Fiction and Fantasy` |
| FM | Fantasy | `Science Fiction and Fantasy` |
| **FXA** | **Graphic novels: Manga** | **`Manga` ⭐ new** |
| FX, FXL, FXS, FXZ | Graphic novels (excl. Manga) | `Graphic Novels` |
| FV | Historical fiction | `Historical Fiction` |
| FA | Modern & contemporary fiction (post c 1945) | `General Fiction` |
| FC | Classic fiction (pre c 1945) | `Classics` |
| FT | Sagas | `General Fiction` |
| FYB | Short stories | `General Fiction` |
| FYT | Fiction in translation | `Translated Fiction` ⭐ new (post-launch) |
| FJ, FJH, FJM, FJW | Adventure (all) | `General Fiction` |
| FW | Religious & spiritual fiction | `General Fiction` |
| FQ | Myth & legend told as fiction | `General Fiction` |
| FP | Erotic fiction | `General Fiction` |

### Children's
| BIC code | BIC name | → BMBooks tag |
|---|---|---|
| YFC, YFB, YFH, YFM, YFD, YFP, YF* | Children's fiction (all subtypes) | `Childrens Fiction` |
| YN*, YB* | Children's non-fiction (all) | `Childrens Non Fiction` |
| YP*, YQ* | Children's picture books / early learning | `Childrens Picture Books` |
| YBG | Early learning / pre-school | `Books For Babies` |

### Non-Fiction
| BIC code | BIC name | → BMBooks tag |
|---|---|---|
| BM, BG, BGA, BGF, BGH | Memoir / Biography (all) | `Biography` |
| WB, WBT, WBJ, WBH | Food & drink (all) | `Food And Beverage` |
| VS, VSC, VSK, VFV | Self-help / psychology / relationships | `Psychology` |
| MJ, MJG | Health / medicine | `Health` |
| HR, HRA | Religion / spirituality | `Religion` |
| JF, JP, JPA, JPV | Social sciences / politics | `Politics` |
| JH, JHB | Sociology | `Sociology` |
| HB, HBJ, HBT | History | `History` |
| KN, KJC, KJH, KJM | Business / management | `Business` |
| PD, PG, PH, PN, PS | Science (all) | `General Science` |
| RG, RGC | Natural history / ecology | `Environment` |
| AK, AKT, AKH | Architecture | `Architecture` |
| AG, AGB | Art & design | `Art` |
| AV, AVA | Music | `Music And Performing Arts` |
| AC, ACB | Craft | `Craft` |
| AJ, AJC | Photography | `Photography` |
| WK, WKD | Sport | `General Sport And Fitness` |
| WT, WTL | Travel guides | `Travel Guides` |
| WTR | Travel writing | `Travel Literature` |
| WG, WGF | Gardening | `Gardening` |
| WQN | Motoring | `Transport` |
| CB, CBX | Languages / dictionaries | `Languages` |
| GTC, GTM | Maps / atlases | `Maps` |

*This mapping will be refined based on what the 3-way comparison test reveals. Codes not in this table default to no enrichment.*

---

## Test Plan — 3-Way Comparison (run before building enrichment script)

**Goal:** Validate that BICMAIN gives correct results across ALL categories — not just fiction. Confirm BIC correctly ignores non-book items. Catch any BIC mapping errors before they touch 38,000 products.

**Run by Lance in terminal.** Script outputs a CSV; Lance reviews it.

### What the test script does

For a stratified sample (10 books per subcategory, ~950 total across all 95 subcategories):
1. Reads Bookscan MAINCAT + SUBCAT from WEBLIST
2. Looks up BICMAIN in PUBLISHER.DBF
3. Looks up BIC name in BICSUBJECT.DBF
4. Looks up Google Books BISAC category (API call — limited sample only)
5. Outputs one row per book:

```
ISBN | Title | Bookscan_MAINCAT | Bookscan_SUBCAT | BIC_code | BIC_name | Google_BISAC | Assessment
```

Assessment values:
- `MATCH` — BIC agrees with Bookscan subcat
- `RECLASSIFY` — BIC suggests a different (more specific) tag; Bookscan subcat is vague
- `MISMATCH` — BIC disagrees with a specific Bookscan subcat (flag for review)
- `NO_BIC` — no BIC code, Google Books used as fallback
- `NO_DATA` — neither BIC nor Google Books has data
- `SKIP` — non-book item (Stationery, Gifts, Vouchers etc.)

### Pass criteria before proceeding

| Category | Pass condition |
|---|---|
| Fiction: Romance hiding in General Fiction | ≥10 books correctly flagged RECLASSIFY → Romance |
| Fiction: Horror hiding in General Fiction | ≥5 books correctly flagged RECLASSIFY → Horror |
| Fiction: NZ Fiction sample | 0 NZ Fiction books marked RECLASSIFY (must not touch specific tags) |
| Te Ao Māori + Manawatū sample | 100% assessed as SKIP — these subcats must be explicitly protected |
| NZ Children's subcats (NZ Picture Books etc.) | 100% assessed as SKIP |
| Fiction: Crime Fiction sample | ≥70% MATCH rate |
| Non-Fiction: Well Being / Food & Beverage | BIC correctly identifies Food & Beverage books with WB* codes |
| Non-Fiction: Sciences / Business | BIC correctly identifies Business books with K* codes |
| Stationery / Gifts / Vouchers | 100% assessed as SKIP — no BIC codes applied |
| Te Ao Maori | Script handles no-BIC gracefully, no incorrect tags applied |

### Running the test

The test script does not yet exist. Once the plan is approved, the steps are:

**Step 1** — Lance confirms plan is correct  
**Step 2** — Claude writes `Sync/genre_enrichment_v2.py` (new script, keeps old one intact)  
**Step 3** — Lance runs comparison test in terminal:
```bash
cd /Users/lancealfred/Projects/bmbooks-workspace/Sync
python3 genre_enrichment_v2.py --compare --sample 10
# Outputs: Reports/genre_comparison_test.csv
```
**Step 4** — Lance reviews CSV. Flag any unexpected RECLASSIFY or MISMATCH rows.  
**Step 5** — If any BIC mapping errors found: update mapping table in script, re-run test.  
**Step 6** — Once all pass criteria met: run full audit.

---

## Full Audit (after test passes)

```bash
# Full catalogue — reads all DBF files locally, no API calls for the 90% with BIC
python3 genre_enrichment_v2.py --audit
# Outputs: Reports/genre_audit_changes.csv  (books to reclassify)
#          Reports/genre_audit_full.csv      (all books with full comparison)
#          Reports/genre_audit_no_data.csv   (books with no BIC and no Google data)
```

For the ~10% without BIC, the script makes Google Books API calls in a separate pass:
```bash
python3 genre_enrichment_v2.py --audit-fallback --api-key YOUR_KEY
# Appends Google Books results to genre_audit_changes.csv
```

Review the changes CSV, then apply:
```bash
# Dry-run first — prints exactly what would change
python3 genre_enrichment_v2.py --apply --dry-run

# Apply for real
python3 genre_enrichment_v2.py --apply
```

---

## Tag Preservation

`bookscan_sync.py` already implements `_merge_tags()` — tags applied by this enrichment script are preserved on all future sync runs. The sync tracks which tags it set (under `bookscan_tags` in `sync_state.json`) and only replaces those, leaving external enrichment tags untouched.

This means: once a book is correctly tagged `Romance` by this script, it stays `Romance` even when the sync updates its price, stock, or description.

---

## Benefits

### SEO
- **More indexable collection pages**: Each new collection (Romance, Horror, Manga, Thriller) creates a dedicated URL that can rank for specific genre searches — "romance books NZ", "horror novels online NZ", "manga Palmerston North". Currently these searches have nowhere to land on the BMBooks site.
- **Collection page authority builds over time**: Google rewards category pages that have consistent, well-classified products. A Romance collection with 220 correctly-tagged books will outrank a General Fiction page stuffed with misclassified content.
- **Reduced thin content risk**: Post-enrichment, collections like General Fiction shrink to genuinely general books. Every collection becomes more focused and signals more topical authority.
- **Internal linking multiplier**: A book appearing in 2–3 collections gets 2–3× the internal link equity. A Romance novel currently in only "General Fiction" gets one link signal; after enrichment it's in "Romance" + "General Fiction" — stronger crawl signal and ranking support.
- **Breadcrumb schema becomes meaningful**: The `BreadcrumbList` schema already on product pages (Books › Romance › Book Title) becomes accurate and crawlable once the Romance collection exists and books are correctly tagged. Google has confirmed breadcrumb markup improves CTR in search results.
- **`bookGenre` in Book schema**: The `Book` JSON-LD already in `theme.liquid` supports a `bookGenre` property that is currently unpopulated. Once tags are enriched, this field can be populated from the product's genre tag — adding genre as structured data that Google can read directly without interpreting page content.
- **Collection descriptions become investable**: Writing the 50–150 word editorial descriptions recommended by Google's March 2026 update is only worth doing once collections have the right products in them. Enrichment is the prerequisite for that content investment to pay off.

### AI Optimisation (AEO)
AI assistants (ChatGPT, Perplexity, Google AI Overview, Gemini) increasingly answer queries like "where can I buy romance novels in Palmerston North?" or "best horror bookshop NZ". For BMBooks to appear in those answers:
- **Structured data quality**: AI crawlers ingest JSON-LD directly. A `Book` schema with `bookGenre: "Romance"` explicitly tells an AI assistant "this bookshop sells Romance books" — no page-reading inference required.
- **Collection page signals**: A dedicated, well-populated "Horror" collection page with editorial content is something AI systems can cite as evidence ("BMBooks has a dedicated Horror section with 133 titles"). A book buried in a 2,500-product "General Fiction" page provides no such signal.
- **Navigation structure as context**: AI crawlers use breadcrumbs and nav structure to understand hierarchy. "Fiction → Romance → Contemporary Romance" as a navigable path tells an AI the store is seriously organised around genre, not just a generic catalogue.
- **`llms.txt` synergy**: BMBooks already has `llms.txt` in place. That file is a signal to AI crawlers to index the site. The richer and more structured the underlying content, the more useful those citations become when an AI assistant recommends BMBooks.
- **Entity authority**: Correctly classified books with schema markup help AI systems understand BMBooks as an entity that *specialises* in certain genres — more likely to be cited in genre-specific AI answers ("independent bookshop specialising in NZ fiction, romance, and crime").

### Customer Experience
- **Findability**: A customer who wants a romance novel today cannot browse to one — 220 Romance books are hidden inside a 2,500-book "General Fiction" page. After enrichment, they tap "Romance" and see exactly what they came for.
- **Manga audience retention**: 186 Manga titles with no dedicated section means Manga customers leave for Whitcoulls or Amazon. A Manga section keeps that audience on the site.
- **Recommendation quality**: Shopify's "You may also like" algorithm uses collection membership as a signal. A Romance book currently in only "General Fiction" gets recommendations from all general fiction — after enrichment, it recommends other Romance books, which is what a romance reader wants.
- **Mobile browsing**: On mobile, tapping a genre collection is far more natural than typing a search. Correct collections make genre browsing viable on small screens in a way that a bloated General Fiction page does not.
- **Trust and credibility**: Well-labelled, correctly classified shelves signal expertise. Online, that's correct genre collections. A customer who can't find Horror books doesn't conclude "they don't stock horror" — they conclude "this site is hard to use" and leave.
- **NZ-specific sections stay authoritative**: Te Ao Māori, The Manawatū, NZ Fiction, NZ Biography — enrichment must protect these. They are BMBooks's primary competitive differentiator against Booktopia and Amazon. No overseas competitor can credibly curate a Manawatū section.

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Te Ao Māori / Manawatū books get incorrect BIC tags** | Medium | High — these are BMBooks's key differentiators | Enrichment script must never overwrite books already in NZ-specific subcats (NZ Fiction, NZ History, Maori Studies, Our Authors, Books About Palmy). Add explicit SKIP rule for all NZ-prefixed and Manawatū subcategories. |
| **Children's NZ subcategories overwritten** | Medium | Medium | "New Zealand Picture Books" and related NZ Children's subcats must be in the SKIP list alongside Te Ao Māori. BIC has no NZ-specific children's codes. |
| **Sync wipes enrichment tags before test is confirmed** | Low | High | `_merge_tags()` in `bookscan_sync.py` already protects external tags. But confirm by running tag preservation test (Test 6 in original test plan) BEFORE applying enrichment tags to production. |
| **BIC L1-only codes (e.g. `F` = Fiction, `B` = Biography) are too vague to map** | Medium | Low | Script should treat L1-only BIC codes the same as missing BIC — fall back to Google Books. Don't attempt to map `F` → `General Fiction` as it provides no enrichment value over what Bookscan already has. |
| **Dual-tagged books in Crime Fiction + Thriller cause nav confusion** | Low | Medium | Both collections will show the book — this is correct behaviour (a political thriller belongs in both). Document this as intentional in collection descriptions. Only becomes a problem if collections are poorly named; get Louisa's input on naming at Sunday meeting. |
| **BIC code is stale for older titles** | Medium | Low | Nielsen updates BIC periodically — older books in the DBF may have outdated or missing codes. This is handled by the Google Books fallback. Stale codes that produce MISMATCH results are flagged for review, not auto-applied. |
| **Google Books fallback misclassifies NZ/AU titles** | Medium | Medium | The 10% fallback applies to books without BIC — typically older or more obscure NZ/AU titles. Treat Google Books fallback results as SUGGESTED, not auto-applied. Lance reviews these before `--apply`. |
| **Shopify tag limit (250 tags per product)** | Very low | Low | Each enrichment adds 1 tag. Current products have 2–5 tags. No risk of hitting the 250 limit. |
| **`--apply` runs against wrong environment** | Low | High | Script must confirm store URL before any write operation. Add explicit confirmation prompt: "About to write to [store URL]. Proceed? (yes/no)". |

---

## Missed Opportunity — Shopify Product Taxonomy

Shopify's Standard Product Taxonomy (introduced 2023) allows assigning a standardised category (e.g. "Books & Magazines > Books > Fiction > Romance") to each product. This:
- Unlocks standard metafields for that category type
- Improves Google Shopping product data (cleaner category signals in product feed)
- Makes product data exportable to Google Merchant Centre with fewer manual mappings

BIC codes map cleanly to Shopify taxonomy categories. When `genre_enrichment_v2.py` applies a genre tag, it could simultaneously set the Shopify taxonomy category via the same GraphQL `productUpdate` mutation — zero extra API calls.

This is deferred to post-launch but should be added to the enrichment script as a `--taxonomy` flag for a future run.

---

## Why We're Not Updating Bookscan (Yet) — And the Long-Term Path

### Why not now

The cleaner long-term architecture would be to write the enriched genre classifications back into Bookscan's `WEBLIST.DBF` — so Bookscan becomes the single correct source of truth, and the normal sync pipeline carries the right tags automatically. That's actually Version A thinking applied retroactively.

There are three blockers to doing this today:

1. **Romance, Horror, Manga, Thriller don't exist as Bookscan SUBCAT entries.** `WEBSUBCAT.DBF` has no entries for these genres. Before we could write them back, someone would need to create new SUBCAT entries in Bookscan admin and get the numeric IDs. This is a Bookscan admin task requiring Louisa's involvement.

2. **DBF write safety is unconfirmed.** Bookscan is a live POS system running in the shop every day. Writing to its DBF files from an external script while Bookscan has those files open risks file corruption. The action item "Investigate DBF write safety" (Phase 2) covers this — file locking behaviour needs to be tested before any external writes go near the live system.

3. **Barcode Solutions hasn't been consulted.** Bookscan is a vendor product. External writes to its database files may void support, or there may be a supported way to do this (ONIX file drop, import function) that's safer than direct DBF writes. This needs a vendor conversation before proceeding.

### The long-term path — question for Louisa (Sunday June 8)

> *"We're going to enrich the website with correct genre tags using the Nielsen BIC data that's already in Bookscan. Longer term, would it make sense to also update the Bookscan category fields to match — so that Bookscan and the website always agree? This would mean adding new category entries for Romance, Horror, Manga, and Thriller in Bookscan, and updating the affected books. It's not urgent — we can do the website enrichment first and revisit Bookscan later — but I want to flag it as something worth doing eventually."*

If Louisa is open to it, the eventual architecture is:

```
Enrichment script identifies correct genre (BIC → BMBooks tag)
           ↓
Write back to Bookscan WEBSUBCAT + WEBLIST (once DBF write safety confirmed)
           ↓
Normal sync reads SUBCAT → creates correct Shopify tag automatically
           ↓
External enrichment script no longer needed for new books
```

This closes the loop cleanly: Bookscan becomes fully accurate, the sync pipeline is the only thing that ever writes tags, and `_merge_tags()` tag preservation becomes less critical (because the sync itself sets the right tag every cycle).

**Add to Phase 2 action items:** Once DBF write safety is confirmed and new SUBCATs are created in Bookscan, run a one-time back-population of enriched categories into `WEBLIST.DBF`.

---

## What This Does NOT Do

- Does not modify Bookscan itself — all changes are Shopify-side tags only (see above for why, and the path to changing this)
- Does not override a specific Bookscan subcat with a BIC suggestion (only vague/missing subcats are enriched)
- Does not touch non-book items (Stationery, Gifts, Vouchers, Games)
- Does not retroactively change historically correct tags (NZ Fiction, Crime Fiction etc. stay as-is)

---

## Open Questions (resolve at Sunday June 8 Louisa meeting)

- **Naming**: Smart collections for Romance and Horror — what should they be called on the website?
- **Food & Beverage location**: Move it out of Well Being MAINCAT into its own section, or keep under Well Being? (BIC enrichment identifies the books regardless)
- **Business under Sciences**: Same question — separate or keep nested?
- **Duplicate collections**: History & Politics / Non-Fiction / Politics; Biographies / Biography; Gifts / Gifts & Stationery / Stationery — which names to keep?

---

## Tasks

All tasks from this plan are tracked in `Project/BMBooks_Action_Items.md` — that is the single source of truth for what needs doing and in what order. Look for rows prefixed **Genre enrichment 1–5** in the Post-Go-Live section, plus the downstream collection and schema tasks.

*All post-go-live. Go-live is not blocked by this work.*

---

## Files

| File | Purpose |
|---|---|
| `Sync/genre_enrichment_v2.py` | New script — BIC-first, Google Books fallback |
| `Sync/genre_enrichment.py` | Old script — kept intact for reference |
| `Sync/SABSSAVE/PUBLISHER.DBF` | Source of BICMAIN field |
| `Sync/SABSSAVE/BICSUBJECT.DBF` | BIC code → name lookup (2,616 codes) |
| `Sync/SABSSAVE/WEBLIST.DBF` | Web-listed books + their MAINCAT/SUBCAT |
| `Sync/SABSSAVE/MASTER.DBF` | Book titles |
| `Reports/genre_comparison_test.csv` | Output of --compare test run |
| `Reports/genre_audit_changes.csv` | Output of --audit: books to reclassify |
| `Reports/genre_audit_full.csv` | Output of --audit: full catalogue comparison |

---

*See also: `Project/BMBooks_Category_Research.md` for the category management research that informed the original plan.*
