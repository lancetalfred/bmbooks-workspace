"""
Create / update smart collections for BMBooks genre enrichment.

Collections created (tag is [name]):
  Romance, Horror, Manga, Thriller, Translated Fiction

Existing Romance / Horror collections are updated to use the new tag format
(enrichment script applies 'Romance' / 'Horror' without the old 'genre:' prefix).

Usage:
  python3 create_genre_collections.py          # preview only
  python3 create_genre_collections.py --apply  # write to Shopify
"""

import argparse
import os
import json
import sys
import requests

SHOPIFY_STORE_URL    = os.environ.get("SHOPIFY_STORE_URL", "bruce-mckenzie-booksellers.myshopify.com")
SHOPIFY_ACCESS_TOKEN = os.environ["SHOPIFY_ACCESS_TOKEN"]

HEADERS = {
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
    "Content-Type": "application/json",
}
BASE = f"https://{SHOPIFY_STORE_URL}/admin/api/2024-01"

# Collections we want to exist with correct tag rules
DESIRED = [
    {"title": "Romance",          "tag": "Romance"},
    {"title": "Horror",           "tag": "Horror"},
    {"title": "Manga",            "tag": "Manga"},
    {"title": "Thriller",         "tag": "Thriller"},
    {"title": "Translated Fiction","tag": "Translated Fiction"},
]


def get_all_smart_collections():
    collections = []
    url = f"{BASE}/smart_collections.json?limit=250&fields=id,title,rules"
    while url:
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()
        data = r.json()
        collections.extend(data.get("smart_collections", []))
        link = r.headers.get("Link", "")
        url = None
        for part in link.split(","):
            if 'rel="next"' in part:
                url = part.split("<")[1].split(">")[0].strip()
    return collections


def build_rule(tag):
    return [{"column": "tag", "relation": "equals", "condition": tag}]


def create_collection(title, tag, dry_run):
    payload = {
        "smart_collection": {
            "title": title,
            "rules": build_rule(tag),
            "disjunctive": False,
            "published": True,
        }
    }
    if dry_run:
        print(f"  [DRY RUN] Would CREATE '{title}'  (tag is {tag!r})")
        return
    r = requests.post(f"{BASE}/smart_collections.json", headers=HEADERS, json=payload)
    r.raise_for_status()
    sc = r.json()["smart_collection"]
    print(f"  CREATED '{sc['title']}'  id={sc['id']}")


def update_collection(cid, title, tag, dry_run):
    payload = {
        "smart_collection": {
            "id": cid,
            "rules": build_rule(tag),
            "disjunctive": False,
        }
    }
    if dry_run:
        print(f"  [DRY RUN] Would UPDATE '{title}'  → tag is {tag!r}")
        return
    r = requests.put(f"{BASE}/smart_collections/{cid}.json", headers=HEADERS, json=payload)
    r.raise_for_status()
    print(f"  UPDATED '{title}'  id={cid}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write to Shopify (default is dry run)")
    args = parser.parse_args()
    dry_run = not args.apply

    if dry_run:
        print("DRY RUN — pass --apply to write\n")

    print("Fetching existing smart collections...")
    existing = get_all_smart_collections()
    by_title = {c["title"].strip(): c for c in existing}

    for spec in DESIRED:
        title = spec["title"]
        tag   = spec["tag"]

        if title in by_title:
            coll  = by_title[title]
            rules = coll.get("rules", [])
            current_tags = [r["condition"] for r in rules if r.get("column") == "tag"]
            if current_tags == [tag]:
                print(f"  OK '{title}'  already has correct rule (tag is {tag!r})")
            else:
                print(f"  UPDATING '{title}'  current={current_tags}  → {[tag]}")
                update_collection(coll["id"], title, tag, dry_run)
        else:
            print(f"  MISSING '{title}'")
            create_collection(title, tag, dry_run)

    print("\nDone.")


if __name__ == "__main__":
    main()
