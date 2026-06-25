# ─────────────────────────────────────────────────────────────────────────────
# BMBooks — Post-sync duplicate product cleanup
#
# Finds duplicate Shopify products by variant SKU and deletes older copies,
# keeping the most-recently-updated one. Cleans up the ~36 duplicates created
# by the buggy REST find_by_sku before the GraphQL fix landed (2026-05-12).
#
# Usage:
#   python dedupe.py             — dry run, reports what would be deleted
#   python dedupe.py --execute   — actually delete duplicates
#
# Safe to re-run — does nothing if no duplicates exist.
# ─────────────────────────────────────────────────────────────────────────────

import sys
import time
from collections import defaultdict

from bookscan_sync import ShopifyAPI, SHOPIFY_STORE_URL, SHOPIFY_ACCESS_TOKEN, log


DRY_RUN = "--execute" not in sys.argv


def list_all_products(api):
    """Paginate through every product in the store via GraphQL."""
    query = """
    query listProducts($cursor: String) {
      products(first: 100, after: $cursor) {
        edges {
          cursor
          node {
            id
            title
            updatedAt
            variants(first: 1) {
              edges { node { sku } }
            }
          }
        }
        pageInfo { hasNextPage }
      }
    }
    """
    products = []
    cursor = None
    page = 0
    while True:
        page += 1
        result = api._graphql(query, {"cursor": cursor})
        edges = result["data"]["products"]["edges"]
        for edge in edges:
            node = edge["node"]
            variants = node["variants"]["edges"]
            sku = variants[0]["node"]["sku"] if variants else None
            products.append({
                "product_id": int(node["id"].rsplit("/", 1)[-1]),
                "title":      node["title"],
                "updated_at": node["updatedAt"],
                "sku":        sku,
            })
        if page % 10 == 0:
            log.info(f"  Listed {len(products):,} products so far (page {page})")
        if not result["data"]["products"]["pageInfo"]["hasNextPage"]:
            break
        cursor = edges[-1]["cursor"]
    return products


def find_duplicate_groups(products):
    """Group products by SKU; return only SKUs that have more than one product."""
    by_sku = defaultdict(list)
    for p in products:
        if p["sku"]:
            by_sku[p["sku"]].append(p)
    return {sku: items for sku, items in by_sku.items() if len(items) > 1}


def main():
    log.info(f"Dedupe — {'DRY RUN' if DRY_RUN else 'EXECUTE'} mode")

    api = ShopifyAPI(SHOPIFY_STORE_URL, SHOPIFY_ACCESS_TOKEN)

    log.info("Listing all products from Shopify...")
    t0 = time.time()
    products = list_all_products(api)
    log.info(f"  {len(products):,} total products listed in {time.time() - t0:.0f}s")

    duplicates = find_duplicate_groups(products)
    if not duplicates:
        log.info("No duplicates found. Nothing to do.")
        return

    extras = sum(len(items) - 1 for items in duplicates.values())
    log.info(f"Found {len(duplicates)} SKUs with duplicates — {extras} extra products to delete")

    # For each duplicate group, keep the most-recently-updated and queue the rest for deletion
    to_delete = []
    for sku, items in duplicates.items():
        sorted_items = sorted(items, key=lambda p: p["updated_at"], reverse=True)
        keep = sorted_items[0]
        for item in sorted_items[1:]:
            to_delete.append({**item, "kept_id": keep["product_id"]})

    log.info(f"Sample of duplicates that would be deleted (first 20 of {len(to_delete)}):")
    for d in to_delete[:20]:
        log.info(f"  SKU {d['sku']}: delete {d['product_id']} ({d['title'][:50]}), keep {d['kept_id']}")
    if len(to_delete) > 20:
        log.info(f"  ... and {len(to_delete) - 20} more")

    if DRY_RUN:
        log.info("DRY RUN — re-run with --execute to perform deletions")
        return

    log.info(f"Deleting {len(to_delete)} duplicate products...")
    deleted = 0
    errors = 0
    for d in to_delete:
        try:
            api._request("DELETE", f"products/{d['product_id']}.json")
            deleted += 1
            if deleted % 10 == 0:
                log.info(f"  Deleted {deleted}/{len(to_delete)}")
        except Exception as e:
            log.error(f"  Failed to delete {d['product_id']} ({d['sku']}): {e}")
            errors += 1

    log.info(f"Done. Deleted: {deleted}  Errors: {errors}")


if __name__ == "__main__":
    main()
