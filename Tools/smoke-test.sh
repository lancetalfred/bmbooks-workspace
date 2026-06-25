#!/bin/bash
# smoke-test.sh — Standalone health check for staging or production
# Usage: ./smoke-test.sh [staging|production]
# Default: staging

set -euo pipefail

STORE="bruce-mckenzie-booksellers.myshopify.com"
STAGING_THEME="150391423054"
PROD_THEME="149898395726"

TARGET="${1:-staging}"

if [ "$TARGET" = "production" ]; then
    PREVIEW="?preview_theme_id=${PROD_THEME}"
    LABEL="PRODUCTION"
else
    PREVIEW="?preview_theme_id=${STAGING_THEME}"
    LABEL="STAGING"
fi

echo "🔍 Smoke testing ${LABEL}..."
echo ""

FAILED=0
PAGES=("/" "/collections" "/collections/all" "/products" "/pages/about-us")

for PAGE in "${PAGES[@]}"; do
    URL="https://${STORE}${PAGE}${PREVIEW}"
    START=$(date +%s%N 2>/dev/null || date +%s)
    HTTP=$(curl -s -o /tmp/smoke-body.html -w "%{http_code}" --max-time 15 -A "Mozilla/5.0" "$URL")
    END=$(date +%s%N 2>/dev/null || date +%s)

    if [ "$HTTP" -eq 200 ]; then
        SIZE=$(wc -c < /tmp/smoke-body.html | tr -d ' ')
        if grep -qi "internal server error\|template not found\|Liquid error" /tmp/smoke-body.html 2>/dev/null; then
            echo "  ⚠️  ${PAGE} — 200 but contains error strings"
            FAILED=1
        elif [ "$SIZE" -lt 1000 ]; then
            echo "  ⚠️  ${PAGE} — 200 but suspiciously small (${SIZE} bytes)"
            FAILED=1
        else
            echo "  ✅ ${PAGE} — 200 (${SIZE} bytes)"
        fi
    elif [ "$HTTP" -eq 302 ] || [ "$HTTP" -eq 301 ]; then
        echo "  ↩️  ${PAGE} — ${HTTP} redirect (may be password wall)"
    else
        echo "  ❌ ${PAGE} — HTTP ${HTTP}"
        FAILED=1
    fi
done

rm -f /tmp/smoke-body.html
echo ""

if [ "$FAILED" -eq 1 ]; then
    echo "⛔ ${LABEL} has issues. Review before proceeding."
    exit 1
fi

echo "✅ ${LABEL} looks healthy."
