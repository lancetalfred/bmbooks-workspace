# ─────────────────────────────────────────────────────────────────────────────
# audit_subcats.py — Sub-category product count audit
#
# Reads WEBLIST, WEBMAINCAT, WEBSUBCAT DBFs and reports product counts
# per sub-category, grouped by parent category. Used to determine which
# sub-categories have enough products to warrant dedicated Shopify collections.
#
# Usage:
#   python audit_subcats.py
#   python audit_subcats.py --min 50    # only show sub-cats with 50+ products
# ─────────────────────────────────────────────────────────────────────────────

import os
import sys
from collections import defaultdict
from dbfread import DBF

# ── DBF paths (mirrors bookscan_sync.py) ──────────────────────────────────────
_SHOP_DBF_PATH  = r"Z:\bookscan"
_LOCAL_DBF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SABSSAVE")
DBF_BASE_PATH   = _SHOP_DBF_PATH if os.path.exists(_SHOP_DBF_PATH) else _LOCAL_DBF_PATH

DBF_WEBLIST_PATH = os.path.join(DBF_BASE_PATH, "WEBLIST.DBF")
DBF_MAINCAT_PATH = os.path.join(DBF_BASE_PATH, "WEBMAINCAT.DBF")
DBF_SUBCAT_PATH  = os.path.join(DBF_BASE_PATH, "WEBSUBCAT.DBF")

# ── Minimum product count to include in output ────────────────────────────────
MIN_PRODUCTS = int(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 1


def load_category_maps():
    maincat_map = {}
    for r in DBF(DBF_MAINCAT_PATH, ignore_missing_memofile=True):
        maincat_map[r["MAINCAT"]] = str(r["CATNAME"]).strip()

    subcat_map = {}
    for r in DBF(DBF_SUBCAT_PATH, ignore_missing_memofile=True):
        subcat_map[r["SUBCAT"]] = str(r["CATNAME"]).strip()

    return maincat_map, subcat_map


def audit():
    maincat_map, subcat_map = load_category_maps()

    # Count products per (maincat_id, subcat_id) from active WEBLIST entries
    counts = defaultdict(int)       # (maincat_id, subcat_id) → product count
    no_subcat = defaultdict(int)    # maincat_id → products with no sub-category
    no_category = 0

    for r in DBF(DBF_WEBLIST_PATH, ignore_missing_memofile=True):
        if r["INACTIVE"]:
            continue
        maincat_id = r["MAINCAT"]
        subcat_id  = r["SUBCAT"]

        if not maincat_id:
            no_category += 1
            continue

        if subcat_id:
            counts[(maincat_id, subcat_id)] += 1
        else:
            no_subcat[maincat_id] += 1

    # ── Output ─────────────────────────────────────────────────────────────────
    print(f"\n{'═'*60}")
    print("  BMBooks Sub-category Audit")
    print(f"  DBF path: {DBF_BASE_PATH}")
    print(f"  Min products filter: {MIN_PRODUCTS}")
    print(f"{'═'*60}\n")

    # Group by parent category, sort by parent name
    by_maincat = defaultdict(list)
    for (maincat_id, subcat_id), count in counts.items():
        maincat_name = maincat_map.get(maincat_id, f"[unknown maincat {maincat_id}]")
        subcat_name  = subcat_map.get(subcat_id,  f"[unknown subcat {subcat_id}]")
        by_maincat[maincat_name].append((subcat_name, count))

    total_subcats = 0
    total_products = 0

    for maincat_name in sorted(by_maincat.keys()):
        subcats = sorted(by_maincat[maincat_name], key=lambda x: -x[1])
        maincat_total = sum(c for _, c in subcats)
        uncategorised = no_subcat.get(
            next((k for k, v in maincat_map.items() if v == maincat_name), None), 0
        )

        eligible = [(name, count) for name, count in subcats if count >= MIN_PRODUCTS]
        if not eligible and uncategorised < MIN_PRODUCTS:
            continue

        print(f"▸ {maincat_name}  ({maincat_total + uncategorised:,} products total)")
        print(f"  {'Sub-category':<40} {'Products':>8}  {'Suggested URL slug'}")
        print(f"  {'─'*40}  {'─'*8}  {'─'*35}")

        for subcat_name, count in subcats:
            if count < MIN_PRODUCTS:
                continue
            slug = subcat_name.lower().replace(" & ", "-").replace(" ", "-").replace("/", "-").replace("'", "")
            print(f"  {subcat_name:<40} {count:>8,}  /collections/{slug}")
            total_subcats += 1
            total_products += count

        if uncategorised:
            print(f"  {'(no sub-category)':<40} {uncategorised:>8,}")
        print()

    print(f"{'─'*60}")
    print(f"  Sub-categories ≥ {MIN_PRODUCTS} products: {total_subcats}")
    print(f"  Products covered:                    {total_products:,}")
    if no_category:
        print(f"  Products with no main category:      {no_category:,}")
    print()


if __name__ == "__main__":
    audit()
