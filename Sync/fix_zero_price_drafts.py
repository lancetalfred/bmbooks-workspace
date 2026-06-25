"""
fix_zero_price_drafts.py — one-time cleanup script.

Sets all Active Shopify products with a zero price to Draft so they're hidden from
customers. Run before go-live day (and before removing the store password).

After this runs, bookscan_sync.py's force_status logic keeps zero-price products
as Draft going forward — this script is only needed once to clean up existing ones.

Usage:
    python fix_zero_price_drafts.py           # live run
    python fix_zero_price_drafts.py --dry-run # preview only, no changes
"""

import sys
import logging

# Import API credentials and ShopifyAPI class from the main sync script.
# Safe to import because bookscan_sync.py's main() only runs under __name__ == "__main__".
from bookscan_sync import ShopifyAPI, SHOPIFY_STORE_URL, SHOPIFY_ACCESS_TOKEN

DRY_RUN = "--dry-run" in sys.argv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def main():
    mode = "DRY RUN — no changes will be made" if DRY_RUN else "LIVE — will set zero-price products to Draft"
    log.info(f"fix_zero_price_drafts.py starting — {mode}")

    shopify = ShopifyAPI(SHOPIFY_STORE_URL, SHOPIFY_ACCESS_TOKEN)

    scanned = 0
    found = 0
    fixed = 0
    since_id = 0

    while True:
        result = shopify._request(
            "GET",
            f"products.json?limit=250&since_id={since_id}&fields=id,title,status,variants"
        )
        products = result.get("products", [])
        if not products:
            break

        for product in products:
            scanned += 1
            variants = product.get("variants", [])
            if not variants:
                continue

            all_zero = all(float(v.get("price", "0") or "0") == 0.0 for v in variants)
            if not all_zero:
                continue

            found += 1
            pid = product["id"]
            title = product.get("title", "—")
            status = product.get("status", "unknown")

            if DRY_RUN:
                log.info(f"  [DRY RUN] Would set to Draft: [{pid}] {title!r} (currently: {status})")
            else:
                shopify._request("PUT", f"products/{pid}.json", {"product": {"status": "draft"}})
                fixed += 1
                log.info(f"  Drafted [{pid}] {title!r} (was: {status})")

        since_id = products[-1]["id"]

        if scanned % 2500 == 0:
            log.info(f"  Progress: {scanned:,} scanned, {found:,} zero-price found so far...")

    log.info(f"Complete — {scanned:,} products scanned, {found:,} zero-price found, {fixed:,} set to Draft")
    if DRY_RUN and found > 0:
        log.info("Re-run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
