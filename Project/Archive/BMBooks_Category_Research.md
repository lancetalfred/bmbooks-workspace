# BMBooks — Category Management Research
**Completed:** June 5, 2026  
**Purpose:** Reference document for category structure decisions pre- and post-go-live.  
**Context:** BMBooks has ~34,500 products and 75 smart collections at time of research. Two-level hierarchy (e.g. Fiction → Classics, Crime & Thriller). Known gaps: Romance and Horror missing, Food & Drink misplaced under Well Being.

---

## Section 1: Google's Recommendations

### Category Hierarchy
- Google does not prescribe a maximum depth — it frames it as a **linking completeness problem**: every product must be reachable via navigation or sitemap.
- Industry consensus (grounded in Google guidelines + Baymard research): **5–8 top-level nav items, 2–3 hierarchy levels, minimum 10 products per deepest-level collection page.**
- Sub-divide a category when it exceeds ~10 sub-types.
- Google's March 2026 update penalised **thin category pages** (product grid with no editorial text). Minimum 50–300 words of unique descriptive content per collection page is now the competitive benchmark.

### Faceted Navigation & Crawl Budget
- Google explicitly recommends blocking faceted filter URLs from crawling — they consume crawl budget with no SEO benefit.
- Shopify's Search & Discovery app generates filter URLs in the format `?filter.p.*` and `?filter.v.*`. These must be blocked in `robots.txt` with `Disallow: /*?filter*`.
- Tag-based filter URLs (`/collections/fiction/romance`) also exist in Shopify and should be blocked or canonicalled.
- 35–60% of crawl budget on large stores is consumed by faceted URLs with no SEO value (Screaming Frog analysis).

### Category Page SEO
- **Thin content risk**: Collection pages with only a product grid give Google nothing to evaluate. Recommended structure:
  - 50-word editorial intro above the product grid
  - Product grid (24–48 products per page)
  - 100–500 words below the fold (FAQ, staff pick note, "what to read if you liked X")
- **Pagination**: Each paginated page (`?page=2`) should have a self-referencing canonical (NOT pointing back to page 1). rel=prev/next is deprecated.
- **Canonical tags**: Shopify generates `/collections/[collection]/products/[product]` duplicate URLs — modern themes (Dawn derivatives) canonical these back to `/products/[product]` correctly.

### Breadcrumbs & Schema
- `BreadcrumbList` schema on collection AND product pages causes the breadcrumb trail to appear in Google search snippets (e.g. "Books › Fiction › Crime") instead of raw URLs.
- Confirmed CTR improvement: one case study showed CTR drop from 6.6% to 4.1% when breadcrumb schema was lost.
- Google explicitly uses breadcrumb markup "to categorize information from the page in search results."
- Google supports multiple `BreadcrumbList` structures per page (a book in both Horror and Fantasy can carry both breadcrumb paths).
- **BMBooks gap**: BreadcrumbList schema implemented on product pages (2026-06-05) but NOT yet on collection pages.

### Large Catalogue Specifics (10k+ SKUs)
- Submit a well-maintained XML sitemap with `lastmod` values — essential for Googlebot to find products it can't reach via navigation alone.
- Return 404/410 for out-of-print books promptly — soft-404s (page returns HTTP 200 but shows "out of stock") waste crawl budget.
- Internal link equity flows from collection membership — a product in 3 collections gets 3× the internal link signals.

---

## Section 2: Shopify's Recommendations

### Collections vs Tags vs Metafields
| Tool | Purpose | Customer-visible? | SEO-facing? |
|---|---|---|---|
| **Collections** | Browsable category pages with their own URL | Yes — `/collections/[slug]` | Yes — indexable, can rank |
| **Tags** | Product-level labels for smart collection rules and on-site filtering | Partially via `/collections/[name]/[tag]` URLs (should be blocked) | No |
| **Metafields** | Structured attributes (ISBN, publisher, Bookscan genre, binding) | Theme-dependent | No — used in smart collection conditions |

- **Shopify Standard Product Taxonomy** (2023–24): assigning the correct taxonomy category (e.g. "Books & Magazines > Books > Fiction > Thrillers") unlocks standard metafields and makes product data exportable to Google Shopping with fewer manual steps.

### Smart vs Manual Collections
- **Smart collections** for all genre-based categories — the only maintainable approach at 34,500 products. Rules like `tag contains "genre:romance"` auto-populate as new books are added.
- **Manual collections** for: curated gift guides, staff picks, seasonal promotions, editorial themes where curation IS the value.
- **Critical pitfall**: Collection type cannot be changed after creation. Plan the tagging taxonomy before creating smart collections.

### Navigation Depth
- Shopify recommends 5–7 top-level nav items (BMBooks at 7 is at the upper edge).
- Mega menus: no more than 30 links total before cognitive load benefit is lost.
- "91% of ecommerce sites make the overcategorisation mistake" — if a product can belong to more than one subcategory, those should be filters instead of separate permanent collections.

