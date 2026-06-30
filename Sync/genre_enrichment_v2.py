"""
BMBooks Genre Enrichment v2
============================
Primary source: BICMAIN from PUBLISHER.DBF (Nielsen BookData, ~90% coverage)
Fallback:       Google Books API for books without BIC data (~10%)

Modes:
  --compare         Stratified 3-way comparison across all subcategories
  --audit           Full BIC pass — classify all web-listed books (local only, fast)
  --audit-fallback  Google Books pass for books flagged NO_BIC by --audit
  --apply           Apply approved tags from genre_audit_changes.csv to Shopify

Usage:
  python genre_enrichment_v2.py --compare --sample 10
  python genre_enrichment_v2.py --audit
  python genre_enrichment_v2.py --audit-fallback --api-key YOUR_KEY
  python genre_enrichment_v2.py --apply --dry-run
  python genre_enrichment_v2.py --apply

Options:
  --sample N      Books per subcategory in --compare mode (default: 10)
  --api-key KEY   Google Books API key (for --audit-fallback; or set GOOGLE_BOOKS_API_KEY)
  --dry-run       Preview changes without writing to Shopify
  --input FILE    Override input CSV for --apply (default: Reports/genre_audit_changes.csv)
"""

import argparse
import csv
import os
import random
import sys
import time
from collections import Counter, defaultdict

import requests
from dbfread import DBF

# ── Paths ──────────────────────────────────────────────────────────────────────
_BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
_REPORTS_DIR = os.path.join(_BASE_DIR, "..", "Reports")
_SABSSAVE    = os.path.join(_BASE_DIR, "SABSSAVE")

OUT_COMPARE  = os.path.join(_REPORTS_DIR, "genre_comparison_test.csv")
OUT_FULL     = os.path.join(_REPORTS_DIR, "genre_audit_full.csv")
OUT_CHANGES  = os.path.join(_REPORTS_DIR, "genre_audit_changes.csv")
OUT_NO_DATA  = os.path.join(_REPORTS_DIR, "genre_audit_no_bic.csv")

# ── Shopify ────────────────────────────────────────────────────────────────────
SHOPIFY_STORE_URL    = os.environ.get("SHOPIFY_STORE_URL", "bruce-mckenzie-booksellers.myshopify.com")
SHOPIFY_ACCESS_TOKEN = os.environ["SHOPIFY_ACCESS_TOKEN"]
SHOPIFY_API_VER      = "2024-01"

# ── Subcategories that must NEVER be enriched ──────────────────────────────────
# NZ-specific and Māori collections are BMBooks's core competitive differentiator.
SKIP_SUBCATS = {
    # NZ-specific — never overwrite with generic BIC/Google tags
    "NZ Fiction", "NZ History", "NZ Sociology", "NZ Environment", "NZ Art",
    "NZ Gardening", "New Zealand Picture Books", "New Zealand Biography",
    "NZ Military", "NZ Sciences", "New Zealand Travel",
    # Te Ao Māori — always protected
    "Maori Studies and History", "Maori Picture Books", "Maori Language", "Maori Art",
    # The Manawatū local collection — always protected
    "Our Authors", "Books About Palmy",
    # Non-book items
    "Stationery", "Games and Puzzles", "Gifts", "Calendars And Diaries",
    "Bruce McKenzie Booksellers Vouchers", "NZ Booksellers Tokens",
    "Music CDs",
    # Merchandising (not real genre categories)
    "Bestsellers", "New Arrivals", "Forthcoming",
}

# ── Vague subcategories — enrichment candidates ────────────────────────────────
VAGUE_SUBCATS = {"General Fiction", "General", "", "Unknown"}

