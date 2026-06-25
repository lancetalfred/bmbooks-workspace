#!/bin/bash
# Download cover images for the 20 UAT products from WooCommerce cPanel.
# Strategy: try <ISBN>-1.jpg first (what WooCommerce uses), fall back to <ISBN>.jpg.

BASE_URL="https://bmbooks.co.nz/wp-content/uploads"
OUT_DIR="$(dirname "$0")/images"
mkdir -p "$OUT_DIR"

ISBNS=(
  9781925195941
  9780473656348
  9780001712713
  9780001712812
  9780001713260
  9780006513773
  9780006514831
  9780006543947
  9780006546061
  9780006716778
  9780006716785
  9780006716792
  9780006716808
  9780006716815
  9780006716839
  9780006755135
  9780007107001
  9780008663094
  9780007123742
  9780007137800
)

FOUND=0
MISSING=0

for ISBN in "${ISBNS[@]}"; do
  DEST="$OUT_DIR/${ISBN}.jpg"

  # Skip if already downloaded
  if [ -f "$DEST" ]; then
    echo "  SKIP  $ISBN (already exists)"
    ((FOUND++))
    continue
  fi

  # Try -1 variant first (the one WooCommerce uses as product image)
  URL_1="${BASE_URL}/${ISBN}-1.jpg"
  HTTP=$(curl -s -o "$DEST" -w "%{http_code}" "$URL_1")
  if [ "$HTTP" = "200" ]; then
    SIZE=$(wc -c < "$DEST")
    echo "    OK  $ISBN  (-1 variant, ${SIZE} bytes)"
    ((FOUND++))
    continue
  fi
  rm -f "$DEST"

  # Fall back to original
  URL_0="${BASE_URL}/${ISBN}.jpg"
  HTTP=$(curl -s -o "$DEST" -w "%{http_code}" "$URL_0")
  if [ "$HTTP" = "200" ]; then
    SIZE=$(wc -c < "$DEST")
    echo "    OK  $ISBN  (original, ${SIZE} bytes)"
    ((FOUND++))
    continue
  fi
  rm -f "$DEST"

  echo " MISS  $ISBN  (neither variant found — HTTP $HTTP)"
  ((MISSING++))
done

echo ""
echo "Done: $FOUND downloaded, $MISSING missing."
