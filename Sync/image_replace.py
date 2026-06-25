#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
# BMBooks — One-off image replacement
#
# Replaces blurry 64×100 thumbnails with high-res images from LargeImages\.
# Resolution cascade per ISBN: LargeImages\ → MediumImages\ → catalog\ → skip
# Products with no high-res image are left untouched (keep existing).
#
# Runtime: ~10–20 hours for ~34k products. Resumable — progress saved to
# image_replace_state.json after every 100 products.
#
# Run on shop machine:
#   python image_replace.py
#
# After this script completes, future bookscan_sync.py runs will naturally
# produce high-res images for any new product via the updated resolve_image().
# ─────────────────────────────────────────────────────────────────────────────

import os
import sys
import json
import time
import base64
import logging
import requests
from datetime import datetime

SHOPIFY_STORE_URL    = os.environ.get("SHOPIFY_STORE_URL", "bruce-mckenzie-booksellers.myshopify.com")
SHOPIFY_ACCESS_TOKEN = os.environ["SHOPIFY_ACCESS_TOKEN"]

# Image folders on the shop machine (Z: drive).
# Confirmed 2026-05-12: LargeImages\ has 257×400 images, ~40k files.
# Same {isbn}.jpg naming convention as catalog\.
LARGE_IMAGE_PATH  = r"Z:\bookscan\Catalog\LargeImages"
MEDIUM_IMAGE_PATH = r"Z:\bookscan\Catalog\MediumImages"
CATALOG_PATH      = r"Z:\bookscan\Catalog"

STATE_FILE = "image_replace_state.json"
LOG_FILE   = "image_replace.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# SHOPIFY API
# ─────────────────────────────────────────────────────────────────────────────

class ShopifyAPI:
    def __init__(self, store_url, token):
        self.base = f"https://{store_url}/admin/api/2024-01"
        self.headers = {
            "X-Shopify-Access-Token": token,
            "Content-Type": "application/json"
        }

    def _get(self, endpoint, params=None):
        url = f"{self.base}/{endpoint}"
        r = requests.get(url, headers=self.headers, params=params)
        time.sleep(0.6)
        r.raise_for_status()
        return r.json(), r.headers

    def _post(self, endpoint, data):
        url = f"{self.base}/{endpoint}"
        r = requests.post(url, headers=self.headers, json=data)
        time.sleep(0.6)
        if not r.ok:
            try:
                body = r.json()
            except Exception:
                body = r.text
            raise requests.HTTPError(
                f"{r.status_code} {r.reason} — Shopify: {body}",
                response=r
            )
        return r.json()

    def _delete(self, endpoint):
        url = f"{self.base}/{endpoint}"
        r = requests.delete(url, headers=self.headers)
        time.sleep(0.6)
        r.raise_for_status()

    def products_page(self, page_info=None, limit=250):
        """Fetch one page of products. Returns (products, next_page_info)."""
        params = {"limit": limit, "fields": "id,variants,images"}
        if page_info:
            params["page_info"] = page_info
        data, headers = self._get("products.json", params)

        next_page = None
        link = headers.get("Link", "")
        if 'rel="next"' in link:
            for part in link.split(","):
                if 'rel="next"' in part:
                    next_page = part.split("page_info=")[1].split(">")[0]
                    break

        return data.get("products", []), next_page

    def delete_image(self, product_id, image_id):
        self._delete(f"products/{product_id}/images/{image_id}.json")

    def upload_image(self, product_id, b64_data, filename):
        data = {"image": {"attachment": b64_data, "filename": filename}}
        return self._post(f"products/{product_id}/images.json", data)


# ─────────────────────────────────────────────────────────────────────────────
# IMAGE RESOLUTION
# ─────────────────────────────────────────────────────────────────────────────

def find_image(isbn):
    """
    Find the best available local image for this ISBN.
    Returns (path, source_label) or (None, None) if not found.
    """
    for folder, label in [
        (LARGE_IMAGE_PATH,  "large"),
        (MEDIUM_IMAGE_PATH, "medium"),
        (CATALOG_PATH,      "catalog"),
    ]:
        if folder:
            path = os.path.join(folder, f"{isbn}.jpg")
            if os.path.exists(path):
                return path, label
    return None, None


# ─────────────────────────────────────────────────────────────────────────────
# STATE — resumability
# ─────────────────────────────────────────────────────────────────────────────

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            raw = json.load(f)
        raw["processed"] = set(raw.get("processed", []))
        return raw
    return {"processed": set(), "replaced": 0, "skipped": 0, "errors": 0}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump({**state, "processed": list(state["processed"])}, f)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    api   = ShopifyAPI(SHOPIFY_STORE_URL, SHOPIFY_ACCESS_TOKEN)
    state = load_state()

    log.info("=" * 60)
    log.info("BMBooks image replacement")
    log.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(f"Resuming from {len(state['processed']):,} already processed")
    log.info(f"  Replaced: {state['replaced']:,}  Skipped: {state['skipped']:,}  Errors: {state['errors']:,}")
    log.info("=" * 60)

    page_info  = None
    total_seen = 0

    while True:
        products, page_info = api.products_page(page_info=page_info)
        if not products:
            break

        for product in products:
            variants = product.get("variants", [])
            if not variants:
                continue

            isbn       = variants[0].get("sku", "").strip()
            product_id = product["id"]

            if not isbn or isbn in state["processed"]:
                continue

            total_seen += 1

            image_path, source = find_image(isbn)

            if not image_path:
                state["skipped"]  += 1
                state["processed"].add(isbn)
                log.info(f"Skipped  [{isbn}] no image found in LargeImages/MediumImages/catalog")
                continue

            try:
                with open(image_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                api.upload_image(product_id, b64, f"{isbn}.jpg")

                for img in product.get("images", []):
                    api.delete_image(product_id, img["id"])

                state["replaced"] += 1
                state["processed"].add(isbn)
                log.info(f"Replaced [{isbn}] {source}")

            except Exception as e:
                log.error(f"Error    [{isbn}] {e}")
                state["errors"]  += 1
                state["processed"].add(isbn)

            if total_seen % 100 == 0:
                save_state(state)
                log.info(
                    f"  Progress {total_seen:,} — "
                    f"Replaced: {state['replaced']:,}  "
                    f"Skipped: {state['skipped']:,}  "
                    f"Errors: {state['errors']:,}"
                )

        if not page_info:
            break

    save_state(state)
    log.info("=" * 60)
    log.info(f"Done — Replaced: {state['replaced']:,}  Skipped: {state['skipped']:,}  Errors: {state['errors']:,}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
