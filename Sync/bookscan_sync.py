# ─────────────────────────────────────────────────────────────────────────────
# BMBooks — Bookscan DBF → Shopify Sync Script
# Reads Bookscan product database and syncs to Shopify Admin API
# Runs on a 1-hour schedule
#
# Usage:
#   python bookscan_sync.py              — delta sync (only changed products)
#   python bookscan_sync.py --full       — full sync (all web-listed products)
#   python bookscan_sync.py --dry-run    — show what would sync, no API calls
#
# DBF files required (from Z:\bookscan on shop machine — mapped drive):
#   MASTER.DBF + MASTER.FPT    — product catalog (title, author, price, stock)
#   PUBLISHER.DBF              — pub details (publisher, pages, date, weight, blurb)
#   WEBLIST.DBF                — web filter (which products are listed on website)
#
# Last updated: June 15, 2026
# ─────────────────────────────────────────────────────────────────────────────

import sys
import os
import time
import base64
import hashlib
import logging
import schedule
import requests
import json
from datetime import datetime
from pathlib import Path
from dbfread import DBF


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# Fill these in before running. Keep this file off GitHub.
# ─────────────────────────────────────────────────────────────────────────────

SHOPIFY_STORE_URL    = os.environ.get("SHOPIFY_STORE_URL", "bruce-mckenzie-booksellers.myshopify.com")
SHOPIFY_ACCESS_TOKEN = os.environ["SHOPIFY_ACCESS_TOKEN"]

# DBF file paths — Z:\bookscan on the shop machine, confirmed via dry-run 2026-05-12.
# Mapped drive — actual location may be a network share or local subfolder.
# The script lives in C:\BookKeeper\ on the shop machine but reads data from Z:\.
# When running locally for testing, falls back to SABSSAVE/ next to this script.
_SHOP_DBF_PATH  = r"\\Server\c\bookscan"
_LOCAL_DBF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SABSSAVE")
DBF_BASE_PATH   = _SHOP_DBF_PATH if os.path.exists(_SHOP_DBF_PATH) else _LOCAL_DBF_PATH
DBF_MASTER_PATH    = os.path.join(DBF_BASE_PATH, "MASTER.DBF")
DBF_PUBLISH_PATH   = os.path.join(DBF_BASE_PATH, "PUBLISHER.DBF")
DBF_WEBLIST_PATH   = os.path.join(DBF_BASE_PATH, "WEBLIST.DBF")
DBF_MAINCAT_PATH   = os.path.join(DBF_BASE_PATH, "WEBMAINCAT.DBF")
DBF_SUBCAT_PATH    = os.path.join(DBF_BASE_PATH, "WEBSUBCAT.DBF")

# Cover image folders — on the shop machine (Z: drive).
# Cascade: LargeImages (257×400) → MediumImages (128×200) → catalog (64×100 thumbnail).
# Set paths to None when running locally for testing.
LARGE_IMAGE_PATH   = r"\\Server\c\bookscan\Catalog\LargeImages"
MEDIUM_IMAGE_PATH  = r"\\Server\c\bookscan\Catalog\MediumImages"
CATALOG_IMAGE_PATH = r"\\Server\c\bookscan\Catalog"

# Cover image fallback — WooCommerce upload directory
# Used when CATALOG_IMAGE_PATH is None or image not found in catalog folder.
# Safe to use until WordPress is shut down. Confirm exact filenames in catalog
# during Chrome Remote Desktop session before switching to catalog-only.
WOOCOMMERCE_IMAGE_BASE = "https://bmbooks.co.nz/wp-content/uploads"  # kept for download_images.sh only

# Placeholder image — shown when no cover art is found in catalog or WooCommerce.
# Point at the local no_cover.jpg for now. Once uploaded to Shopify Files,
# replace with PLACEHOLDER_IMAGE_URL (Shopify CDN URL) instead.
PLACEHOLDER_IMAGE_PATH = None  # no longer needed — using Shopify CDN URL below
PLACEHOLDER_IMAGE_URL  = "https://cdn.shopify.com/s/files/1/0766/8708/1661/files/no_cover.jpg?v=1777572301"

# State file — tracks which products have been synced and their last-known hash.
# Enables delta sync: only changed products are pushed on subsequent runs.
_BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(_BASE_DIR, "sync_state.json")

# CSTATUS codes that should never sync — expanded to full NOWEB=True set.
# Confirmed by Louisa 2026-06-08: follow Bookscan's own NOWEB flag.
# Original 3 (OP/RP/RUC) plus all remaining NOWEB=True codes from status table.
STATUS_EXCLUDE = {
    "OP",   # Out of Print
    "RP",   # Reprinting
    "RUC",  # Reprint Under Consideration
    "OSI",  # Out of Stock Indefinitely
    "NOR",  # No Rights in NZ
    "PBA",  # Publication Abandoned
    "ASC",  # Awaiting Supplier Confirm
    "NLA",  # No Longer Available
    "PBD",  # Publication Delayed
    "PDR",  # Publisher Cannot Be Found
    "ORD",  # Order Direct
    "NLD",  # No Longer Distributed NZ
    "PUA",  # Publication Cancelled
    "CHP",  # Check Price Each Time
    "OLD",  # Old Edition — New Available
    "INT",  # Internet Only Purchase
    "NOT",  # No Listing Found
    "WFC",  # Waiting for Confirmation
    "AD",   # Not To Web (explicit NOWEB flag)
}

