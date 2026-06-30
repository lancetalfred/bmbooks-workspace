"""
Usage: python check_isbn_status.py <ISBN>

Read-only check: will the next sync change this ISBN's Shopify publish status?
Replicates the exact force_status decision logic from bookscan_sync.py against
real BookScan data and the current sync state — no Shopify writes.
"""
import sys
sys.path.insert(0, '.')
from bookscan_sync import read_products, load_state, ShopifyAPI, AUTO_PUBLISH, SHOPIFY_STORE_URL, SHOPIFY_ACCESS_TOKEN

if len(sys.argv) < 2:
    print("Usage: python check_isbn_status.py <ISBN>")
    sys.exit(1)

isbn = sys.argv[1].strip()

products = read_products()
matches = [p for p in products if p["isbn"] == isbn]
if not matches:
    print(f"{isbn} not found in active web-listed products (excluded by CSTATUS/DEPARTMENT, or not web-listed)")
    sys.exit(0)

p = matches[0]
state = load_state()
prev_price = state.get("fields", {}).get(isbn, {}).get("price", -1)

shopify = ShopifyAPI(SHOPIFY_STORE_URL, SHOPIFY_ACCESS_TOKEN)
existing = shopify.find_by_sku(isbn)

print(f"Title:          {p['title']!r}")
print(f"Title blank?:   {not bool(p['title'].strip())}")
print(f"Current price:  ${p['price']:.2f}")
print(f"Prev price (last sync): {prev_price}")
print(f"Exists in Shopify already: {bool(existing)}")
print(f"AUTO_PUBLISH: {AUTO_PUBLISH}")
print()

# Mirrors the exact decision logic in bookscan_sync.py — keep in sync if that changes.
if p["price"] == 0:
    decision = "force_status = draft (zero-price always hidden)"
elif AUTO_PUBLISH and existing and prev_price == 0 and p["price"] > 0:
    ready = bool(p["title"].strip())
    decision = f"force_status = {'active' if ready else 'draft'} (zero->priced transition, title guard {'passed' if ready else 'BLOCKED — blank title'})"
else:
    decision = "force_status = None — sync will NOT change this product's current Shopify status, whatever it is right now"

print(f"Next sync decision: {decision}")