### Shopify-Specific Pitfalls
1. **`/collections/all`** — auto-generated, lists all 34,500 products. Low-value page, should be noindexed or redirected.
2. **Collection handle permanence** — changing a collection URL slug without a 301 redirect destroys accumulated ranking. Plan handles carefully before launch.
3. **Filter URL SEO** — Search & Discovery app filter URLs are not automatically blocked. Add `Disallow: /*?filter*` and `Disallow: /*?sort*` to `robots.txt`.
4. **Tag-based collection/tag URLs** — `/collections/[name]/[tag]` auto-generated by Shopify, low quality, should be blocked or canonicalled.
5. **5,000 product limit on filter panels** — the Search & Discovery app limits the filter panel for collections exceeding 5,000 products. Top-level "All Fiction" type collections could hit this.

---

## Section 3: Competitor Category Analysis

### Booktopia (booktopia.com.au) — Australia's Largest Online Bookstore
- **Top-level nav**: 10 items (ALL, BOOKS, TEXTBOOKS, EBOOKS, AUDIOBOOKS, GAMES & PUZZLES, STATIONERY, GIFTS, CLEARANCE, BLOG)
- **Hierarchy depth**: 3 levels (Top-nav → Fiction/Non-Fiction → Sub-genre)
- **Fiction sub-genres at Level 2**: Modern & Contemporary, Australian Fiction, Crime & Mystery, Thrillers & Suspense, **Romance** (standalone with 4 Level-3 sub-genres: Contemporary, Rural, Historical, Paranormal), Erotic Fiction, Fantasy, Graphic Novels & Manga, Historical Fiction, Poetry, Science Fiction, Young Adult, Classic Fiction
- **Horror treatment**: NOT standalone — classified as Fantasy Fiction → Horror & Ghost Stories (Level 3 under Fantasy). URL: `/books-online/fiction-books/fantasy-fiction/horror-ghost-stories/`
- **Romance treatment**: Standalone Level 2 with 4 sub-genres — reflects Romance's commercial dominance in AU/NZ
- **URL structure**: Uses internal category codes (`BKM-FIC`) — legacy CMS. BMBooks on Shopify can have cleaner descriptive slugs.
- **Filters**: Price range (7 tiers), Format (Paperback, Hardcover, Large Print etc.), Language

### Readings (readings.com.au) — Independent Melbourne Bookshop (Closest Analogue to BMBooks)
- **Top-level nav**: 5 items (Books, Kids, Music, Bargains, Gift Cards) — tighter than BMBooks's 7
- **Fiction sub-categories (Level 2)**: New fiction, New Australian fiction, Classics, Crime, Fantasy & Sci-fi, Graphic Novels & Manga, Poetry, **Romance** (standalone), Translated fiction
- **Non-fiction sub-categories (Level 2)**: New nonfiction, Art & design, Biography & memoir, Cooking food & drink, Gardening & nature, History, Personal development, Politics philosophy & economics, Society & culture
- **Horror treatment**: NOT a standalone permanent category — appears as a curated collection ("Horror reads"), reflecting editorial positioning over taxonomy
- **Romantasy treatment**: Editorial curated collection, not a permanent category
- **Translated fiction**: Standalone Level 2 — reflects editorial identity (champions international literature). Analogous to BMBooks's Manawatū section.
- **Key differentiator**: "Popular Authors" as a navigation section — surfaces editorial personality
- **URL structure**: Mix of `/collections/[slug]` and flat `[slug]` — inconsistent, suggests organic growth

### Fishpond NZ (fishpond.co.nz)
- General marketplace — Books is one of 20 top-level categories. Not a useful model for BMBooks.
- Genre filtering is all faceted/on-page, no navigable category hierarchy for books.
- Competes on price/breadth, not curation. Opposite model to BMBooks.

---

## Section 4: Recommendations for BMBooks

### Is 75 Collections Right?
**Yes — in number, but composition needs adjustment.** Readings has ~25–30 genre collections plus ~15–20 curated collections. BMBooks at 75 average ~460 products/collection (healthy). The problem is composition:
- **Over-represented**: General Fiction is a catch-all bloated with misclassified Romance and Horror books
- **Under-represented**: Romance and Horror — the two largest missing genres commercially
- **Misplaced**: Food & Drink under Well Being

**Audit rule**: Any collection with <10 products → merge, hide, or convert to manual curated. Any collection with >2,000 products → review for sub-genre splitting.

### Missing Genres — Priority Order

**1. Romance — Critical, pre-launch**
- Highest volume fiction genre in EN-language markets
- Standalone at both Readings and Booktopia (with sub-genres at Booktopia)
- Strong specific search demand ("romance books NZ", "buy romance novels online")
- Action: Smart Collection on `tag:genre:romance` + bulk-tag existing inventory
- Future: Contemporary, Historical, Rural Romance as Level 3 once tag data is clean

