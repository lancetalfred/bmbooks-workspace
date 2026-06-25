"""
Fix incorrect product_type values for BO and BB binding codes.

The shop machine had swapped/wrong mappings:
  BB → "Big Book"   (should be "Board Book")
  BO → "Board Book" (should be "Boxed")

This script:
  1. Collects all products with product_type "Board Book" (BO products → "Boxed")
  2. Collects all products with product_type "Big Book"   (BB products → "Board Book")
  3. Updates each product's product_type to the correct value

Usage:
  python fix_binding_codes.py --dry-run   # preview changes
  python fix_binding_codes.py             # apply changes
"""

import os
import requests
import time
import sys

SHOPIFY_STORE_URL    = os.environ.get("SHOPIFY_STORE_URL", "bruce-mckenzie-booksellers.myshopify.com")
SHOPIFY_ACCESS_TOKEN = os.environ["SHOPIFY_ACCESS_TOKEN"]
API_VERSION          = "2024-01"
BASE_URL             = f"https://{SHOPIFY_STORE_URL}/admin/api/{API_VERSION}"
HEADERS              = {
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
    "Content-Type": "application/json",
}

DRY_RUN = "--dry-run" in sys.argv

FIXES = [
    ("Board Book", "Boxed"),
    ("Big Book",   "Board Book"),
]


def get_products_by_type(product_type):
    """Fetch all product IDs with the given product_type, paginating through results."""
    products = []
    url = f"{BASE_URL}/products.json"
    params = {
        "product_type": product_type,
        "fields": "id,title,product_type",
        "limit": 250,
    }

    while url:
        response = requests.get(url, headers=HEADERS, params=params)
        time.sleep(0.6)
        response.raise_for_status()

        data = response.json()
        products.extend(data.get("products", []))

        link_header = response.headers.get("Link", "")
        url = None
        params = None
        if 'rel="next"' in link_header:
            for part in link_header.split(","):
                if 'rel="next"' in part:
                    url = part.split("<")[1].split(">")[0]
                    break

    return products


def update_product_type(product_id, new_type):
    """Update a single product's product_type."""
    url = f"{BASE_URL}/products/{product_id}.json"
    payload = {"product": {"id": product_id, "product_type": new_type}}
    response = requests.put(url, headers=HEADERS, json=payload)
    time.sleep(0.6)
    response.raise_for_status()
    return response.json()


def main():
    if DRY_RUN:
        print("=== DRY RUN — no changes will be made ===\n")

    for old_type, new_type in FIXES:
        print(f"Finding products with product_type = \"{old_type}\"...")
        products = get_products_by_type(old_type)
        print(f"  Found {len(products)} products to update → \"{new_type}\"\n")

        if not products:
            continue

        updated = 0
        errors = 0
        for i, product in enumerate(products, 1):
            pid = product["id"]
            title = product["title"]

            if DRY_RUN:
                print(f"  [{i}/{len(products)}] Would update: {title}")
            else:
                try:
                    update_product_type(pid, new_type)
                    updated += 1
                    if i % 50 == 0 or i == len(products):
                        print(f"  Progress: {i}/{len(products)} (updated: {updated}, errors: {errors})")
                except Exception as e:
                    errors += 1
                    print(f"  ERROR [{pid}] {title}: {e}")

        if not DRY_RUN:
            print(f"\n  Done: {updated} updated, {errors} errors\n")
        else:
            print()

    print("Complete.")


if __name__ == "__main__":
    main()
