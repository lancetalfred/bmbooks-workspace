"""
Usage: python3 check_isbn.py <ISBN>
Prints all Bookscan fields for a given ISBN — use to verify UAT field mapping test cases.
"""
import sys
from dbfread import DBF

if len(sys.argv) < 2:
    print("Usage: python3 check_isbn.py <ISBN>")
    sys.exit(1)

isbn = sys.argv[1].strip()
BASE = "/Users/lalfred/Projects/bmbooks-workspace/Sync/SABSSAVE"

# MASTER.DBF — title, author, price, stock, binding
master = None
for r in DBF(f"{BASE}/MASTER.DBF", ignore_missing_memofile=True):
    if str(r.get("ISBN", "")).strip() == isbn:
        master = r
        break

if not master:
    print(f"ISBN {isbn} not found in MASTER.DBF")
    sys.exit(1)

raw_author = str(master.get("AUTHOR", "")).strip()
raw_binding = str(master.get("BINDING", "")).strip()

BINDING_MAP = {
    "PB": "Paperback", "HB": "Hardback", "TP": "Trade Paperback",
    "BO": "Board Book", "PF": "Picture Flat", "BB": "Big Book",
    "PT": "Picture Trade", "ST": "Stapled", "CD": "CD", "MP": "Map",
    "SP": "Spiral", "BC": "Box Set", "CL": "Calendar", "VI": "Video",
    "BM": "Bookmark", "FC": "Flash Cards", "PS": "Poster", "SI": "Single Item",
}

print(f"ISBN:          {isbn}")
print(f"Title:         {str(master.get('TITLE', '')).strip()}")
print(f"Author (raw):  {raw_author}")
print(f"Author (sync): {raw_author.title()}")
print(f"Price:         {float(master.get('SELL_PRICE') or 0):.2f}")
print(f"Stock:         {int(master.get('ONHAND') or 0)}")
print(f"Binding (raw): {raw_binding}")
print(f"Binding (sync): {BINDING_MAP.get(raw_binding, raw_binding)}")

# PUBLISHER.DBF — publisher, pages, pub date, weight, blurb
pub = None
for r in DBF(f"{BASE}/PUBLISHER.DBF", ignore_missing_memofile=True):
    if str(r.get("ISBN", "")).strip() == isbn:
        pub = r
        break

if pub:
    pub_date = pub.get("PUB_DATE")
    print(f"Publisher:     {str(pub.get('PUBLISHER', '')).strip()}")
    print(f"Pages:         {int(pub.get('PAGES') or 0)}")
    print(f"Pub date:      {pub_date.strftime('%d/%m/%Y') if pub_date else 'None'}")
    print(f"Weight (g):    {float(pub.get('WEIGHT') or 0)}")
    blurb = str(pub.get("BLURB") or "").strip()
    print(f"Blurb:         {blurb[:120] + '...' if len(blurb) > 120 else blurb or '(empty — FPT file not available locally)'}")
else:
    print("Publisher:     (not found in PUBLISHER.DBF)")

# WEBLIST.DBF + category lookups
maincat_map = {r["MAINCAT"]: str(r["CATNAME"]).strip()
               for r in DBF(f"{BASE}/WEBMAINCAT.DBF", ignore_missing_memofile=True)}
subcat_map  = {r["SUBCAT"]: str(r["CATNAME"]).strip()
               for r in DBF(f"{BASE}/WEBSUBCAT.DBF", ignore_missing_memofile=True)}

for r in DBF(f"{BASE}/WEBLIST.DBF", ignore_missing_memofile=True):
    if str(r.get("ISBN", "")).strip() == isbn:
        mc = maincat_map.get(r["MAINCAT"], "")
        sc = subcat_map.get(r["SUBCAT"], "")
        print(f"Tags (sync):   {', '.join(filter(None, [mc, sc]))}")
        break