# Department codes to never sync — confirmed with Louisa 2026-06-08.
# TOK and VOU removed from exclude — industry book tokens and vouchers to show on site.
DEPARTMENT_EXCLUDE = {
    "AAA",  # Dept To Be Assigned (uncategorised)
    "FRE",  # Freight (Shopify handles at checkout)
    "GFS",  # Gifts - non web (Louisa: "doesn't go on website")
    "SPE",  # Specials
    "XXX",  # Unnamed/default Bookscan code
    "MAG",  # Magazines (old unused code)
    "AUD",  # Audio
    "CDS",  # CDs / musical recordings
    "EXP",  # Expenses
    "FUN",  # Fun
    "KIT",  # Kit
    "MON",  # Mon
    "POS",  # POS
    "STK",  # Stocktake
    "YOG",  # Yoga (no longer used)
    "",     # Blank dept (no department set)
}

# When True: new products with price > 0 are published (Active) immediately on create.
# Also auto-publishes when a zero-price draft gets a price on the next sync.
# Keep False before go-live bulk-activate. Flip to True after bulk-activate is done.
AUTO_PUBLISH = True

# Sync settings
SYNC_INTERVAL_HOURS = 1
LOG_FILE            = os.path.join(_BASE_DIR, "bookscan_sync.log")
DRY_RUN             = "--dry-run" in sys.argv
FULL_SYNC           = "--full"    in sys.argv
ONCE                = "--once"    in sys.argv
MAX_PRODUCTS        = None   # limit for testing — set to None for full production sync
ISBN_FILTER         = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--isbn=")), None)
LOCK_FILE           = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sync.lock")


# ─────────────────────────────────────────────────────────────────────────────
# BINDING CODE → HUMAN READABLE
# Confirmed from MASTER.DBF inspection (April 2026)
# ─────────────────────────────────────────────────────────────────────────────

BINDING_MAP = {
    "PB": "Paperback",
    "HB": "Hardback",
    "TP": "Trade Paperback",
    "BO": "Boxed",
    "PF": "Picture Flat",
    "BB": "Board Book",
    "PT": "Picture Trade",
    "ST": "Stapled",
    "CD": "CD",
    "MP": "Map",
    "SP": "Spiral",
    "BC": "Box Set",
    "CL": "Calendar",
    "VI": "Video",
    "BM": "Bookmark",
    "FC": "Flash Cards",
    "PS": "Poster",
    "SI": "Single Item",
    "TY": "Toy/Plush",
    "VO": "Voucher",
    "**": "Token",
}


# ─────────────────────────────────────────────────────────────────────────────
# NOTIFICATIONS
# ─────────────────────────────────────────────────────────────────────────────

def _notify(title, message):
    """Send a Windows toast notification. Silent no-op on non-Windows or if winotify is absent."""
    try:
        from winotify import Notification
        icon = os.path.join(_BASE_DIR, "bookkeeper.ico")
        toast = Notification(
            app_id="BookKeeper",
            title=title,
            msg=message,
            icon=icon if os.path.exists(icon) else "",
        )
        toast.show()
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# SHOPIFY API
# ─────────────────────────────────────────────────────────────────────────────