**2. Horror — High, pre-launch**
- Growing genre, strong search demand
- Industry split: Booktopia puts Horror under Fantasy; Readings treats as curated collection
- **Recommendation for BMBooks**: Create as standalone peer genre (not under Fantasy) — search demand for "horror books" is sufficiently distinct from "fantasy books" to justify a separate indexable page
- Action: Smart Collection on `tag:genre:horror` + tag existing inventory
- Note: A book can hold multiple genre tags (e.g. both Fantasy and Horror) — no Shopify penalty for appearing in multiple collections

**3. Food & Drink restructure — High, pre-launch**
- Move out of Well Being → peer of Biography and History under Non-Fiction
- Matches both Readings ("Cooking, food & drink") and Booktopia
- "Cookbook" searches will never surface a page nested under "Well Being"

**4. Science Fiction (separate from Fantasy) — Medium, post-launch**
- Currently combined as a single collection
- Readings combines (Fantasy & Sci-fi); Booktopia separates them
- Split when stock volume and tag data supports it — both have distinct search demand

**5. Graphic Novels & Manga — Review**
- Both Readings and Booktopia surface this at Level 2 under Fiction
- If BMBooks has 50+ titles, worth creating as a standalone collection

### Navigation Depth — Stay at 2, Add Level 3 Selectively
- Maintain 2 navigable levels as the baseline (correct)
- Add Level 3 only where: (a) Level 2 genre is large enough AND (b) demonstrable search demand for the sub-genre
- Level 3 doesn't need to be in the main nav — can be accessible via sub-category page internal links or breadcrumb filter panel
- Don't add Level 3 speculatively — minimum 20 products and a specific search term target

### `/collections` Directory Page
**Recommended approach**: Build a custom `/pages/browse-genres` landing page with:
- H1: "Browse Books by Genre — BMBooks Palmerston North"
- 2–3 column grid of ~20 most important collections with cover images
- 30-word descriptions per genre block
- BreadcrumbList + ItemList schema
- Canonical the auto-generated `/collections` to this page or noindex it

### Quick Wins vs Long-Term

**Pre-launch (days):**
1. Create Romance smart collection + bulk-tag inventory
2. Create Horror smart collection + bulk-tag inventory  
3. Move Food & Drink out of Well Being
4. Block filter URLs in `robots.txt` (`Disallow: /*?filter*`, `Disallow: /*?sort*`)
5. Noindex or redirect `/collections/all`
6. Audit collections with <10 products — hide from nav

**Post-launch month 1–3:**
7. Add 50–150 word editorial descriptions to major collection pages
8. BreadcrumbList schema on all collection pages
9. Build `/pages/browse-genres` directory page + add to footer nav
10. Standardise tag taxonomy (document naming convention: `genre:[name]`, `format:[name]`)

**Post-launch 3–12 months:**
11. Romance sub-genres as Level 3 (Contemporary, Historical, Rural)
12. Science Fiction split from Fantasy
13. Product schema expansion (ISBN, author, publisher — already partially done 2026-06-05)
14. Sitemap strategy with `lastmod` accuracy (track out-of-print changes)
15. Return 404/410 for out-of-print products promptly

---

## Priority Summary Table

| Action | Priority | Effort | SEO Impact |
|---|---|---|---|
| Create Romance collection | 🔴 Critical pre-launch | Low | High |
| Block filter URLs in robots.txt | 🔴 Critical pre-launch | Low | Medium |
| Noindex /collections/all | 🔴 Critical pre-launch | Low | Medium |
| Create Horror collection | 🟡 High pre-launch | Low | Medium-High |
| Move Food & Drink out of Well Being | 🟡 High pre-launch | Low | Medium |
| Audit thin collections (<10 products) | 🟡 High pre-launch | Medium | Medium |
| Editorial descriptions on collection pages | 🟡 High post-launch | Medium | High |
| BreadcrumbList schema on collection pages | 🟡 High post-launch | Medium | Medium-High |
| Browse by Genre directory page | 🟢 Medium post-launch | Medium | Medium |
| Standardise tag taxonomy | 🟢 Medium ongoing | Medium | Foundation |
| Romance sub-genres Level 3 | 🔵 Low post-launch 3mo | Low (once tagged) | Medium |
| Science Fiction standalone | 🔵 Low post-launch 6mo | Low | Low-Medium |

---

*Sources: Google Search Central (ecommerce structure, crawl budget, faceted navigation, breadcrumb schema), Shopify Help Center (collection types, filtering), Shopify Blog (product taxonomy, category SEO, navigation), Booktopia live site, Readings live site, Baymard Institute, Screaming Frog, Search Engine Land.*
