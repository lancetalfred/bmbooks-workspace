#!/bin/bash
# pre-push-hook.sh — Claude Code PreToolUse hook
# Intercepts shopify theme push commands and validates before allowing
# Reads tool input JSON from stdin

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)

# Only act on shopify theme push commands
if ! echo "$COMMAND" | grep -q "shopify theme push"; then
    exit 0
fi

THEME_DIR="/Users/lancealfred/Projects/bmbooks-workspace/Shopify_Theme"
PROD_THEME="149898395726"
STAGING_THEME="150391423054"
BLOCK=""

# Check 1: Template JSON files modified locally — high risk
if [ -d "$THEME_DIR/.git" ]; then
    MODIFIED=$(git -C "$THEME_DIR" diff --name-only 2>/dev/null | grep "^templates/.*\.json$" || true)
    if [ -n "$MODIFIED" ]; then
        BLOCK="BLOCKED: Local templates/*.json modified without pulling first.\nFiles: ${MODIFIED}\nRun: cd $THEME_DIR && shopify theme pull --theme $PROD_THEME --only <file>\nThis caused a homepage 404 on 2026-06-12. Pull first, then retry."
    fi
fi

# Check 2: Pushing to staging without recent production pull
if echo "$COMMAND" | grep -q "$STAGING_THEME"; then
    MARKER="$THEME_DIR/.last_prod_pull"
    if [ -f "$MARKER" ]; then
        LAST_PULL=$(cat "$MARKER" 2>/dev/null || echo 0)
        NOW=$(date +%s)
        AGE_HOURS=$(( (NOW - LAST_PULL) / 3600 ))
        if [ "$AGE_HOURS" -gt 4 ]; then
            echo "⚠️  Last production pull was ${AGE_HOURS}h ago. Consider using Tools/safe-push.sh instead." >&2
        fi
    else
        echo "⚠️  No record of a production pull. Staging may be out of sync." >&2
        echo "   Consider using Tools/safe-push.sh which pulls production first." >&2
    fi
fi

# Check 3: Production push — always warn
if echo "$COMMAND" | grep -q "$PROD_THEME"; then
    echo "🚨 PRODUCTION PUSH — ensure this was tested on staging first." >&2
fi

# Block or allow
if [ -n "$BLOCK" ]; then
    echo -e "$BLOCK" >&2
    exit 2
fi

exit 0
