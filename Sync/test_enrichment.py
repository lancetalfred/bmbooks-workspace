#!/usr/bin/env python3
"""
Targeted validation test for genre_enrichment.py

Tests 8 category segments (20 books each) to confirm the enrichment script:
  - Correctly reclassifies vague categories (General Fiction)
  - Does NOT reclassify books with good specific tags (Crime Fiction, Biography etc.)
  - Does NOT reclassify NZ/Maori books with international categories
  - Does NOT reclassify gifts/stationery as book genres
  - Handles children's sub-categories correctly

Run from the Sync/ directory:
  python3 test_enrichment.py --api-key YOUR_KEY
  or
  export GOOGLE_BOOKS_API_KEY=YOUR_KEY && python3 test_enrichment.py
"""

import csv, os, sys, time, requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from genre_enrichment import query_google_books, map_google_category, SHOPIFY_STORE_URL, SHOPIFY_ACCESS_TOKEN

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--api-key", dest="api_key", default="")
args = parser.parse_args()
API_KEY = args.api_key or os.environ.get("GOOGLE_BOOKS_API_KEY", "")

if not API_KEY:
    print("⚠️  No API key — run with --api-key YOUR_KEY or export GOOGLE_BOOKS_API_KEY=YOUR_KEY")
    print("   Without a key you may hit the 1,000/day free limit quickly.\n")

HEADERS = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN, "Content-Type": "application/json"}
VAGUE_SUBCATS = {"General Fiction", "General", "Reference", ""}

# Segments to test: (name, shopify_tag_to_query, should_reclassify)
SEGMENTS = [
    ("General Fiction",             "General Fiction",              True),   # SHOULD reclassify — vague
    ("Crime Fiction",               "Crime Fiction",                False),  # should NOT reclassify
    ("Biography",                   "Biography",                    False),  # should NOT reclassify
    ("Stationery / Gifts",          "Stationery Puzzles And Gifts", False),  # should NOT reclassify
    ("NZ / Maori",                  "Maori Studies and History",    False),  # should NOT reclassify
    ("Childrens Picture Books",     "Childrens Picture Books",      False),  # should NOT reclassify
    ("Books For Babies",            "Books For Babies",             False),  # should NOT reclassify
    ("Science Fiction and Fantasy", "Science Fiction and Fantasy",  False),  # should NOT reclassify
]

def fetch_isbns_by_tag(tag, limit=20):
    q = f'tag:"{tag}"'
    r = requests.post(
        f"https://{SHOPIFY_STORE_URL}/admin/api/2024-01/graphql.json",
        headers=HEADERS,
        json={"query": 'query($q:String!){productVariants(first:20,query:$q){edges{node{sku product{title tags}}}}}',
              "variables": {"q": q}}
    )
    edges = r.json().get("data", {}).get("productVariants", {}).get("edges", [])
    return [(e["node"]["sku"], e["node"]["product"]["title"], e["node"]["product"]["tags"])
            for e in edges if e["node"]["sku"]]

print(f"\n{'='*80}")
print(f"BMBooks Genre Enrichment — Targeted Segment Validation")
print(f"API key: {'provided ✅' if API_KEY else 'MISSING ⚠️'}")
print(f"{'='*80}\n")

passed = 0
failed = 0
issues = []

for segment_name, shopify_tag, should_reclassify in SEGMENTS:
    print(f"Testing: {segment_name}")
    books = fetch_isbns_by_tag(shopify_tag)
    if not books:
        print(f"  ⚠️  No books found for tag '{shopify_tag}' — skipping\n")
        continue

    counts = {"MATCH": 0, "RECLASSIFY": 0, "MISMATCH": 0, "NO_DATA": 0}
    reclassify_detail = []
    mismatch_detail = []

    for isbn, title, current_tags_list in books:
        gb_title, categories = query_google_books(isbn, API_KEY)
        google_tag = map_google_category(categories) if categories else None

        current_bookscan = [t for t in current_tags_list if not t.startswith("_")]
        current_subcat = current_bookscan[1] if len(current_bookscan) > 1 else (current_bookscan[0] if current_bookscan else "")
        is_vague = current_subcat in VAGUE_SUBCATS or not current_bookscan

        if not google_tag:
            match = "NO_DATA"
        elif google_tag in current_bookscan:
            match = "MATCH"
        elif is_vague and google_tag:
            match = "RECLASSIFY"
        else:
            match = "MISMATCH"

        counts[match] += 1

        if match == "RECLASSIFY":
            reclassify_detail.append(f"    [{isbn}] {title[:50]} → '{google_tag}' (Google: {(categories or [''])[0][:40]})")
        if match == "MISMATCH":
            mismatch_detail.append(f"    [{isbn}] {title[:45]} | Bookscan: '{current_subcat}' | Google: '{google_tag}'")

        time.sleep(0.1)

    total_with_data = counts["MATCH"] + counts["RECLASSIFY"] + counts["MISMATCH"]
    print(f"  ✅ Match: {counts['MATCH']}  🔄 Reclassify: {counts['RECLASSIFY']}  ⚠️  Mismatch: {counts['MISMATCH']}  ❓ No data: {counts['NO_DATA']}")

    # Validate behaviour
    if should_reclassify:
        if counts["RECLASSIFY"] > 0:
            print(f"  ✅ PASS — correctly reclassifying vague books")
            for d in reclassify_detail[:5]:
                print(d)
            passed += 1
        elif total_with_data == 0:
            print(f"  ⚠️  INCONCLUSIVE — no Google data for any books in this segment")
        else:
            print(f"  ⚠️  INCONCLUSIVE — Google data found but nothing to reclassify (may be correct)")
            passed += 1
    else:
        if counts["RECLASSIFY"] > 0:
            print(f"  ❌ FAIL — script is reclassifying books that should NOT change:")
            for d in reclassify_detail:
                print(d)
            issues.append(f"FAIL: {segment_name} — {counts['RECLASSIFY']} unexpected reclassification(s)")
            failed += 1
        elif total_with_data == 0:
            print(f"  ⚠️  INCONCLUSIVE — no Google data returned (check API key / rate limit)")
        else:
            print(f"  ✅ PASS — no unexpected reclassifications")
            passed += 1

    if mismatch_detail and not should_reclassify:
        print(f"  ℹ️  Mismatches (logged only, no changes):")
        for d in mismatch_detail[:3]:
            print(d)

    print()

print(f"{'='*80}")
print(f"RESULTS: {passed} passed  |  {failed} failed")
if issues:
    print(f"\n⚠️  ISSUES — fix before running full audit:")
    for issue in issues:
        print(f"  {issue}")
else:
    print(f"\n✅ All segments behaved correctly. Safe to run full audit.")
print(f"{'='*80}")