class ShopifyAPI:
    """Thin wrapper around Shopify Admin REST API."""

    def __init__(self, store_url, access_token):
        self.base = f"https://{store_url}/admin/api/2024-01"
        self.headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }

    def _request(self, method, endpoint, data=None):
        url = f"{self.base}/{endpoint}"
        response = requests.request(method, url, headers=self.headers, json=data)
        time.sleep(0.6)   # ~1.6 req/sec — safely under Shopify Basic plan limit
        response.raise_for_status()
        return response.json()

    def _graphql(self, query, variables=None):
        """Send a GraphQL admin API request. Raises on transport or GraphQL errors."""
        url = f"{self.base}/graphql.json"
        payload = {"query": query, "variables": variables or {}}
        response = requests.post(url, headers=self.headers, json=payload)
        time.sleep(0.6)
        response.raise_for_status()
        result = response.json()
        if "errors" in result:
            raise RuntimeError(f"GraphQL error: {result['errors']}")
        return result

    def get_location_id(self):
        result = self._request("GET", "locations.json")
        return result["locations"][0]["id"]

    def find_by_sku(self, sku):
        """
        Look up a Shopify product variant by exact SKU using GraphQL.
        Returns (product_id, variant_id, inventory_item_id) or None.

        GraphQL's `query:` argument filters server-side reliably. The previous
        REST /variants.json?sku= approach didn't actually filter on the server —
        it returned a page of most-recent variants and filtered locally, which
        silently missed older products in stores with >50 variants and caused
        duplicate-product creation on every full-sync restart.
        """
        query = """
        query findBySku($q: String!) {
          productVariants(first: 1, query: $q) {
            edges {
              node {
                id
                product { id }
                inventoryItem { id }
              }
            }
          }
        }
        """
        result = self._graphql(query, {"q": f'sku:"{sku}"'})
        edges = result.get("data", {}).get("productVariants", {}).get("edges", [])
        if not edges:
            return None
        node = edges[0]["node"]
        # GraphQL IDs come as "gid://shopify/ProductVariant/1234" — REST endpoints need the numeric portion
        variant_id        = int(node["id"].rsplit("/", 1)[-1])
        product_id        = int(node["product"]["id"].rsplit("/", 1)[-1])
        inventory_item_id = int(node["inventoryItem"]["id"].rsplit("/", 1)[-1])
        return product_id, variant_id, inventory_item_id

    def create_product(self, product_data):
        result = self._request("POST", "products.json", {"product": product_data})
        return result["product"]

    def update_product(self, product_id, product_data):
        result = self._request("PUT", f"products/{product_id}.json", {"product": product_data})
        return result["product"]

    def get_product_tags(self, product_id):
        """Return current tags for a product as a list."""
        result = self._request("GET", f"products/{product_id}.json?fields=tags")
        raw = result.get("product", {}).get("tags", "")
        return [t.strip() for t in raw.split(",") if t.strip()]

    def set_inventory(self, inventory_item_id, location_id, quantity):
        """
        Set on-hand stock level via GraphQL inventorySetOnHandQuantities.

        REST /inventory_levels/set.json and /connect.json both return 404 on
        this store (BMBooks live, 2026-05-12) despite the inventory item and
        location both existing. GraphQL inventory mutations work reliably.

        If the inventory item isn't yet active at the location, the mutation
        returns a userError; we then call inventoryActivate and retry.
        """
        location_gid       = f"gid://shopify/Location/{location_id}"
        inventory_item_gid = f"gid://shopify/InventoryItem/{inventory_item_id}"

        set_mutation = """
        mutation setOnHand($input: InventorySetOnHandQuantitiesInput!) {
          inventorySetOnHandQuantities(input: $input) {
            userErrors { field message }
          }
        }
        """
        set_variables = {
            "input": {
                "reason": "correction",
                "setQuantities": [{
                    "inventoryItemId": inventory_item_gid,
                    "locationId":      location_gid,
                    "quantity":        quantity
                }]
            }
        }

        def _try_set():
            result = self._graphql(set_mutation, set_variables)
            return result.get("data", {}).get("inventorySetOnHandQuantities", {}).get("userErrors", [])

        errors = _try_set()
        if not errors:
            return

        # If inventory item isn't stocked/active at this location, activate then retry
        needs_activate = any(
            kw in (e.get("message") or "").lower()
            for e in errors
            for kw in ("not stocked", "not active", "activate", "tracked")
        )
        if not needs_activate:
            raise RuntimeError(f"inventorySetOnHandQuantities errors: {errors}")

        activate_mutation = """
        mutation activate($inventoryItemId: ID!, $locationId: ID!) {
          inventoryActivate(inventoryItemId: $inventoryItemId, locationId: $locationId) {
            userErrors { field message }
          }
        }
        """
        self._graphql(activate_mutation, {
            "inventoryItemId": inventory_item_gid,
            "locationId":      location_gid
        })

        errors = _try_set()
        if errors:
            raise RuntimeError(f"inventorySetOnHandQuantities errors after activate: {errors}")


# ─────────────────────────────────────────────────────────────────────────────
# COVER IMAGE RESOLUTION
# ─────────────────────────────────────────────────────────────────────────────

def resolve_image(isbn):
    """
    Return (image_dict, source_label) for this ISBN, or (None, None).

    Resolution order:
      1. LargeImages\ (257×400) — highest res, near-full catalog coverage.
      2. MediumImages\ (128×200) — fallback for titles missing from LargeImages.
      3. catalog\ (64×100) — original thumbnail folder populated by Ebility.
      4. Placeholder (Shopify CDN) — no_cover.jpg for books with no local image.
    """
    folders = [
        (LARGE_IMAGE_PATH,   "LargeImages"),
        (MEDIUM_IMAGE_PATH,  "MediumImages"),
        (CATALOG_IMAGE_PATH, "catalog"),
    ]
    for folder, label in folders:
        if folder:
            path = os.path.join(folder, f"{isbn}.jpg")
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return (
                        {"attachment": base64.b64encode(f.read()).decode("utf-8"), "filename": f"{isbn}.jpg"},
                        label,
                    )

    if PLACEHOLDER_IMAGE_URL:
        return {"src": PLACEHOLDER_IMAGE_URL}, "placeholder"
    if PLACEHOLDER_IMAGE_PATH and os.path.exists(PLACEHOLDER_IMAGE_PATH):
        with open(PLACEHOLDER_IMAGE_PATH, "rb") as f:
            return {"attachment": base64.b64encode(f.read()).decode("utf-8")}, "placeholder"

    return None, None


# ─────────────────────────────────────────────────────────────────────────────
# STATE FILE — delta sync tracking
# ─────────────────────────────────────────────────────────────────────────────

