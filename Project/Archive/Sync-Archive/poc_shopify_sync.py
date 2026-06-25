# ─────────────────────────────────────────────────────────────────────────────
# BMBooks — Shopify Sync POC
# Reads WooCommerce CSV export → pushes products to Shopify dev store
#
# This is the proof of concept. Once confirmed working:
#   - Replace CSV reader with DBF reader from bookscan_sync.py
#   - Point at live Shopify store instead of dev store
#
# Usage:
#   pip install -r requirements.txt
#   python poc_shopify_sync.py products.csv
# ─────────────────────────────────────────────────────────────────────────────

import os
import re
import sys
import csv
import time
import logging
import requests
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION — fill in before running
# ─────────────────────────────────────────────────────────────────────────────

SHOPIFY_STORE_URL    = os.environ.get("SHOPIFY_STORE_URL", "bruce-mckenzie-booksellers.myshopify.com")
SHOPIFY_ACCESS_TOKEN = os.environ["SHOPIFY_ACCESS_TOKEN"]

BATCH_SIZE = 10     # products to sync per run (start small, increase once confirmed)
DRY_RUN    = False   # set to False to actually push to Shopify


# ─────────────────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# DESCRIPTION PARSER
# Bookscan embeds author, format, pub date, pages into the WooCommerce
# description field as structured HTML text. This extracts them.
#
# Example description snippet:
#   Author: PATTERSON JAMES<br>
#   Format: Hardback<br>
#   Publication date: 05/06/2025<br>
#   Pages: 192<br>
# ─────────────────────────────────────────────────────────────────────────────

def parse_description(html):
    """
    Extract structured fields from Bookscan's description HTML.
    Returns dict of extracted fields + cleaned body text.
    """
    def extract(pattern, text):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else ""

    # Normalise line breaks so regex works consistently
    text = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
    text = re.sub(r'<BR\s*/?>', '\n', text)

    author   = extract(r'Author:\s*(.+)',           text)
    binding  = extract(r'Format:\s*(.+)',            text)
    pub_date = extract(r'Publication date:\s*(.+)', text)
    pages    = extract(r'Pages:\s*(\d+)',            text)

    # Build clean body_html — strip metadata lines, keep the synopsis
    # Remove the structured header block (ISBN: / Title: / Author: lines)
    body = re.sub(r'(ISBN|Title|Author|Format|Publication date|Pages|Available stock|Temporarily out of stock)[^\n]*\n?', '', text)
    # Strip remaining HTML tags
    body = re.sub(r'<[^>]+>', '', body)
    # Collapse whitespace
    body = re.sub(r'\n{3,}', '\n\n', body).strip()

    return {
        "author":   author,
        "binding":  binding,
        "pub_date": pub_date,
        "pages":    pages,
        "body":     body,
    }


def is_valid_isbn(isbn):
    """
    Return True only for 13-digit numeric ISBNs.
    Filters out vouchers (BMBVOU10) and malformed entries.
    """
    return bool(re.match(r'^\d{13}$', isbn.strip()))


# ─────────────────────────────────────────────────────────────────────────────
# SHOPIFY API
# ─────────────────────────────────────────────────────────────────────────────

class ShopifyAPI:
    def __init__(self, store_url, access_token):
        self.base = f"https://{store_url}/admin/api/2024-01"
        self.headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }

    def _request(self, method, endpoint, data=None):
        url = f"{self.base}/{endpoint}"
        response = requests.request(method, url, headers=self.headers, json=data)
        time.sleep(0.6)   # Shopify Basic rate limit: 2 req/sec
        response.raise_for_status()
        return response.json()

    def find_by_sku(self, sku):
        result = self._request("GET", f"variants.json?sku={sku}&fields=id,sku,product_id,inventory_item_id")
        variants = result.get("variants", [])
        # Validate exact SKU match — Shopify can return all variants if the filter is ignored
        matching = [v for v in variants if v.get("sku") == sku]
        if matching:
            v = matching[0]
            return v["product_id"], v["id"], v["inventory_item_id"]
        return None

    def create_product(self, data):
        result = self._request("POST", "products.json", {"product": data})
        return result["product"]

    def update_product(self, product_id, data):
        result = self._request("PUT", f"products/{product_id}.json", {"product": data})
        return result["product"]

    def get_location_id(self):
        result = self._request("GET", "locations.json")
        return result["locations"][0]["id"]

    def set_inventory(self, inventory_item_id, location_id, quantity):
        # Step 1: check inventory item tracking status
        item_data = self._request("GET", f"inventory_items/{inventory_item_id}.json")
        item = item_data.get("inventory_item", {})
        tracked = item.get("tracked", False)
        log.info(f"  inv_item={inventory_item_id} tracked={tracked}")

        # Step 2: enable tracking if it's off (API-created items often default to untracked)
        if not tracked:
            self._request("PUT", f"inventory_items/{inventory_item_id}.json", {
                "inventory_item": {"id": inventory_item_id, "tracked": True}
            })
            log.info(f"  Enabled tracking for inv_item={inventory_item_id}")

        # Step 3: connect to location
        try:
            self._request("POST", "inventory_levels/connect.json", {
                "location_id":       location_id,
                "inventory_item_id": inventory_item_id,
            })
            log.info(f"  Connected to location={location_id}")
        except Exception as e:
            log.info(f"  Connect skipped (already connected): {e}")

        # Step 4: set quantity
        self._request("POST", "inventory_levels/set.json", {
            "location_id":       location_id,
            "inventory_item_id": inventory_item_id,
            "available":         int(quantity or 0)
        })

    def get_inventory_item(self, inventory_item_id):
        """Fetch inventory item to verify it exists and is tracked."""
        return self._request("GET", f"inventory_items/{inventory_item_id}.json")