# ── Dual-tag pairs: (bookscan_subcat, bic_tag) ────────────────────────────────
# Books with a specific Bookscan subcat AND a BIC tag that represents a SECOND
# valid genre. Assessment = ADD_SECONDARY — keeps existing tag, adds BIC tag.
DUAL_TAG_PAIRS = {
    ("Graphic Novels",              "Manga"),            # 242 Manga books in GN collection
    ("Historical Fiction",          "Romance"),          # 54 historical romance novels
    ("Historical Fiction",          "Crime Fiction"),    # 41 historical crime/mystery
    ("Historical Fiction",          "Thriller"),         # 8 historical thrillers
    ("Science Fiction and Fantasy", "Horror"),           # 42 dark fantasy / horror crossovers
    ("Crime Fiction",               "Historical Fiction"), # 10 historical crime novels
    ("Crime Fiction",               "Thriller"),          # 511 thrillers shelved as Crime Fiction
    ("Classics",                    "Romance"),          # 6 classic romance (Austen etc.)
    ("Classics",                    "Horror"),           # 57 classic horror (Lovecraft, Shelley etc.)
    ("Classics",                    "Poetry"),           # 66 classic poetry (Inferno, Odyssey etc.)
    # Art sub-disciplines
    ("Art",                         "Architecture"),     # 335 architecture books in Art collection
    ("Art",                         "Craft"),            # 180 craft books in Art collection
    ("Art",                         "Photography"),      # 156 photography books in Art collection
    ("Design",                      "Architecture"),     # 78 design/architecture crossovers
    # Non-fiction cross-collection
    ("Health",                      "Psychology"),       # 256 health/psychology crossovers
    ("History",                     "Politics"),         # 268 political history books
    ("History",                     "Biography"),        # 132 historical biographies
    ("Business",                    "Economics"),        # 67 business/economics crossovers
    ("Music And Performing Arts",   "Biography"),        # 194 music biographies
    ("General Sport And Fitness",   "Biography"),        # 96 sports biographies
    # Reference
    ("Dictionaries",                "Languages"),        # 29 dictionaries
    ("Thesaurus",                   "Languages"),        # 8 thesaurus books
    ("Christmas Cooking",           "Food And Beverage"), # 10 seasonal food books
    # Children's
    ("Childrens Well Being",        "Childrens Picture Books"), # 66 wellbeing picture books
}

