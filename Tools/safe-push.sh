#!/bin/bash
# safe-push.sh — Pull production → push staging → smoke test
# Usage: ./safe-push.sh [--only path/to/file]
# All guardrails in one script. Zero tokens.

set -euo pipefail

THEME_DIR="/Users/lancealfred/Projects/bmbooks-workspace/Shopify_Theme"
PROD_THEME="149898395726"
STAGING_THEME="150391423054"
STORE="bruce-mckenzie-booksellers.myshopify.com"

cd "$THEME_DIR"

# --- Step 1: Block template JSON pushes unless pulled first ---
if [ "${1:-}" = "--only" ] && [[ "${2:-}" == templates/*.json ]]; then
    echo "📥 Template JSON detected — pulling fresh copy from production first..."
    shopify theme pull --theme "$PROD_THEME" --only "$2"
fi

# --- Step 2: Sync with production ---
if [ "${1:-}" = "--only" ] && [ -n "${2:-}" ]; then
    echo "📥 Pulling targeted file from production..."
    shopify theme pull --theme "$PROD_THEME" --only "$2"
else
    echo "📥 Pulling full production to ensure local is current..."
    shopify theme pull --theme "$PROD_THEME"
fi
date +%s > "$THEME_DIR/.last_prod_pull"
echo ""

echo "📤 Pushing to staging..."
if [ "${1:-}" = "--only" ] && [ -n "${2:-}" ]; then
    shopify theme push --theme "$STAGING_THEME" --only "$2"
else
    shopify theme push --theme "$STAGING_THEME"
fi

PUSH_EXIT=$?
if [ $PUSH_EXIT -ne 0 ]; then
    echo "❌ Push to staging failed (exit $PUSH_EXIT)"
    exit $PUSH_EXIT
fi
echo ""

# --- Step 3: Smoke test ---
echo "🔍 Smoke testing staging..."
FAILED=0
PAGES=("/" "/collections" "/collections/all")

for PAGE in "${PAGES[@]}"; do
    URL="https://${STORE}${PAGE}?preview_theme_id=${STAGING_THEME}"
    HTTP=$(curl -s -o /tmp/smoke-body.html -w "%{http_code}" --max-time 15 -A "Mozilla/5.0" "$URL")

    if [ "$HTTP" -eq 302 ] || [ "$HTTP" -eq 301 ]; then
        echo "  ↩️  ${PAGE} — HTTP ${HTTP} (password wall or redirect)"
    elif [ "$HTTP" -ne 200 ]; then
        echo "  ❌ ${PAGE} — HTTP ${HTTP}"
        FAILED=1
    elif grep -qi "internal server error\|template not found\|Liquid error" /tmp/smoke-body.html 2>/dev/null; then
        echo "  ⚠️  ${PAGE} — HTTP 200 but contains error strings"
        FAILED=1
    else
        SIZE=$(wc -c < /tmp/smoke-body.html | tr -d ' ')
        echo "  ✅ ${PAGE} — HTTP 200 (${SIZE} bytes)"
    fi
done

rm -f /tmp/smoke-body.html
echo ""

if [ "$FAILED" -eq 1 ]; then
    echo "⛔ SMOKE TEST FAILED — do NOT push to production."
    echo "   Review staging at: https://${STORE}?preview_theme_id=${STAGING_THEME}"
    exit 1
fi

echo "✅ All checks passed. Staging is safe."