def load_state():
    """Load sync state from disk. Returns dict with 'hashes', 'fields', 'last_run', and 'bookscan_tags'."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
        data.setdefault("fields", {})
        data.setdefault("bookscan_tags", {})
        return data
    return {"last_run": None, "hashes": {}, "fields": {}, "bookscan_tags": {}}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def _field_snapshot(p):
    """Return the subset of product fields used for diffing."""
    return {
        "title":         p.get("title", ""),
        "author":        p.get("author", ""),
        "publisher":     p.get("publisher", ""),
        "price":         p.get("price", 0),
        "stock":         p.get("stock", 0),
        "binding":       p.get("binding", ""),
        "pages":         p.get("pages", 0),
        "dim_length":    p.get("dim_length", ""),
        "dim_width":     p.get("dim_width", ""),
        "dim_thickness": p.get("dim_thickness", ""),
        "tags":          ",".join(p.get("tags", [])),
    }


def _format_diff(prev, curr):
    """Return a pipe-separated string of fields that changed, with before → after values."""
    LABELS = {
        "title": "Title", "author": "Author", "publisher": "Publisher",
        "price": "Price", "stock": "Stock", "binding": "Binding",
        "pages": "Pages", "dim_length": "Length", "dim_width": "Width",
        "dim_thickness": "Thickness", "tags": "Tags",
    }
    parts = []
    for key, label in LABELS.items():
        old = prev.get(key, "")
        new = curr.get(key, "")
        if str(old) != str(new):
            old_fmt = f"${old:.2f}" if key == "price" and isinstance(old, float) else old
            new_fmt = f"${new:.2f}" if key == "price" and isinstance(new, float) else new
            parts.append(f"{label}: {old_fmt} → {new_fmt}")
    return " | ".join(parts) if parts else "no field changes detected"


def _format_created_detail(p):
    """Return a pipe-separated summary of all key fields for a newly created product."""
    parts = []
    if p.get("author"):    parts.append(f"Author: {p['author']}")
    if p.get("publisher"): parts.append(f"Publisher: {p['publisher']}")
    if p.get("binding"):   parts.append(f"Binding: {p['binding']}")
    parts.append(f"Price: ${p.get('price', 0):.2f}")
    parts.append(f"Stock: {p.get('stock', 0)}")
    if p.get("pages"):     parts.append(f"Pages: {p['pages']}")
    return " | ".join(parts)


def _check_warnings(p):
    """Return a list of data quality issues for this product."""
    issues = []
    if p.get("price", 0) == 0:
        issues.append("No price — synced as Draft")
    if not p.get("author", "").strip():
        issues.append("Missing author")
    bc = p.get("binding_code", "")
    if bc and bc not in BINDING_MAP:
        issues.append(f"Unknown binding: {bc}")
    return issues


def product_hash(p):
    """
    Compute a hash of the fields we care about for change detection.
    If any of these change in Bookscan, we push an update to Shopify.
    """
    key = "|".join([
        p.get("title",     ""),
        p.get("author",    ""),
        p.get("publisher", ""),
        str(p.get("price",  0)),
        str(p.get("stock",  0)),
        p.get("binding",   ""),
        str(p.get("pages",  0)),
        p.get("dim_length",    ""),
        p.get("dim_width",     ""),
        p.get("dim_thickness", ""),
        ",".join(p.get("tags", [])),
    ])
    return hashlib.md5(key.encode()).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# BOOKSCAN READER
# Reads MASTER.DBF, PUBLISHER.DBF, and WEBLIST.DBF
# Joins on ISBN to build a complete product record
# ─────────────────────────────────────────────────────────────────────────────

def load_publisher_map():
    """
    Load PUBLISHER.DBF into a dict keyed by stripped ISBN.
    PUBLISHER.DBF holds: publisher name, pages, publication date,
    weight, dimensions, and blurb.
    """
    log.info(f"Loading publisher data from {DBF_PUBLISH_PATH}")
    pub_map = {}
    for r in DBF(DBF_PUBLISH_PATH, ignore_missing_memofile=True):
        isbn = str(r["ISBN"]).strip()
        if isbn:
            pub_map[isbn] = r
    log.info(f"  {len(pub_map):,} publisher records loaded")
    return pub_map


def load_category_maps():
    """
    Load WEBMAINCAT.DBF and WEBSUBCAT.DBF into lookup dicts.
    Returns (maincat_map, subcat_map) keyed by numeric category ID.
    e.g. maincat_map[1] = "Fiction", subcat_map[2] = "Crime Fiction"
    """
    maincat_map = {}
    for r in DBF(DBF_MAINCAT_PATH, ignore_missing_memofile=True):
        maincat_map[r["MAINCAT"]] = str(r["CATNAME"]).strip()

    subcat_map = {}
    for r in DBF(DBF_SUBCAT_PATH, ignore_missing_memofile=True):
        subcat_map[r["SUBCAT"]] = str(r["CATNAME"]).strip()

    return maincat_map, subcat_map


def load_weblist():
    """
    Load WEBLIST.DBF — the list of ISBNs that Bookscan exports to the website.
    Returns a dict of {isbn: (maincat_id, subcat_id)} where INACTIVE is False.
    """
    log.info(f"Loading web list from {DBF_WEBLIST_PATH}")
    web_isbns = {}
    for r in DBF(DBF_WEBLIST_PATH, ignore_missing_memofile=True):
        isbn = str(r["ISBN"]).strip()
        if isbn and not r["INACTIVE"]:
            web_isbns[isbn] = (r["MAINCAT"], r["SUBCAT"])
    log.info(f"  {len(web_isbns):,} active web ISBNs")
    return web_isbns


def _format_dimension(value, unit):
    """Format a dimension value with its unit. Returns empty string if zero/None."""
    v = float(value or 0)
    if v == 0:
        return ""
    u = str(unit or "").strip().lower()
    return f"{v:.0f} {u}".strip() if u else f"{v:.0f}"


def _format_author(raw):
    """
    Bookscan stores authors as "LASTNAME FIRSTNAME" (all caps, single space).
    Convert to "Firstname Lastname" for display.
    Single-word names (e.g. "ANONYMOUS") are returned as-is after title-casing.
    Names with commas (e.g. "WELLS, MARTHA") are handled as an alternative delimiter.
    """
    if not raw:
        return ""
    # Handle comma-separated "LAST, FIRST" format if present
    if "," in raw:
        parts = [p.strip().title() for p in raw.split(",", 1)]
        return f"{parts[1]} {parts[0]}".strip() if len(parts) == 2 else raw.title()
    # Default: space-separated "LAST FIRST" — split on last space to handle "DE VRIES JAN"
    parts = raw.split()
    if len(parts) == 1:
        return parts[0].title()
    # Last token is first name; everything before is the last name
    first = parts[-1].title()
    last  = " ".join(p.title() for p in parts[:-1])
    return f"{first} {last}"


def read_products():
    """
    Read all web-listed products from MASTER.DBF, joined with PUBLISHER.DBF.
    Only includes ISBNs present in WEBLIST with INACTIVE=False.
    Returns a list of normalised product dicts.
    """
    pub_map          = load_publisher_map()
    web_isbns        = load_weblist()        # {isbn: (maincat_id, subcat_id)}
    maincat_map, subcat_map = load_category_maps()

    log.info(f"Reading products from {DBF_MASTER_PATH}")
    products = []
    status_skipped = 0
    dept_skipped = 0

    for r in DBF(DBF_MASTER_PATH, ignore_missing_memofile=True):
        isbn = str(r["ISBN"]).strip()

        # Only sync products listed on the website
        if isbn not in web_isbns:
            continue

        cstatus = (r.get("CSTATUS") or "").strip()
        if cstatus in STATUS_EXCLUDE:
            status_skipped += 1
            continue

        department = (r.get("DEPARTMENT") or "").strip()
        if department in DEPARTMENT_EXCLUDE:
            dept_skipped += 1
            continue

        title = str(r["TITLE"]).strip()
        if not title or not isbn:
            continue

        # Pull enriched fields from PUBLISHER.DBF
        pub = pub_map.get(isbn, {})

        # Description: prefer PUBLISHER.BLURB, fall back to MASTER.MTABSTRACT
        blurb = pub.get("BLURB") or r.get("MTABSTRACT")
        description = str(blurb).strip() if blurb else ""

        # Publication date: PUBLISHER.PUB_DATE is a proper date object
        pub_date = pub.get("PUB_DATE")
        pub_date_str = pub_date.strftime("%d/%m/%Y") if pub_date else ""

        # Publisher name from PUBLISHER.DBF
        publisher = str(pub.get("PUBLISHER") or "").strip()

        # Pages: PUBLISHER tends to have better data than MASTER
        pages = int(pub.get("PAGES") or 0)
        if pages == 0:
            pages = int(r.get("PAGES") or 0)

        # Weight in grams from PUBLISHER.DBF
        weight_g = float(pub.get("WEIGHT") or 0)

        # Dimensions from PUBLISHER.DBF (LENGTH/WIDTH/THICKNESS + unit fields)
        dim_length    = _format_dimension(pub.get("LENGTH"),    pub.get("LMEASURE"))
        dim_width     = _format_dimension(pub.get("WIDTH"),     pub.get("WMEASURE"))
        dim_thickness = _format_dimension(pub.get("THICKNESS"), pub.get("TMEASURE"))

        # Binding: map 2-char code to human-readable label
        binding_code = str(r.get("BINDING") or "").strip()
        binding = BINDING_MAP.get(binding_code, binding_code)

        # Category tags from WEBLIST → WEBMAINCAT / WEBSUBCAT
        maincat_id, subcat_id = web_isbns[isbn]
        tags = []
        if maincat_id and maincat_id in maincat_map:
            tags.append(maincat_map[maincat_id])
        if subcat_id and subcat_id in subcat_map:
            tags.append(subcat_map[subcat_id])

        # Hidden Bookscan metadata tags — `_` prefix is suppressed from customer-facing
        # display by most themes (including Horizon), but remain searchable and
        # filterable in the Shopify admin product list. Lets Louisa point-and-click
        # filter by status/department for post-launch cleanup without exposing
        # internal codes to shoppers.
        if cstatus:
            tags.append(f"_cstatus-{cstatus}")
        if department:
            tags.append(f"_dept-{department}")

        products.append({
            "isbn":         isbn,
            "title":        title,
            "author":       _format_author(str(r["AUTHOR"]).strip()),
            "price":        float(r.get("SELL_PRICE") or 0),
            "stock":        int(r.get("ONHAND") or 0),
            "binding":      binding,
            "binding_code": binding_code,
            "publisher":    publisher,
            "pub_date":   pub_date_str,
            "pages":      pages,
            "weight_g":     weight_g,
            "dim_length":   dim_length,
            "dim_width":    dim_width,
            "dim_thickness": dim_thickness,
            "body_html":  description,
            "tags":       tags,
            "cstatus":    cstatus,
            "department": department,
        })

    log.info(f"  {len(products):,} web products read")
    if status_skipped:
        log.info(f"  {status_skipped:,} skipped via CSTATUS exclude ({', '.join(sorted(STATUS_EXCLUDE))})")
    if dept_skipped:
        log.info(f"  {dept_skipped:,} skipped via DEPARTMENT exclude ({', '.join(sorted(DEPARTMENT_EXCLUDE))})")

    # Deduplicate by ISBN — Bookscan occasionally has 2–3 records for the same ISBN
    # (slightly different titles, one with real stock, one with None).
    # Keep the record with the highest stock value; break ties by preferring non-zero price.
    seen = {}
    for p in products:
        key = p["isbn"]
        if key not in seen:
            seen[key] = p
        else:
            existing = seen[key]
            # Prefer real stock over None/0
            if p["stock"] > existing["stock"]:
                seen[key] = p
            # Same stock — prefer non-zero price
            elif p["stock"] == existing["stock"] and p["price"] > existing["price"]:
                seen[key] = p

    deduped = list(seen.values())
    if len(deduped) < len(products):
        log.info(f"  Deduped {len(products) - len(deduped)} duplicate ISBN record(s) -> {len(deduped):,} unique products")

    return deduped


# ─────────────────────────────────────────────────────────────────────────────
# FIELD MAPPING — Bookscan product dict → Shopify product payload
# ─────────────────────────────────────────────────────────────────────────────

def _merge_tags(new_bookscan_tags, prev_bookscan_tags, current_shopify_tags, is_new):
    """
    Merge Bookscan-generated tags with any externally-added tags on the Shopify product.

    Strategy: tags previously set by Bookscan are tracked in sync state. On update,
    remove those tracked tags from the current Shopify set, then add the new Bookscan
    tags. Any tag not in the previous Bookscan set (e.g. 'Romance' added by the genre
    enrichment script) is treated as external and preserved.

    New products get only the Bookscan tags — no prior Shopify state to merge with.
    """
    if is_new or not current_shopify_tags:
        return new_bookscan_tags
    prev_managed = set(prev_bookscan_tags or [])
    preserved = [t for t in current_shopify_tags if t not in prev_managed]
    return preserved + new_bookscan_tags


def to_shopify_product(p, image=None, is_new=False, variant_id=None, prev_bookscan_tags=None, current_shopify_tags=None, force_status=None):
    metafields = [
        {
            "namespace": "bookscan",
            "key":       "isbn",
            "value":     p["isbn"],
            "type":      "single_line_text_field"
        },
    ]

    if p["author"]:
        metafields.append({
            "namespace": "bookscan",
            "key":       "author",
            "value":     p["author"],
            "type":      "single_line_text_field"
        })

    if p["pages"]:
        metafields.append({
            "namespace": "bookscan",
            "key":       "pages",
            "value":     str(p["pages"]),
            "type":      "single_line_text_field"
        })

    if p["pub_date"]:
        metafields.append({
            "namespace": "bookscan",
            "key":       "publication_date",
            "value":     p["pub_date"],
            "type":      "single_line_text_field"
        })

    for dim_key, dim_val in [("length", p.get("dim_length")), ("width", p.get("dim_width")), ("depth", p.get("dim_thickness"))]:
        if dim_val:
            metafields.append({
                "namespace": "bookscan",
                "key":       dim_key,
                "value":     dim_val,
                "type":      "single_line_text_field"
            })

    if p.get("cstatus"):
        metafields.append({
            "namespace": "bookscan",
            "key":       "cstatus",
            "value":     p["cstatus"],
            "type":      "single_line_text_field"
        })

    if p.get("department"):
        metafields.append({
            "namespace": "bookscan",
            "key":       "department",
            "value":     p["department"],
            "type":      "single_line_text_field"
        })

    payload = {
        "title":        p["title"],
        "vendor":       p["publisher"],
        "product_type": p["binding"],
        "body_html":    p["body_html"],
        "tags":         ", ".join(_merge_tags(p["tags"], prev_bookscan_tags, current_shopify_tags, is_new)),
        "published_scope": "web",            # publish to Online Store (not POS-only)
        "variants": [{
            **({"id": variant_id} if variant_id else {}),
            "sku":                  p["isbn"],
            "price":                f"{p['price']:.2f}",
            "inventory_management": "shopify",
            "inventory_quantity":   p["stock"],
            "inventory_policy":     "continue",   # "Available to order" when stock = 0
            "weight":               p["weight_g"],
            "weight_unit":          "g",
            "requires_shipping":    True,
            "taxable":              True,
        }],
        "metafields": metafields,
    }

    if force_status:
        payload["status"] = force_status          # zero-price hide or 0→>0 auto-publish
    elif is_new:
        payload["status"] = "active" if (AUTO_PUBLISH and p["price"] > 0) else "draft"

    if image:
        payload["images"] = [image]

    return payload


# ─────────────────────────────────────────────────────────────────────────────
# SYNC JOB
# ─────────────────────────────────────────────────────────────────────────────

def run_sync():
    Path(LOCK_FILE).touch()
    try:
        _run_sync_inner()
    finally:
        Path(LOCK_FILE).unlink(missing_ok=True)


def _run_sync_inner():
    log.info("=" * 60)
    log.info(f"BMBooks Bookscan -> Shopify sync")
    log.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    mode_label = "DRY RUN — " if DRY_RUN else ""
    sync_label = "FULL sync" if FULL_SYNC else "delta sync"
    log.info(f"Mode: {mode_label}{sync_label}")
    log.info("=" * 60)

    if DRY_RUN:
        log.info("DRY RUN — no Shopify API calls will be made")

    _notify("BookKeeper", f"Sync started — {'full sync' if FULL_SYNC else 'delta sync'}")

    state = load_state()
    prev_hashes       = state.get("hashes", {})
    prev_fields       = state.get("fields", {})
    prev_bookscan_tags = state.get("bookscan_tags", {})

    products = read_products()

    # ISBN filter: --isbn=<isbn> restricts sync to a single product (useful for dry-run inspection)
    if ISBN_FILTER:
        products = [p for p in products if p["isbn"] == ISBN_FILTER]
        if not products:
            log.warning(f"ISBN filter: {ISBN_FILTER} not found in web-listed products")
            return
        log.info(f"ISBN filter: {ISBN_FILTER} — {len(products)} product")

    # Delta filter: skip products whose key fields haven't changed since last run
    if not FULL_SYNC and prev_hashes:
        to_process = []
        skipped = 0
        for p in products:
            h = product_hash(p)
            if prev_hashes.get(p["isbn"]) != h:
                to_process.append(p)
            else:
                skipped += 1
        log.info(f"Delta: {len(to_process):,} changed, {skipped:,} unchanged — skipping unchanged")
    else:
        to_process = products
        log.info(f"Processing all {len(to_process):,} products")

    # Apply MAX_PRODUCTS cap (for testing — set to None for full production sync)
    # When capping, sort so standard book ISBNs (978/979) come first — better test data
    if MAX_PRODUCTS and len(to_process) > MAX_PRODUCTS:
        to_process.sort(key=lambda p: (0 if p["isbn"].startswith(("978", "979")) else 1))
        log.info(f"MAX_PRODUCTS={MAX_PRODUCTS} — capping to first {MAX_PRODUCTS} products (remove cap for full sync)")
        to_process = to_process[:MAX_PRODUCTS]

    if DRY_RUN:
        if ISBN_FILTER and len(to_process) == 1:
            p = to_process[0]
            log.info(f"DRY RUN — full detail for {ISBN_FILTER}:")
            log.info(f"  Title:     {p['title']}")
            log.info(f"  Author:    {p['author']}")
            log.info(f"  Publisher: {p['publisher']}")
            log.info(f"  Binding:   {p['binding']}")
            log.info(f"  Price:     ${p['price']:.2f}")
            log.info(f"  Stock:     {p['stock']}")
            log.info(f"  Pages:     {p['pages']}")
            log.info(f"  Pub date:  {p['pub_date']}")
            log.info(f"  Weight:    {p['weight_g']}g")
            log.info(f"  Length:    {p.get('dim_length') or '—'}")
            log.info(f"  Width:     {p.get('dim_width') or '—'}")
            log.info(f"  Thickness: {p.get('dim_thickness') or '—'}")
            log.info(f"  Tags:      {', '.join(p['tags'])}")
            log.info(f"  Hash:      {product_hash(p)}")
            prev_hash = prev_hashes.get(p['isbn'])
            if prev_hash == product_hash(p):
                log.info(f"  Status:    UNCHANGED (would be skipped in delta sync)")
            else:
                log.info(f"  Status:    CHANGED — would {'create' if not prev_hash else 'update'}")
        else:
            log.info(f"DRY RUN — showing first {min(20, len(to_process))} products that would be synced:")
            for p in to_process[:20]:
                log.info(f"  [{p['isbn']}] {p['title']} — ${p['price']:.2f} — stock: {p['stock']}")
            if len(to_process) > 20:
                log.info(f"  ... and {len(to_process) - 20} more")
        log.info("Set DRY_RUN = False (or remove --dry-run) to push to Shopify")
        return

    shopify     = ShopifyAPI(SHOPIFY_STORE_URL, SHOPIFY_ACCESS_TOKEN)
    location_id = shopify.get_location_id()

    created = updated = errors = warnings = 0
    warning_list = []
    error_list   = []
    updated_list = []
    created_list = []
    new_hashes        = dict(prev_hashes)       # carry forward unchanged hashes
    new_fields        = dict(prev_fields)        # carry forward unchanged field snapshots
    new_bookscan_tags = dict(prev_bookscan_tags) # carry forward unchanged bookscan tag records

    for i, p in enumerate(to_process, 1):
        isbn = p["isbn"]

        if i % 100 == 0:
            log.info(f"  Progress: {i}/{len(to_process)} — Created: {created}  Updated: {updated}  Warnings: {warnings}  Errors: {errors}")
            save_state({"last_run": datetime.now().isoformat(), "hashes": new_hashes, "fields": new_fields, "bookscan_tags": new_bookscan_tags})

        try:
            existing = shopify.find_by_sku(isbn)

            # Determine status override for this product
            prev_price = prev_fields.get(isbn, {}).get("price", -1)
            if p["price"] == 0:
                force_status = "draft"                    # always hide zero-price products
            elif AUTO_PUBLISH and existing and prev_price == 0 and p["price"] > 0:
                force_status = "active"                   # was zero-price draft, now priced → publish
            else:
                force_status = None                       # preserve existing Shopify status

            if existing:
                product_id, variant_id, inv_item_id = existing
                current_tags = shopify.get_product_tags(product_id)
                shopify.update_product(product_id, to_shopify_product(
                    p, is_new=False, variant_id=variant_id,
                    prev_bookscan_tags=prev_bookscan_tags.get(isbn, []),
                    current_shopify_tags=current_tags,
                    force_status=force_status,
                ))
                new_bookscan_tags[isbn] = p["tags"]
                updated += 1
                log.info(f"Updated  [{isbn}] {p['title']}")
                diff = _format_diff(prev_fields.get(isbn, {}), _field_snapshot(p))
                log.info(f"DETAIL_U [{isbn}] {diff}")
                updated_list.append([isbn, p["title"], diff])
                # Update inventory separately on existing products
                try:
                    shopify.set_inventory(inv_item_id, location_id, p["stock"])
                except Exception as inv_e:
                    log.warning(f"  Inventory update non-fatal: {inv_e}")
            else:
                image, img_source = resolve_image(isbn)
                log.info(f"  Image   [{isbn}] {img_source or 'not found'}")
                shopify.create_product(to_shopify_product(p, image=image, is_new=True, force_status=force_status))
                new_bookscan_tags[isbn] = p["tags"]
                created += 1
                log.info(f"Created  [{isbn}] {p['title']}")
                detail = _format_created_detail(p)
                log.info(f"DETAIL_C [{isbn}] {detail}")
                created_list.append([isbn, p["title"], detail])

            # Data quality warnings
            issues = _check_warnings(p)
            if issues:
                log.info(f"WARN     [{isbn}] {p['title']} ||| {' | '.join(issues)}")
                warnings += 1
                warning_list.append([isbn, p["title"], " | ".join(issues)])

            # Record hash and field snapshot so next run can detect changes and diff them
            new_hashes[isbn] = product_hash(p)
            new_fields[isbn] = _field_snapshot(p)

        except Exception as e:
            log.error(f"Error    [{isbn}] {p['title']} — {e}")
            errors += 1
            error_list.append([isbn, p["title"], str(e)])

    # Persist state
    save_state({
        "last_run":      datetime.now().isoformat(),
        "hashes":        new_hashes,
        "fields":        new_fields,
        "bookscan_tags": new_bookscan_tags,
    })

    log.info("=" * 60)
    log.info(f"Sync complete — Created: {created}  Updated: {updated}  Warnings: {warnings}  Errors: {errors}")
    if not ONCE:
        log.info(f"Next run in {SYNC_INTERVAL_HOURS} hours")
    log.info("=" * 60)

    summary_path = os.path.join(_BASE_DIR, "last_run_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "completed":     datetime.now().strftime("%Y-%m-%d %H:%M"),
            "created":       created,
            "updated":       updated,
            "errors":        errors,
            "warnings":      warnings,
            "created_items": created_list,
            "updated_items": updated_list,
            "warning_items": warning_list,
            "error_items":   error_list,
        }, f, indent=2, ensure_ascii=False)

    if errors > 0:
        _notify("BookKeeper ⚠", f"Sync finished with {errors} error(s) — open BookKeeper to review")
    elif warnings > 0:
        _notify("BookKeeper ⚠", f"Sync complete — {warnings} data warning(s) — open BookKeeper to review")
    else:
        _notify("BookKeeper", f"Sync complete — Created: {created}  Updated: {updated}  Errors: 0")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if ONCE:
        run_sync()
    else:
        log.info("BMBooks Bookscan -> Shopify sync service starting")
        log.info(f"Store:    {SHOPIFY_STORE_URL}")
        log.info(f"Interval: every {SYNC_INTERVAL_HOURS} hours")

        # Run immediately on startup, then every 2 hours
        run_sync()
        schedule.every(SYNC_INTERVAL_HOURS).hours.do(run_sync)

        while True:
            schedule.run_pending()
            time.sleep(60)