# ── BIC code → BMBooks tag  (most-specific prefix first, first match wins) ────
# Rule: bic_code.startswith(prefix). Longer prefixes MUST come before shorter ones.
BIC_MAP = [
    # ── Fiction ───────────────────────────────────────────────────────────────
    ("FR",   "Romance"),                       # FRD, FRH, FR → Romance
    ("FK",   "Horror"),                        # FKC, FK → Horror
    ("FFC",  "Crime Fiction"),                 # before FF
    ("FFH",  "Crime Fiction"),                 # before FF
    ("FF",   "Crime Fiction"),
    ("FHD",  "Thriller"),                      # before FH
    ("FHP",  "Thriller"),                      # before FH
    ("FH",   "Thriller"),
    ("FXA",  "Manga"),                         # MUST come before FX
    ("FXL",  "Graphic Novels"),
    ("FXS",  "Graphic Novels"),
    ("FXZ",  "Graphic Novels"),
    ("FX",   "Graphic Novels"),
    ("FLS",  "Science Fiction and Fantasy"),   # before FL
    ("FLC",  "Science Fiction and Fantasy"),   # before FL
    ("FL",   "Science Fiction and Fantasy"),
    ("FM",   "Science Fiction and Fantasy"),   # Fantasy
    ("FV",   "Historical Fiction"),
    ("FYT",  "Translated Fiction"),            # MUST come before FY
    ("FYB",  "General Fiction"),               # Short stories, before FY
    ("FY",   "General Fiction"),
    ("FC",   "Classics"),
    ("FT",   "General Fiction"),               # Sagas
    ("FJ",   "General Fiction"),               # Adventure
    ("FW",   "General Fiction"),               # Religious fiction
    ("FQ",   "General Fiction"),               # Myth & legend
    ("FP",   "General Fiction"),               # Erotic fiction
    ("FA",   "General Fiction"),               # Modern & contemporary
    # ── Children's ────────────────────────────────────────────────────────────
    ("YBG",  "Books For Babies"),              # MUST come before YB
    ("YBC",  "Childrens Picture Books"),       # Picture books — MUST come before YB
    ("YN",   "Childrens Non Fiction"),
    ("YB",   "Childrens Non Fiction"),
    ("YP",   "Childrens Picture Books"),
    ("YQ",   "Childrens Picture Books"),
    # YA codes that encode both age group AND genre — map to both tags
    ("YFM",  "Childrens Fiction, Romance"),    # YA romance & relationships
    ("YFCB", "Childrens Fiction, Thriller"),   # YA thrillers
    ("YFD",  "Childrens Fiction, Horror"),     # YA horror & ghost stories
    ("YF",   "Childrens Fiction"),             # All other YF* subtypes
    # ── Biography / True Stories ──────────────────────────────────────────────
    ("BM",   "Biography"),                     # Memoir
    ("BGA",  "Biography"),                     # before BG
    ("BGF",  "Biography"),                     # before BG
    ("BGH",  "Biography"),                     # before BG
    ("BG",   "Biography"),
    # BJ = Diaries, letters & journals in this BIC taxonomy — not True Crime.
    # True Crime books in BMBooks are already tagged via Bookscan SUBCAT "True Crime".
    # ("BJ", "True Crime"),  ← REMOVED — BJ miscodes journals/diaries as True Crime
    # ── Non-Fiction ───────────────────────────────────────────────────────────
    ("WB",   "Food And Beverage"),             # All WB* food codes
    ("VS",   "Psychology"),                    # Self-help & popular psychology
    ("VFJ",  "Psychology"),                    # Coping with illness/personal issues (before VF)
    # VF = Family & health — too broad for Psychology.
    # VFD (medicine), VFDW (women's health), VFM (fitness/diet), VFX (parenting) are Health, not Psychology.
    ("MJ",   "Health"),
    ("HR",   "Religion"),
    ("HQ",   "Religion"),
    ("JP",   "Politics"),
    ("JK",   "Politics"),
    ("JF",   "Sociology"),
    ("JH",   "Sociology"),
    ("HBJ",  "History"),                       # before HB
    ("HBT",  "History"),
    ("HBW",  "History"),
    ("HBG",  "History"),
    ("HB",   "History"),
    ("KJC",  "Business"),                      # before KJ
    ("KJH",  "Business"),
    ("KJM",  "Business"),
    ("KJ",   "Business"),
    ("KN",   "Business"),
    ("KC",   "Economics"),
    ("KF",   "Economics"),
    ("PD",   "General Science"),
    ("PG",   "General Science"),
    ("PH",   "General Science"),
    ("PN",   "General Science"),
    ("PS",   "General Science"),
    ("PB",   "General Science"),
    ("RG",   "Environment"),
    # AK = Industrial/commercial art & design (graphic design, illustration, fashion design)
    # NOT Architecture — removed to avoid false positives on design/fashion books
    ("AM",   "Architecture"),                  # AM = Architecture only
    ("AG",   "Art"),
    ("AB",   "Art"),
    ("AV",   "Music And Performing Arts"),
    ("AP",   "Music And Performing Arts"),
    # AC = History of art & design styles (Impressionism, Surrealism etc.) — NOT craft instruction
    # Craft instruction is WF* branch — already handled above. AC removed to avoid false positives.
    ("AJ",   "Photography"),
    ("WFBQ", "Craft"),                         # Quilting & patchwork — before WFB
    ("WFBS", "Craft"),                         # Sewing — before WFB
    ("WFBN", "Craft"),                         # Knitting & crochet — before WFB
    ("WFBR", "Craft"),                         # Rugmaking — before WFB
    ("WFB",  "Craft"),                         # All craft forms (before WF)
    ("WFL",  "Craft"),                         # Textiles & fabrics (before WF)
    ("WFT",  "Craft"),                         # Flower arranging & floral art (before WF)
    ("WFW",  "Craft"),                         # Flower arranging displays (before WF)
    ("WFN",  "Craft"),                         # Craft: textiles & fashion (before WF)
    ("WFJ",  "Craft"),                         # Jewellery making (before WF)
    ("WFK",  "Craft"),                         # Beadwork (before WF)
    ("WF",   "Fashion"),                       # Fashion & beauty (genuine fashion codes)
    ("WK",   "General Sport And Fitness"),
    ("WTR",  "Travel Literature"),             # MUST come before WT
    ("WT",   "Travel Guides"),
    ("WG",   "Gardening"),
    ("WQY",  "Biography"),                     # Family history & genealogy — before WQ
    ("WQ",   "Transport"),
    ("WH",   "Humour"),
    ("CB",   "Languages"),
    ("GTC",  "Languages"),                     # Communication studies — before GT (not Maps)
    ("GT",   "Maps"),
    ("DC",   "Poetry"),
    ("DQ",   "General Fiction"),               # Anthologies
    ("DS",   "Classics"),                      # Literature & criticism
]

