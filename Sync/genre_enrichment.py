"""
BMBooks Genre Enrichment Tool
==============================
Queries the Google Books API by ISBN to classify books into BMBooks genre tags.

Modes:
  --audit        Query Google Books and generate comparison reports (default)
  --apply        Bulk-apply approved tags to Shopify products

Usage:
  python genre_enrichment.py --audit --sample 100
  python genre_enrichment.py --audit --api-key YOUR_KEY
  python genre_enrichment.py --apply --input Reports/genre_audit_approved.csv

Options:
  --sample N       Process only N ISBNs (default: all). Use for validation first.
  --api-key KEY    Google Books API key (10,000 req/day free). Without key: 1,000/day.
  --resume         Skip ISBNs already in the progress file. Safe to re-run.
  --input FILE     CSV file for --apply mode (must have isbn and tags_to_add columns).
  --dry-run        Show what would be applied without making Shopify changes.
"""

import argparse
import csv
import json
import os
import random
import sys
import time
import requests
from datetime import datetime

# ── Paths ──────────────────────────────────────────────────────────────────────
_BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
_REPORTS_DIR   = os.path.join(_BASE_DIR, "..", "Reports")
ISBN_CSV       = os.path.join(_REPORTS_DIR, "BMBooks_ISBNs_BookData.csv")
PROGRESS_FILE  = os.path.join(_BASE_DIR, "genre_enrichment_progress.json")
OUT_FULL       = os.path.join(_REPORTS_DIR, "genre_audit_full.csv")
OUT_CHANGES    = os.path.join(_REPORTS_DIR, "genre_audit_changes.csv")
OUT_LOUISA     = os.path.join(_REPORTS_DIR, "genre_audit_louisa.csv")

# ── Shopify credentials (from bookscan_sync.py) ────────────────────────────────
SHOPIFY_STORE_URL    = os.environ.get("SHOPIFY_STORE_URL", "bruce-mckenzie-booksellers.myshopify.com")
SHOPIFY_ACCESS_TOKEN = os.environ["SHOPIFY_ACCESS_TOKEN"]

# ── Google Books category → BMBooks tag mapping ────────────────────────────────
# Order matters — first match wins. More specific entries go first.
CATEGORY_MAP = [
    # Fiction — specific genres first
    ("Fiction / Romance",               "Romance"),
    ("Fiction / Horror",                "Horror"),
    ("Fiction / Ghost",                 "Horror"),
    ("Fiction / Science Fiction",       "Science Fiction and Fantasy"),
    ("Fiction / Fantasy",               "Science Fiction and Fantasy"),
    ("Fiction / Mystery & Detective",   "Crime Fiction"),
    ("Fiction / Thrillers & Suspense",  "Crime Fiction"),
    ("Fiction / Crime",                 "Crime Fiction"),
    ("Fiction / Historical",            "Historical Fiction"),
    ("Fiction / Classic",               "Classics"),
    ("Fiction / Classics",              "Classics"),
    ("Fiction / Graphic Novels",        "Graphic Novels"),
    ("Comics & Graphic Novels",         "Graphic Novels"),
    ("Fiction / Humorous",              "Humour"),
    ("Fiction / Action & Adventure",    "General Fiction"),
    ("Fiction / Literary",              "General Fiction"),
    ("Fiction / General",               "General Fiction"),
    # Children's / Young Adult
    ("Young Adult Fiction",             "Teen Fiction"),
    ("Young Adult Nonfiction",          "Teen Fiction"),
    ("Juvenile Fiction",                "Childrens Fiction"),
    ("Juvenile Nonfiction",             "Childrens Non Fiction"),
    ("Juvenile Biography",              "Childrens Non Fiction"),
    # Non-Fiction subjects
    ("True Crime",                      "True Crime"),
    ("Biography & Autobiography",       "Biography"),
    ("Cooking",                         "Food And Beverage"),
    ("Food Science",                    "Food And Beverage"),
    ("Self-Help",                       "Well Being"),
    ("Health & Fitness",                "Well Being"),
    ("Psychology",                      "Psychology"),
    ("Body, Mind & Spirit",             "New Age"),
    ("New Age",                         "New Age"),
    ("History",                         "History"),
    ("Political Science",               "History And Politics"),
    ("Social Science / Politics",       "History And Politics"),
    ("Business & Economics / Economics","Economics"),
    ("Business & Economics",            "Business"),
    ("Drama",                           "Plays"),
    ("Poetry",                          "Poetry"),
    ("Music",                           "Music And Performing Arts"),
    ("Performing Arts",                 "Music And Performing Arts"),
    ("/ Art",                           "Art"),
    ("Art /",                           "Art"),
    ("Art History",                     "Art"),
    ("Fine Art",                        "Art"),
    ("Visual Art",                      "Art"),
    ("Photography",                     "Photography"),
    ("Architecture",                    "Architecture"),
    ("Design",                          "Design"),
    ("Fashion",                         "Fashion"),
    ("Science",                         "Sciences"),
    ("Nature",                          "Sciences"),
    ("Travel",                          "Travel"),
    ("Sports & Recreation / Rugby",     "Rugby"),
    ("Sports & Recreation / Cycling",   "Cycling"),
    ("Sports & Recreation",             "Sport"),
    ("Games & Activities",              "Activities"),
    ("Crafts & Hobbies",                "Craft"),
    ("House & Home",                    "The Garden"),
    ("Gardening",                       "The Garden"),
    ("Religion",                        "Religion"),
    ("Philosophy",                      "Philosophy"),
    ("Social Science / Gender Studies", "Gender"),
    ("Language Arts & Disciplines",     "Languages"),
    ("Education",                       "Study And Education"),
    ("Family & Relationships",          "Family"),
    ("Mythology",                       "Mythology"),
    ("Humor",                           "Humour"),
]