# ─────────────────────────────────────────────────────────────────────────────
# CSV READER
# ─────────────────────────────────────────────────────────────────────────────

def read_csv(filepath):
    """
    Read WooCommerce export CSV.
    Parses description to extract author, binding, pub_date, pages.
    Filters out vouchers and products without valid ISBNs.
    """
    products = []
    skipped  = 0

    with open(filepath, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            isbn = row.get("isbn", "").strip()

            # Skip vouchers and anything without a valid 13-digit ISBN
            if not is_valid_isbn(isbn):
                skipped += 1
                continue

            description = row.get("description", "")
            parsed      = parse_description(description)

            products.append({
                "isbn":      isbn,
                "title":     row.get("title", "").strip(),
                "body":      parsed["body"],
                "price":     row.get("price", "0").strip() or "0",
                "stock":     row.get("stock", "0").strip() or "0",
                "weight":    row.get("weight", "0").strip().replace("NULL", "0") or "0",
                "author":    parsed["author"],
                "binding":   parsed["binding"],
                "pub_date":  parsed["pub_date"],
                "pages":     parsed["pages"],
            })

    log.info(f"Read {len(products)} valid products from CSV ({skipped} skipped — vouchers/invalid ISBNs)")
    return products


# ─────────────────────────────────────────────────────────────────────────────
# FIELD MAPPING — WooCommerce CSV → Shopify
# ─────────────────────────────────────────────────────────────────────────────

def to_shopify_product(p):
    metafields = []

    for key, value in [
        ("author",           p["author"]),
        ("isbn",             p["isbn"]),
        ("pages",            p["pages"]),
        ("publication_date", p["pub_date"]),
    ]:
        if value:
            metafields.append({
                "namespace": "bookscan",
                "key":       key,
                "value":     value,
                "type":      "single_line_text_field"
            })

    return {
        "title":        p["title"],
        "product_type": p["binding"] or "Book",
        "body_html":    p["body"],
        "status":       "draft",
        "variants": [{
            "sku":                  p["isbn"],
            "price":                p["price"],
            "inventory_management": "shopify",
            "inventory_quantity":   int(p.get("stock", 0) or 0),
            "inventory_policy":     "continue",   # "Available to order" when out of stock
            "weight":               float(p["weight"] or 0),
            "weight_unit":          "g",    # Bookscan weight is in grams
            "requires_shipping":    True,
            "taxable":              False,  # NZ books are GST exempt
        }],
        "metafields": metafields
    }


# ─────────────────────────────────────────────────────────────────────────────
# SYNC
# ─────────────────────────────────────────────────────────────────────────────

def run_poc(csv_path):
    log.info("=" * 60)
    log.info(f"BMBooks Shopify POC — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(f"Source:  {csv_path}")
    log.info(f"Store:   {SHOPIFY_STORE_URL}")
    log.info(f"Dry run: {DRY_RUN}")
    log.info("=" * 60)

    products = read_csv(csv_path)
    batch    = products[:BATCH_SIZE]
    log.info(f"Processing {len(batch)} of {len(products)} products (batch size: {BATCH_SIZE})")

    if DRY_RUN:
        log.info("DRY RUN — showing what would be sent to Shopify:")
        for p in batch:
            log.info(f"  [{p['isbn']}] {p['title']}")
            log.info(f"    Price: ${p['price']}  Stock: {p['stock']}  Weight: {p['weight']}g")
            log.info(f"    Author: {p['author']}  Format: {p['binding']}  Pages: {p['pages']}")
            log.info(f"    Pub date: {p['pub_date']}")
            log.info(f"    Body preview: {p['body'][:80]}...")
            log.info("")
        log.info("Set DRY_RUN = False to push to Shopify")
        return

    shopify     = ShopifyAPI(SHOPIFY_STORE_URL, SHOPIFY_ACCESS_TOKEN)
    location_id = shopify.get_location_id()

    created = updated = errors = 0

    for p in batch:
        shopify_p = to_shopify_product(p)

        try:
            existing = shopify.find_by_sku(p["isbn"])

            if existing:
                product_id, _, inv_item_id = existing
                shopify.update_product(product_id, shopify_p)
                updated += 1
                log.info(f"Updated  [{p['isbn']}] {p['title']}")
                try:
                    shopify.set_inventory(inv_item_id, location_id, int(p["stock"]))
                except Exception as inv_e:
                    log.warning(f"  Inventory update failed (non-fatal): {inv_e}")
            else:
                result = shopify.create_product(shopify_p)
                created += 1
                log.info(f"Created  [{p['isbn']}] {p['title']}")

        except Exception as e:
            log.error(f"Error    [{p['isbn']}] {p['title']} — {e}")
            errors += 1

    log.info(f"\nPOC complete — Created: {created}  Updated: {updated}  Errors: {errors}")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python poc_shopify_sync.py products.csv")
        sys.exit(1)

    run_poc(sys.argv[1])