# ── Google Books category → BMBooks tag (fallback only) ───────────────────────
GOOGLE_MAP = [
    ("Fiction / Romance",                "Romance"),
    ("Fiction / Horror",                 "Horror"),
    ("Fiction / Ghost",                  "Horror"),
    ("Fiction / Science Fiction",        "Science Fiction and Fantasy"),
    ("Fiction / Fantasy",                "Science Fiction and Fantasy"),
    ("Fiction / Mystery & Detective",    "Crime Fiction"),
    ("Fiction / Thrillers & Suspense",   "Thriller"),
    ("Fiction / Crime",                  "Crime Fiction"),
    ("Fiction / Historical",             "Historical Fiction"),
    ("Fiction / Classic",                "Classics"),
    ("Fiction / Classics",               "Classics"),
    ("Comics & Graphic Novels / Manga",  "Manga"),
    ("Fiction / Graphic Novels",         "Graphic Novels"),
    ("Comics & Graphic Novels",          "Graphic Novels"),
    ("Fiction / Humorous",               "Humour"),
    ("Fiction / Literary",               "General Fiction"),
    ("Fiction / General",                "General Fiction"),
    ("Young Adult Fiction",              "Teen Fiction"),
    ("Young Adult Nonfiction",           "Teen Fiction"),
    ("Juvenile Fiction",                 "Childrens Fiction"),
    ("Juvenile Nonfiction",              "Childrens Non Fiction"),
    ("Juvenile Biography",               "Childrens Non Fiction"),
    ("True Crime",                       "True Crime"),
    ("Biography & Autobiography",        "Biography"),
    ("Cooking",                          "Food And Beverage"),
    ("Food Science",                     "Food And Beverage"),
    ("Self-Help",                        "Psychology"),
    ("Health & Fitness",                 "Health"),
    ("Psychology",                       "Psychology"),
    ("Body, Mind & Spirit",              "New Age"),
    ("History",                          "History"),
    ("Political Science",                "Politics"),
    ("Business & Economics / Economics", "Economics"),
    ("Business & Economics",             "Business"),
    ("Drama",                            "Plays"),
    ("Poetry",                           "Poetry"),
    ("Music",                            "Music And Performing Arts"),
    ("Performing Arts",                  "Music And Performing Arts"),
    ("/ Art",                            "Art"),
    ("Art /",                            "Art"),
    ("Art History",                      "Art"),
    ("Fine Art",                         "Art"),
    ("Photography",                      "Photography"),
    ("Architecture",                     "Architecture"),
    ("Science",                          "General Science"),
    ("Nature",                           "Environment"),
    ("Travel",                           "Travel Guides"),
    ("Sports & Recreation / Rugby",      "Rugby"),
    ("Sports & Recreation / Cycling",    "Cycling"),
    ("Sports & Recreation",              "General Sport And Fitness"),
    ("Crafts & Hobbies",                 "Craft"),
    ("Gardening",                        "Gardening"),
    ("Religion",                         "Religion"),
    ("Philosophy",                       "Philosophy"),
    ("Language Arts & Disciplines",      "Languages"),
    ("Family & Relationships",           "Family"),
    ("Mythology",                        "Mythology"),
    ("Humor",                            "Humour"),
]


# ── Helpers ────────────────────────────────────────────────────────────────────

def load_catalogue():
    """Load WEBLIST + PUBLISHER + MASTER + lookups into a list of book dicts."""
    print("Loading DBF files...", end=" ", flush=True)

    maincat_map = {r["MAINCAT"]: str(r["CATNAME"]).strip()
                   for r in DBF(os.path.join(_SABSSAVE, "WEBMAINCAT.DBF"),
                                ignore_missing_memofile=True)}
    subcat_map  = {r["SUBCAT"]: str(r["CATNAME"]).strip()
                   for r in DBF(os.path.join(_SABSSAVE, "WEBSUBCAT.DBF"),
                                ignore_missing_memofile=True)}
    bic_names   = {str(r["BICCODE"]).strip(): str(r["BICNAME"]).strip()
                   for r in DBF(os.path.join(_SABSSAVE, "BICSUBJECT.DBF"),
                                ignore_missing_memofile=True)}
    pub_bic     = {}
    for r in DBF(os.path.join(_SABSSAVE, "PUBLISHER.DBF"), ignore_missing_memofile=True):
        isbn = str(r.get("ISBN") or "").strip()
        bic  = str(r.get("BICMAIN") or "").strip()
        if isbn:
            pub_bic[isbn] = bic
    titles = {}
    for r in DBF(os.path.join(_SABSSAVE, "MASTER.DBF"), ignore_missing_memofile=True):
        isbn = str(r.get("ISBN") or "").strip()
        if isbn:
            titles[isbn] = str(r.get("TITLE") or "").strip()

    books = []
    for r in DBF(os.path.join(_SABSSAVE, "WEBLIST.DBF"), ignore_missing_memofile=True):
        isbn = str(r.get("ISBN") or "").strip()
        if not isbn:
            continue
        maincat  = maincat_map.get(r.get("MAINCAT"), "")
        subcat   = subcat_map.get(r.get("SUBCAT"), "")
        bic_code = pub_bic.get(isbn, "")
        books.append({
            "isbn":     isbn,
            "title":    titles.get(isbn, ""),
            "maincat":  maincat,
            "subcat":   subcat,
            "bic":      bic_code,
            "bic_name": bic_names.get(bic_code, "") if bic_code else "",
        })

    print(f"{len(books):,} books loaded.")
    return books, bic_names