def map_google_category(categories):
    """
    Given a list of Google Books category strings, return the best-matching
    BMBooks tag. Returns None if no match found.
    """
    if not categories:
        return None
    for category_str in categories:
        for fragment, bmbooks_tag in CATEGORY_MAP:
            if fragment.lower() in category_str.lower():
                return bmbooks_tag
    return None


def query_google_books(isbn, api_key=None):
    """
    Query Google Books API for an ISBN.
    Returns (title, categories_list) or (None, None) if not found.
    """
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": f"isbn:{isbn}", "maxResults": 1}
    if api_key:
        params["key"] = api_key

    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 429:
            return "RATE_LIMIT", None
        r.raise_for_status()
        data = r.json()
        items = data.get("items", [])
        if not items:
            return None, None
        info = items[0].get("volumeInfo", {})
        title = info.get("title", "")
        categories = info.get("categories", [])
        return title, categories
    except Exception as e:
        return f"ERROR:{e}", None


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {}


def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)


def run_audit(args):
    print(f"\n{'='*60}")
    print(f"BMBooks Genre Enrichment — Audit Mode")
    print(f"{'='*60}")

    # Load ISBNs
    isbns = []
    with open(ISBN_CSV) as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].strip().isdigit():
                isbns.append(row[0].strip())
    print(f"Loaded {len(isbns):,} ISBNs from {os.path.basename(ISBN_CSV)}")

    if args.sample:
        isbns = random.sample(isbns, min(args.sample, len(isbns)))
        print(f"Sample mode: processing {len(isbns)} randomly-selected ISBNs")

    # Load progress (for --resume)
    progress = load_progress() if args.resume else {}
    already_done = set(progress.keys())
    to_process = [i for i in isbns if i not in already_done]
    if already_done:
        print(f"Resuming: {len(already_done):,} already processed, {len(to_process):,} remaining")

    api_key = args.api_key or os.environ.get("GOOGLE_BOOKS_API_KEY", "")
    print(f"API key: {'provided' if api_key else 'none (1,000 req/day limit — set GOOGLE_BOOKS_API_KEY or use --api-key)'}")
    print(f"Estimated time: ~{len(to_process) // 60 + 1} minutes at 1 req/sec\n")

    # Query Google Books
    rate_limit_pause = 0
    for i, isbn in enumerate(to_process, 1):
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(to_process)} ({i + len(already_done)}/{len(isbns)} total)")
            save_progress(progress)

        if rate_limit_pause:
            time.sleep(rate_limit_pause)
            rate_limit_pause = 0

        title, categories = query_google_books(isbn, api_key)

        if title == "RATE_LIMIT":
            print(f"  Rate limited — pausing 60s...")
            time.sleep(60)
            title, categories = query_google_books(isbn, api_key)

        google_tag = map_google_category(categories) if categories else None

        progress[isbn] = {
            "google_title":      title or "",
            "google_categories": categories or [],
            "google_tag":        google_tag or "",
        }
        time.sleep(0.1)  # ~10 req/sec — well within limits

    save_progress(progress)

    # Now fetch current Shopify tags for comparison
    print(f"\nFetching current Shopify tags for {len(progress):,} products...")
    shopify_tags = _fetch_shopify_tags(list(progress.keys()))

    # Build results
    results = []
    for isbn, data in progress.items():
        current_tags = shopify_tags.get(isbn, [])
        current_bookscan = [t for t in current_tags if not t.startswith("_")]
        google_tag = data["google_tag"]

        # Subcategories considered too vague — Google can improve on these
        VAGUE_SUBCATS = {"General Fiction", "General", "Reference", ""}

        # Does Google agree with the current classification?
        current_subcat = current_bookscan[1] if len(current_bookscan) > 1 else (current_bookscan[0] if current_bookscan else "")
        is_vague = current_subcat in VAGUE_SUBCATS or not current_bookscan

        if not google_tag:
            match = "NO_DATA"
        elif google_tag in current_bookscan:
            match = "MATCH"
        elif is_vague and google_tag:
            match = "RECLASSIFY"  # vague/missing Bookscan tag — Google gives us something better
        else:
            match = "MISMATCH"   # Bookscan already has a specific tag — log for reference, don't auto-apply

        results.append({
            "isbn":               isbn,
            "shopify_title":      shopify_tags.get(f"{isbn}_title", ""),
            "google_title":       data["google_title"],
            "current_tags":       ", ".join(current_bookscan),
            "google_categories":  " | ".join(data["google_categories"]),
            "google_tag":         google_tag or "",
            "match":              match,
            "tags_to_add":        google_tag if match == "RECLASSIFY" else "",
        })

    # Write full report
    fieldnames = ["isbn", "shopify_title", "google_title", "current_tags",
                  "google_categories", "google_tag", "match", "tags_to_add"]

    with open(OUT_FULL, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(results)

    # Write changes-only report (what would actually change)
    changes = [r for r in results if r["tags_to_add"]]
    with open(OUT_CHANGES, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(changes)

    # Write Louisa report — grouped by recommended action
    louisa_rows = []
    by_tag = {}
    for r in changes:
        tag = r["tags_to_add"]
        by_tag.setdefault(tag, []).append(r)
    for tag in sorted(by_tag.keys()):
        for r in sorted(by_tag[tag], key=lambda x: x["shopify_title"]):
            louisa_rows.append({
                "Recommended Genre": tag,
                "ISBN":              r["isbn"],
                "Title":             r["shopify_title"] or r["google_title"],
                "Current Category":  r["current_tags"],
                "Google Says":       r["google_categories"],
            })
    with open(OUT_LOUISA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Recommended Genre", "ISBN", "Title", "Current Category", "Google Says"])
        w.writeheader()
        w.writerows(louisa_rows)

    # Summary
    total = len(results)
    matched    = sum(1 for r in results if r["match"] == "MATCH")
    reclassify = sum(1 for r in results if r["match"] == "RECLASSIFY")
    mismatch   = sum(1 for r in results if r["match"] == "MISMATCH")
    no_data    = sum(1 for r in results if r["match"] == "NO_DATA")

    print(f"\n{'='*60}")
    print(f"Audit complete — {total:,} books processed")
    print(f"  ✅ Match (Google agrees):           {matched:,} ({matched*100//total}%)")
    print(f"  🔄 Reclassify (out of General Fic): {reclassify:,} ({reclassify*100//total}%)")
    print(f"  ⚠️  Mismatch (wrong category):       {mismatch:,} ({mismatch*100//total}%)")
    print(f"  ❓ No Google data:                  {no_data:,} ({no_data*100//total}%)")
    print(f"\nTag breakdown for books to change:")
    for tag in sorted(by_tag.keys()):
        print(f"  {len(by_tag[tag]):>4}  → {tag}")
    print(f"\nReports written to Reports/:")
    print(f"  genre_audit_full.csv    — all {total:,} books")
    print(f"  genre_audit_changes.csv — {len(changes):,} books with recommended changes")
    print(f"  genre_audit_louisa.csv  — same, grouped by genre for Louisa's review")
    print(f"\nNext step: review genre_audit_changes.csv, then run:")
    print(f"  python genre_enrichment.py --apply --input Reports/genre_audit_changes.csv")


def _fetch_shopify_tags(isbns):
    """Fetch current tags and titles from Shopify for a list of ISBNs via GraphQL."""
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    result = {}
    batch_size = 50
    for i in range(0, len(isbns), batch_size):
        batch = isbns[i:i + batch_size]
        sku_filter = " OR ".join(f'sku:"{isbn}"' for isbn in batch)
        query = """
        query($q: String!) {
          productVariants(first: 50, query: $q) {
            edges {
              node {
                sku
                product {
                  title
                  tags
                }
              }
            }
          }
        }
        """
        r = requests.post(
            f"https://{SHOPIFY_STORE_URL}/admin/api/2024-01/graphql.json",
            headers=headers,
            json={"query": query, "variables": {"q": sku_filter}},
        )
        edges = r.json().get("data", {}).get("productVariants", {}).get("edges", [])
        for edge in edges:
            node = edge["node"]
            isbn = node["sku"]
            product = node.get("product", {})
            result[isbn] = product.get("tags", [])
            result[f"{isbn}_title"] = product.get("title", "")
        time.sleep(0.2)

    return result


def run_apply(args):
    print(f"\n{'='*60}")
    print(f"BMBooks Genre Enrichment — Apply Mode")
    if args.dry_run:
        print("DRY RUN — no changes will be made to Shopify")
    print(f"{'='*60}\n")

    if not args.input:
        print("Error: --apply requires --input <csv_file>")
        sys.exit(1)

    # Load approved changes
    rows = []
    with open(args.input) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("tags_to_add"):
                rows.append(row)
    print(f"Loaded {len(rows):,} books to tag from {args.input}")

    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json",
    }

    applied = skipped = errors = 0
    for i, row in enumerate(rows, 1):
        isbn = row["isbn"]
        new_tag = row["tags_to_add"].strip()

        if i % 50 == 0:
            print(f"  Progress: {i}/{len(rows)} — Applied: {applied}  Skipped: {skipped}  Errors: {errors}")

        # Find the product via GraphQL
        query = """
        query($q: String!) {
          productVariants(first: 1, query: $q) {
            edges {
              node {
                product { id tags }
              }
            }
          }
        }
        """
        r = requests.post(
            f"https://{SHOPIFY_STORE_URL}/admin/api/2024-01/graphql.json",
            headers=headers,
            json={"query": query, "variables": {"q": f'sku:"{isbn}"'}},
        )
        edges = r.json().get("data", {}).get("productVariants", {}).get("edges", [])
        if not edges:
            skipped += 1
            continue

        node = edges[0]["node"]["product"]
        product_gid = node["id"]
        current_tags = node["tags"]

        if new_tag in current_tags:
            skipped += 1
            continue

        if args.dry_run:
            print(f"  DRY RUN [{isbn}] Would add '{new_tag}' to existing: {current_tags[:3]}")
            applied += 1
            continue

        # Add the tag via GraphQL mutation
        updated_tags = current_tags + [new_tag]
        mutation = """
        mutation($id: ID!, $tags: [String!]!) {
          productUpdate(input: { id: $id, tags: $tags }) {
            userErrors { field message }
          }
        }
        """
        r = requests.post(
            f"https://{SHOPIFY_STORE_URL}/admin/api/2024-01/graphql.json",
            headers=headers,
            json={"query": mutation, "variables": {"id": product_gid, "tags": updated_tags}},
        )
        errs = r.json().get("data", {}).get("productUpdate", {}).get("userErrors", [])
        if errs:
            print(f"  Error [{isbn}]: {errs}")
            errors += 1
        else:
            applied += 1

        time.sleep(0.1)

    print(f"\n{'='*60}")
    print(f"Apply complete")
    print(f"  Applied:  {applied:,}")
    print(f"  Skipped:  {skipped:,} (already tagged or not found)")
    print(f"  Errors:   {errors:,}")


def main():
    parser = argparse.ArgumentParser(description="BMBooks Genre Enrichment Tool")
    parser.add_argument("--audit",   action="store_true", help="Run Google Books audit (default)")
    parser.add_argument("--apply",   action="store_true", help="Apply tags from approved CSV to Shopify")
    parser.add_argument("--sample",  type=int, metavar="N", help="Process only N ISBNs")
    parser.add_argument("--api-key", dest="api_key", metavar="KEY", help="Google Books API key")
    parser.add_argument("--resume",  action="store_true", help="Resume from previous progress file")
    parser.add_argument("--input",   metavar="FILE", help="Input CSV for --apply mode")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    args = parser.parse_args()

    if args.apply:
        run_apply(args)
    else:
        run_audit(args)


if __name__ == "__main__":
    main()
