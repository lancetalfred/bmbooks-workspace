# ─────────────────────────────────────────────────────────────────────────────
# BMBooks — Inventory diagnostic
#
# For the products that failed `inventorySetOnHandQuantities` with "the
# specified inventory item could not be found" during the initial backfill,
# this script queries the variant + inventory item directly to figure out
# why Shopify can't resolve the inventory item ID.
#
# Run with no arguments for a default sample, or pass specific ISBNs:
#   python diagnose_inventory.py
#   python diagnose_inventory.py 028945650128 190295708085
#
# Read-only — makes no changes to Shopify.
# ─────────────────────────────────────────────────────────────────────────────

import sys
import json

from bookscan_sync import ShopifyAPI, SHOPIFY_STORE_URL, SHOPIFY_ACCESS_TOKEN


# Sample of products known to fail set_inventory during 2026-05-12 backfill.
# These are the very first products processed each run (in ISBN order), all of
# them existing products that ran through the Update path rather than Create.
DEFAULT_SKUS = [
    "028945650128",   # Liszt For Lovers (CD)
    "028945655222",   # Guitar Favorites (CD)
    "0723803997246",  # Takaro - Feelings and Emotions
    "190295708085",   # Beau soir - Works for Violin and Piano (CD)
]


VARIANT_QUERY = """
query getVariant($id: ID!) {
  productVariant(id: $id) {
    id
    sku
    title
    inventoryQuantity
    inventoryPolicy
    inventoryItem {
      id
      sku
      tracked
      requiresShipping
    }
  }
}
"""

INVENTORY_ITEM_QUERY = """
query getItem($id: ID!) {
  inventoryItem(id: $id) {
    id
    sku
    tracked
    inventoryLevels(first: 5) {
      edges {
        node {
          id
          location { id name }
          quantities(names: ["on_hand", "available", "incoming"]) { name quantity }
        }
      }
    }
  }
}
"""


def diagnose(api, sku):
    print(f"\n{'=' * 70}")
    print(f"SKU: {sku}")
    print('=' * 70)

    # Step 1: find via find_by_sku (the same path the sync uses)
    result = api.find_by_sku(sku)
    if not result:
        print("  find_by_sku → None — product doesn't exist in Shopify")
        return

    product_id, variant_id, inventory_item_id = result
    print(f"  find_by_sku → product {product_id}, variant {variant_id}, inv_item {inventory_item_id}")

    # Step 2: query the variant directly — what does Shopify say about its inventory state?
    print("\n  --- Variant direct query ---")
    res = api._graphql(VARIANT_QUERY, {"id": f"gid://shopify/ProductVariant/{variant_id}"})
    variant = res.get("data", {}).get("productVariant")
    if variant:
        print(json.dumps(variant, indent=4))
    else:
        print(f"  (variant query returned no data — errors: {res.get('errors')})")

    # Step 3: query the inventoryItem directly — does it exist as a queryable entity?
    print("\n  --- InventoryItem direct query ---")
    res = api._graphql(INVENTORY_ITEM_QUERY, {"id": f"gid://shopify/InventoryItem/{inventory_item_id}"})
    item = res.get("data", {}).get("inventoryItem")
    if item is None:
        print("  ⚠️  inventoryItem query returned NULL — this is the bug.")
        print("  The variant references an inventory_item_id that doesn't resolve to a real entity.")
        if res.get("errors"):
            print(f"  GraphQL errors: {res['errors']}")
    else:
        print(json.dumps(item, indent=4))


def main():
    api = ShopifyAPI(SHOPIFY_STORE_URL, SHOPIFY_ACCESS_TOKEN)
    skus = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_SKUS
    for sku in skus:
        diagnose(api, sku)


if __name__ == "__main__":
    main()