def map_bic(bic_code):
    """Return BMBooks tag for a BIC code, or None if L1-only or unmapped."""
    if not bic_code or len(bic_code) <= 1:
        return None  # single-letter L1 code — too vague to map
    for prefix, tag in BIC_MAP:
        if bic_code.startswith(prefix):
            return tag
    return None


def map_google(categories):
    """Return BMBooks tag for a list of Google Books category strings."""
    if not categories:
        return None
    for cat in categories:
        for fragment, tag in GOOGLE_MAP:
            if fragment.lower() in cat.lower():
                return tag
    return None


def query_google_books(isbn, api_key=None):
    """Query Google Books. Returns (title, categories) or (None, None)."""
    params = {"q": f"isbn:{isbn}", "maxResults": 1}
    if api_key:
        params["key"] = api_key
    try:
        r = requests.get("https://www.googleapis.com/books/v1/volumes",
                         params=params, timeout=10)
        if r.status_code == 429:
            return "RATE_LIMIT", None
        r.raise_for_status()
        items = r.json().get("items", [])
        if not items:
            return None, None
        info = items[0].get("volumeInfo", {})
        return info.get("title", ""), info.get("categories", [])
    except Exception as e:
        return f"ERROR:{e}", None


def _shopify_post(payload):
    url = f"https://{SHOPIFY_STORE_URL}/admin/api/{SHOPIFY_API_VER}/graphql.json"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()
    return r.json()


def _lookup_product(isbn):
    """Return (product_gid, current_tags) for an ISBN/SKU, or (None, None)."""
    q = """
    query($q: String!) {
      productVariants(first: 1, query: $q) {
        edges { node { product { id tags } } }
      }
    }"""
    data = _shopify_post({"query": q, "variables": {"q": f'sku:"{isbn}"'}})
    edges = data.get("data", {}).get("productVariants", {}).get("edges", [])
    if not edges:
        return None, None
    product = edges[0]["node"]["product"]
    return product["id"], product["tags"]


# ── Mode: Compare ──────────────────────────────────────────────────────────────

