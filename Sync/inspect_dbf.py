# ─────────────────────────────────────────────────────────────────────────────
# inspect_dbf.py — DBF field name inspector
#
# Run this FIRST once we have the DBF files from Louisa.
# It prints every field name and a sample value from each DBF file.
# Use this to confirm the exact field names before running bookscan_sync.py.
#
# Usage:
#   python inspect_dbf.py Z:\bookscan\TITLES.DBF
#   python inspect_dbf.py Z:\bookscan\STOCK.DBF
# ─────────────────────────────────────────────────────────────────────────────

import sys
from dbfread import DBF

def inspect(path):
    print(f"\n{'='*60}")
    print(f"File: {path}")
    print(f"{'='*60}")

    db = DBF(path, encoding="latin-1", ignore_missing_memofile=True)

    print(f"\nField names ({len(db.fields)}):")
    for f in db.fields:
        print(f"  {f.name:<20} type={f.type}  length={f.length}")

    print("\nFirst 3 records:")
    for i, record in enumerate(db):
        if i >= 3:
            break
        print(f"\n  Record {i+1}:")
        for key, value in record.items():
            if key != '_NullFlags':
                print(f"    {key:<20} = {repr(value)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inspect_dbf.py <path_to_dbf>")
        sys.exit(1)
    inspect(sys.argv[1])
