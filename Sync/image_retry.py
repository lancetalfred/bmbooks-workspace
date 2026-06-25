#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
# BMBooks — Image retry for 422 errors from image_replace.py
#
# Targets the 101 ISBNs that got Shopify 422 errors. Uses product IDs from
# the log (no pagination needed). Logs Shopify's full response body so we can
# diagnose the actual rejection reason.
#
# These products currently have NO IMAGE — old thumbnail was deleted before
# the failed upload. This script restores them.
#
# Run on shop machine:
#   python image_retry.py [--dry-run]
# ─────────────────────────────────────────────────────────────────────────────

import os
import sys
import base64
import logging
import requests
import time
from datetime import datetime

SHOPIFY_STORE_URL    = os.environ.get("SHOPIFY_STORE_URL", "bruce-mckenzie-booksellers.myshopify.com")
SHOPIFY_ACCESS_TOKEN = os.environ["SHOPIFY_ACCESS_TOKEN"]

LARGE_IMAGE_PATH  = r"Z:\bookscan\Catalog\LargeImages"
MEDIUM_IMAGE_PATH = r"Z:\bookscan\Catalog\MediumImages"
CATALOG_PATH      = r"Z:\bookscan\Catalog"

LOG_FILE = "image_retry.log"

# ISBNs and Shopify product IDs extracted from image_replace.log 422 errors.
# Format: (isbn, shopify_product_id)
RETRY_TARGETS = [
    ("9780861549245", "7908669128782"),
    ("9781597073905", "7907132276814"),
    ("9781761560149", "7908353048654"),
    ("9780141984964", "7906534096974"),
    ("9781529922639", "7908201267278"),
    ("9781840915259", "7907505176654"),
    ("9780760381625", "7907722002510"),
    ("9780473415471", "7906608676942"),
    ("9781907155451", "7908499161166"),
    ("9781800653658", "7908361338958"),
    ("9781800654228", "7908681056334"),
    ("9781649634467", "7908954636366"),
    ("9781910218792", "7907968155726"),
    ("9780719844362", "7908604313678"),
    ("9781536222791", "7908179411022"),
    ("9780789327741", "7906729984078"),
    ("9781910593875", "7907615899726"),
    ("9781472132970", "7907870933070"),
    ("9781529032697", "7907089350734"),
    ("9781787300521", "7907401990222"),
    ("9784805317617", "7908052107342"),
    ("9784805315149", "7907712696398"),
    ("9780141396514", "7906531967054"),
    ("9780241567203", "7908162797646"),
    ("9781526642530", "7907971661902"),
    ("9781846977145", "7908797087822"),
    ("9780007165452", "7908424745038"),
    ("9780141991146", "7907876405326"),
    ("9781785038938", "7907352019022"),
    ("9781529109481", "7907101081678"),
    ("9781927305430", "7907666460750"),
    ("9780995121911", "7906822619214"),
    ("9781761380563", "7908039491662"),
    ("9781761211027", "7907943448654"),
    ("9780241243619", "7906560245838"),
    ("9780552577601", "7906635546702"),
    ("9780141992884", "7906536620110"),
    ("9780241446744", "7906571681870"),
    ("9780473628987", "7906623815758"),
    ("9781406383140", "7906890809422"),
    ("9780857527417", "7908620632142"),
    ("9781963183603", "7909007523918"),
    ("9781839768989", "7907989487694"),
    ("9781408716922", "7906905456718"),
    ("9781529075809", "7907095511118"),
    ("9781324030256", "7908734206030"),
    ("9781408720882", "7908912070734"),
    ("9781783788224", "7908071080014"),
    ("9780711268821", "7906666676302"),
    ("9781035061778", "7908697931854"),
    ("9781761521065", "7906600386638"),
    ("9781869409319", "7907541418062"),
    ("9780143566366", "7906545369166"),
    ("9781406392531", "7908792696910"),
    ("9781761471230", "7908494901326"),
    ("9780241303498", "7908094574670"),
    ("9780141985848", "7908542906446"),
    ("9780008509828", "7908959977550"),
    ("9781444939101", "7906958311502"),
    ("9780473547684", "7906616344654"),
    ("9781035039029", "7908371759182"),
    ("9781805332824", "7908916559950"),
    ("9780593581407", "7908286857294"),
    ("9781780894959", "7908051320910"),
    ("9781406394818", "7908637605966"),
    ("9781472272836", "7907002613838"),
    ("9781923049550", "7908480516174"),
    ("9780241741566", "7908494835790"),
    ("9780241674727", "7908314611790"),
    ("9780744531671", "7908463771726"),
    ("9781631069963", "7908246945870"),
    ("9780141987262", "7906534785102"),
    ("9781399725835", "7908101390414"),
    ("9781472129406", "7907721969742"),
    ("9780199576432", "7906558804046"),
    ("9780192884084", "7907959078990"),
    ("9780192786722", "7906557132878"),
    ("9781398701052", "7907920052302"),
    ("9781838930509", "7908367106126"),
    ("9780007236336", "7906325266510"),
    ("8716951380628", "7908987600974"),
    ("9780008664572", "7908871503950"),
    ("9780008681807", "7908469866574"),
    ("9781770850125", "7907244867662"),
    ("9780007492541", "7906481963086"),
    ("9781760526160", "7907185164366"),
    ("9781800921757", "7908722442318"),
    ("9781844489503", "7908043292750"),
    ("9780855329006", "7906747088974"),
    ("9780473689155", "7908291510350"),
    ("9780947492489", "7906774319182"),
    ("9780192803696", "7908870619214"),
    ("9781784877040", "7907349889102"),
    ("9780473729165", "7908602576974"),
    ("9781554073207", "7907116679246"),
    ("9781781577448", "7907336290382"),
    ("9780500285688", "7906628894798"),
    ("9781472263650", "7907001892942"),
    ("9781760761424", "7907199746126"),
    ("9780241711422", "7908533469262"),
    ("9780995117563", "7906805219406"),
    # Connection reset — retry these too
    ("9780008718909", None),
    ("9780500294284", None),
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
log = logging.getLogger(__name__)

DRY_RUN = "--dry-run" in sys.argv


class ShopifyAPI:
    def __init__(self, store_url, token):
        self.base = f"https://{store_url}/admin/api/2024-01"
        self.headers = {
            "X-Shopify-Access-Token": token,
            "Content-Type": "application/json"
        }

    def get_product(self, product_id):
        url = f"{self.base}/products/{product_id}.json"
        r = requests.get(url, headers=self.headers,
                         params={"fields": "id,variants,images"})
        time.sleep(0.6)
        r.raise_for_status()
        return r.json().get("product", {})

    def find_by_sku(self, isbn):
        """Fallback for ISBNs with no known product_id (connection reset ones)."""
        url = f"{self.base}/graphql.json"
        query = """
        {
          productVariants(first: 1, query: "sku:%s") {
            edges { node { product { id legacyResourceId images(first:5) { edges { node { id } } } } } }
          }
        }
        """ % isbn
        r = requests.post(url, headers=self.headers, json={"query": query})
        time.sleep(0.6)
        r.raise_for_status()
        data = r.json()
        edges = data.get("data", {}).get("productVariants", {}).get("edges", [])
        if not edges:
            return None, []
        node = edges[0]["node"]["product"]
        product_id = node["legacyResourceId"]
        image_ids = [e["node"]["id"] for e in node["images"]["edges"]]
        return product_id, image_ids

    def upload_image(self, product_id, b64_data, filename):
        url = f"{self.base}/products/{product_id}/images.json"
        r = requests.post(url, headers=self.headers,
                          json={"image": {"attachment": b64_data, "filename": filename}})
        time.sleep(0.6)
        if not r.ok:
            try:
                body = r.json()
            except Exception:
                body = r.text
            raise ValueError(f"{r.status_code} — Shopify response: {body}")
        return r.json()


def find_image(isbn):
    for folder, label in [
        (LARGE_IMAGE_PATH,  "large"),
        (MEDIUM_IMAGE_PATH, "medium"),
        (CATALOG_PATH,      "catalog"),
    ]:
        path = os.path.join(folder, f"{isbn}.jpg")
        if os.path.exists(path):
            return path, label
    return None, None


def main():
    api = ShopifyAPI(SHOPIFY_STORE_URL, SHOPIFY_ACCESS_TOKEN)

    log.info("=" * 60)
    log.info("BMBooks image retry — 422 error ISBNs")
    log.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(f"Targets: {len(RETRY_TARGETS)}  Dry run: {DRY_RUN}")
    log.info("=" * 60)

    fixed = skipped = failed = 0

    for isbn, product_id in RETRY_TARGETS:
        image_path, source = find_image(isbn)

        if not image_path:
            log.info(f"No image [{isbn}] — no file in LargeImages/MediumImages/catalog")
            skipped += 1
            continue

        file_size = os.path.getsize(image_path)
        log.info(f"Found    [{isbn}] {source} ({file_size:,} bytes)")

        if DRY_RUN:
            continue

        try:
            if product_id is None:
                product_id, _ = api.find_by_sku(isbn)
                if not product_id:
                    log.error(f"NotFound [{isbn}] — product not found in Shopify")
                    failed += 1
                    continue
                log.info(f"Resolved [{isbn}] product_id={product_id}")

            with open(image_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")

            api.upload_image(product_id, b64, f"{isbn}.jpg")
            log.info(f"Fixed    [{isbn}] {source}")
            fixed += 1

        except Exception as e:
            log.error(f"Failed   [{isbn}] {e}")
            failed += 1

    log.info("=" * 60)
    log.info(f"Done — Fixed: {fixed}  Skipped (no image): {skipped}  Failed: {failed}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