def run_compare(args):
    n = args.sample
    print(f"\n{'='*60}")
    print("Genre Enrichment v2 — 3-Way Comparison Test")
    print(f"Sample: {n} books per subcategory")
    print(f"{'='*60}")

    books, _ = load_catalogue()

    api_key = args.api_key or os.environ.get("GOOGLE_BOOKS_API_KEY", "")
    if not api_key:
        print("No API key — Google Books column will be blank. Pass --api-key to include it.")

    by_subcat = defaultdict(list)
    for b in books:
        by_subcat[b["subcat"]].append(b)

    sample = []
    for subcat in sorted(by_subcat):
        sample.extend(random.sample(by_subcat[subcat], min(n, len(by_subcat[subcat]))))
    print(f"Sampled {len(sample):,} books across {len(by_subcat)} subcategories\n")

    fieldnames = [
        "isbn", "title", "bookscan_maincat", "bookscan_subcat",
        "bic_code", "bic_name", "bic_tag",
        "google_categories", "google_tag",
        "assessment", "proposed_tag",
    ]
    rows = []

    for i, book in enumerate(sample, 1):
        subcat   = book["subcat"]
        bic_code = book["bic"]
        bic_tag  = map_bic(bic_code)
        is_vague = subcat in VAGUE_SUBCATS

        # Determine assessment from BIC
        if subcat in SKIP_SUBCATS:
            assessment, proposed = "SKIP", ""
        elif bic_tag:
            if bic_tag == subcat:
                assessment, proposed = "MATCH", ""
            elif is_vague:
                assessment, proposed = "RECLASSIFY", bic_tag
            elif (subcat, bic_tag) in DUAL_TAG_PAIRS:
                assessment, proposed = "ADD_SECONDARY", bic_tag
            else:
                assessment, proposed = "MISMATCH", ""
        else:
            assessment, proposed = "NO_BIC", ""

        # Google Books (only for NO_BIC books when key provided)
        google_cats_str = ""
        google_tag_str  = ""
        if api_key and assessment == "NO_BIC":
            g_title, g_cats = query_google_books(book["isbn"], api_key)
            if g_title == "RATE_LIMIT":
                print("  Rate limited — pausing 60s...")
                time.sleep(60)
                g_title, g_cats = query_google_books(book["isbn"], api_key)
            if g_cats:
                google_cats_str = " | ".join(g_cats)
                g_tag = map_google(g_cats)
                if g_tag:
                    google_tag_str = g_tag
                    if g_tag == subcat:
                        assessment, proposed = "MATCH", ""
                    elif is_vague:
                        assessment, proposed = "RECLASSIFY", g_tag
                    else:
                        assessment, proposed = "MISMATCH", ""
                else:
                    assessment = "NO_DATA"
            else:
                assessment = "NO_DATA"
            time.sleep(0.1)

        rows.append({
            "isbn":             book["isbn"],
            "title":            book["title"],
            "bookscan_maincat": book["maincat"],
            "bookscan_subcat":  subcat,
            "bic_code":         bic_code,
            "bic_name":         book["bic_name"],
            "bic_tag":          bic_tag or "",
            "google_categories": google_cats_str,
            "google_tag":       google_tag_str,
            "assessment":       assessment,
            "proposed_tag":     proposed,
        })

        if i % 200 == 0:
            print(f"  {i}/{len(sample)}")

    os.makedirs(_REPORTS_DIR, exist_ok=True)
    with open(OUT_COMPARE, "w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=fieldnames).writeheader()
        csv.DictWriter(f, fieldnames=fieldnames).writerows(rows)

    counts     = Counter(r["assessment"] for r in rows)
    reclassify = [r for r in rows if r["assessment"] == "RECLASSIFY"]
    by_tag     = defaultdict(list)
    for r in reclassify:
        by_tag[r["proposed_tag"]].append(r)

    print(f"\n{'='*60}")
    print(f"Comparison complete — {len(rows):,} books sampled")
    print(f"  ✅ MATCH:       {counts['MATCH']:>4}")
    print(f"  🔄 RECLASSIFY:  {counts['RECLASSIFY']:>4}")
    print(f"  ⚠️  MISMATCH:    {counts['MISMATCH']:>4}")
    print(f"  🔍 NO_BIC:      {counts['NO_BIC']:>4}")
    print(f"  ❓ NO_DATA:     {counts['NO_DATA']:>4}")
    print(f"  ⏭️  SKIP:        {counts['SKIP']:>4}")
    if reclassify:
        print("\nProposed reclassifications:")
        for tag in sorted(by_tag):
            print(f"  {len(by_tag[tag]):>3}  → {tag}")
    print("\nOutput: Reports/genre_comparison_test.csv")
    print("\nCheck pass criteria in Project/BMBooks_Genre_Enrichment_Plan.md before proceeding.")


# ── Mode: Audit (BIC pass) ─────────────────────────────────────────────────────

def run_audit(args):
    print(f"\n{'='*60}")
    print("Genre Enrichment v2 — Full BIC Audit (local, no API calls)")
    print(f"{'='*60}")

    books, _ = load_catalogue()

    fieldnames = ["isbn", "title", "bookscan_maincat", "bookscan_subcat",
                  "bic_code", "bic_tag", "assessment", "tags_to_add"]
    rows = []

    for book in books:
        subcat  = book["subcat"]
        bic_tag = map_bic(book["bic"])
        is_vague = subcat in VAGUE_SUBCATS

        if subcat in SKIP_SUBCATS:
            assessment, proposed = "SKIP", ""
        elif bic_tag:
            if bic_tag == subcat:
                assessment, proposed = "MATCH", ""
            elif is_vague:
                assessment, proposed = "RECLASSIFY", bic_tag
            elif (subcat, bic_tag) in DUAL_TAG_PAIRS:
                assessment, proposed = "ADD_SECONDARY", bic_tag
            else:
                assessment, proposed = "MISMATCH", ""
        else:
            assessment, proposed = "NO_BIC", ""

        rows.append({
            "isbn":             book["isbn"],
            "title":            book["title"],
            "bookscan_maincat": book["maincat"],
            "bookscan_subcat":  subcat,
            "bic_code":         book["bic"],
            "bic_tag":          bic_tag or "",
            "assessment":       assessment,
            "tags_to_add":      proposed,
        })

    os.makedirs(_REPORTS_DIR, exist_ok=True)
    changes  = [r for r in rows if r["tags_to_add"]]   # RECLASSIFY + ADD_SECONDARY
    no_bic   = [r for r in rows if r["assessment"] == "NO_BIC"]
    mismatches = [r for r in rows if r["assessment"] == "MISMATCH"]

    with open(OUT_FULL, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(rows)

    with open(OUT_CHANGES, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(changes)

    with open(OUT_NO_DATA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(no_bic)

    # Mismatch report — BIC disagrees with specific Bookscan tag (review separately)
    out_mismatch = os.path.join(_REPORTS_DIR, "genre_audit_mismatches.csv")
    with open(out_mismatch, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(mismatches)

    counts  = Counter(r["assessment"] for r in rows)
    by_tag  = Counter(r["tags_to_add"] for r in changes)

    print(f"\n{'='*60}")
    print(f"Audit complete — {len(rows):,} books")
    print(f"  ✅ MATCH:       {counts['MATCH']:>6,}")
    print(f"  🔄 RECLASSIFY:  {counts['RECLASSIFY']:>6,}  ← will be tagged")
    print(f"  ⚠️  MISMATCH:    {counts['MISMATCH']:>6,}  ← BIC disagrees with specific subcat, review separately")
    print(f"  🔍 NO_BIC:      {counts['NO_BIC']:>6,}  ← run --audit-fallback for Google Books pass")
    print(f"  ⏭️  SKIP:        {counts['SKIP']:>6,}")
    if changes:
        print(f"\nProposed tag changes ({len(changes):,} books):")
        for tag, cnt in sorted(by_tag.items(), key=lambda x: -x[1]):
            print(f"  {cnt:>5,}  → {tag}")
    print("\nReports written to Reports/:")
    print(f"  genre_audit_full.csv        — all {len(rows):,} books")
    print(f"  genre_audit_changes.csv     — {len(changes):,} books to reclassify")
    print(f"  genre_audit_no_bic.csv      — {len(no_bic):,} books for Google fallback")
    print(f"  genre_audit_mismatches.csv  — {len(mismatches):,} BIC/Bookscan disagreements (review manually)")
    print("\nNext steps:")
    print("  1. Review genre_audit_changes.csv")
    print("  2. Optionally: python genre_enrichment_v2.py --audit-fallback --api-key KEY")
    print("  3. python genre_enrichment_v2.py --apply --dry-run")


# ── Mode: Audit Fallback (Google Books) ───────────────────────────────────────

def run_audit_fallback(args):
    print(f"\n{'='*60}")
    print("Genre Enrichment v2 — Google Books Fallback")
    print(f"{'='*60}")

    if not os.path.exists(OUT_NO_DATA):
        print(f"Error: {OUT_NO_DATA} not found. Run --audit first.")
        sys.exit(1)

    api_key = args.api_key or os.environ.get("GOOGLE_BOOKS_API_KEY", "")
    if not api_key:
        print("Error: --api-key required (or set GOOGLE_BOOKS_API_KEY env var)")
        sys.exit(1)

    no_bic_rows = []
    with open(OUT_NO_DATA) as f:
        for row in csv.DictReader(f):
            if row.get("assessment") == "NO_BIC":
                no_bic_rows.append(row)

    print(f"Loaded {len(no_bic_rows):,} books without BIC data")
    print(f"Estimated time: ~{len(no_bic_rows) // 600 + 1} minutes at 10 req/sec\n")

    new_changes = []
    for i, row in enumerate(no_bic_rows, 1):
        if i % 100 == 0:
            print(f"  {i}/{len(no_bic_rows)}")

        isbn    = row["isbn"]
        subcat  = row["bookscan_subcat"]
        is_vague = subcat in VAGUE_SUBCATS

        g_title, g_cats = query_google_books(isbn, api_key)
        if g_title == "RATE_LIMIT":
            print("  Rate limited — pausing 60s...")
            time.sleep(60)
            g_title, g_cats = query_google_books(isbn, api_key)

        g_tag = map_google(g_cats) if g_cats else None

        if g_tag and is_vague and g_tag != subcat:
            new_changes.append({
                "isbn":             isbn,
                "title":            row["title"],
                "bookscan_maincat": row["bookscan_maincat"],
                "bookscan_subcat":  subcat,
                "bic_code":         "",
                "bic_tag":          "",
                "assessment":       "RECLASSIFY_GOOGLE",
                "tags_to_add":      g_tag,
            })

        time.sleep(0.1)

    # Append to changes CSV
    fieldnames = ["isbn", "title", "bookscan_maincat", "bookscan_subcat",
                  "bic_code", "bic_tag", "assessment", "tags_to_add"]
    existing = []
    if os.path.exists(OUT_CHANGES):
        with open(OUT_CHANGES) as f:
            existing = list(csv.DictReader(f))

    all_changes = existing + new_changes
    with open(OUT_CHANGES, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(all_changes)

    by_tag = Counter(r["tags_to_add"] for r in new_changes)
    print(f"\nFallback complete: {len(new_changes):,} additional reclassifications")
    if new_changes:
        for tag, cnt in sorted(by_tag.items(), key=lambda x: -x[1]):
            print(f"  {cnt:>4}  → {tag}")
    print(f"\nTotal in genre_audit_changes.csv: {len(all_changes):,}")
    print("\nNext: python genre_enrichment_v2.py --apply --dry-run")


# ── Mode: Apply ───────────────────────────────────────────────────────────────

def run_apply(args):
    input_file = args.input or OUT_CHANGES

    print(f"\n{'='*60}")
    print("Genre Enrichment v2 — Apply Tags to Shopify")
    if args.dry_run:
        print("DRY RUN — no changes will be made to Shopify")
    print(f"{'='*60}\n")

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Run --audit first.")
        sys.exit(1)

    rows = [r for r in csv.DictReader(open(input_file)) if r.get("tags_to_add")]
    print(f"Loaded {len(rows):,} books to tag from {os.path.basename(input_file)}")
    print(f"Store: {SHOPIFY_STORE_URL}\n")

    if not args.dry_run:
        confirm = input(f"About to write tags to {SHOPIFY_STORE_URL}. Proceed? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Aborted.")
            sys.exit(0)

    applied = skipped = errors = 0

    for i, row in enumerate(rows, 1):
        isbn    = row["isbn"]
        new_tag = row["tags_to_add"].strip()

        if i % 100 == 0:
            print(f"  {i}/{len(rows)} — Applied: {applied}  Skipped: {skipped}  Errors: {errors}")

        product_gid, current_tags = _lookup_product(isbn)
        if not product_gid:
            skipped += 1
            continue

        # Support comma-separated tags (e.g. "Childrens Fiction, Romance")
        new_tags = [t.strip() for t in new_tag.split(",") if t.strip()]
        tags_to_apply = [t for t in new_tags if t not in current_tags]

        if not tags_to_apply:
            skipped += 1
            continue

        if args.dry_run:
            preview = ", ".join(current_tags[:3]) + ("..." if len(current_tags) > 3 else "")
            print(f"  DRY [{isbn}] +{tags_to_apply}  (current: {preview})")
            applied += 1
            time.sleep(0.05)
            continue

        mutation = """
        mutation($id: ID!, $tags: [String!]!) {
          productUpdate(input: { id: $id, tags: $tags }) {
            userErrors { field message }
          }
        }"""
        data = _shopify_post({"query": mutation,
                              "variables": {"id": product_gid,
                                            "tags": current_tags + tags_to_apply}})
        errs = data.get("data", {}).get("productUpdate", {}).get("userErrors", [])
        if errs:
            print(f"  Error [{isbn}]: {errs}")
            errors += 1
        else:
            applied += 1
        time.sleep(0.1)

    print(f"\n{'='*60}")
    if args.dry_run:
        print(f"Dry run complete — {applied:,} books would be tagged")
    else:
        print("Apply complete")
        print(f"  Applied:  {applied:,}")
        print(f"  Skipped:  {skipped:,}  (not found or already tagged)")
        print(f"  Errors:   {errors:,}")
        if applied:
            print("\nNext: verify collections in Shopify admin, then create smart collections for new tags.")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="BMBooks Genre Enrichment v2 — BIC-first")
    parser.add_argument("--compare",        action="store_true", help="3-way comparison test (stratified sample)")
    parser.add_argument("--audit",          action="store_true", help="Full BIC audit — all web-listed books")
    parser.add_argument("--audit-fallback", action="store_true", dest="audit_fallback",
                        help="Google Books pass for NO_BIC books")
    parser.add_argument("--apply",          action="store_true", help="Apply approved tags to Shopify")
    parser.add_argument("--sample",         type=int, default=10, metavar="N",
                        help="Books per subcategory in --compare (default: 10)")
    parser.add_argument("--api-key",        dest="api_key", metavar="KEY",
                        help="Google Books API key (or set GOOGLE_BOOKS_API_KEY)")
    parser.add_argument("--dry-run",        action="store_true", dest="dry_run",
                        help="Preview without writing to Shopify")
    parser.add_argument("--input",          metavar="FILE",
                        help="Override input CSV for --apply")
    args = parser.parse_args()

    if args.apply:
        run_apply(args)
    elif args.audit_fallback:
        run_audit_fallback(args)
    elif args.audit:
        run_audit(args)
    elif args.compare:
        run_compare(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
