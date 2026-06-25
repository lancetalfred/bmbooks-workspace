# Shopify CLI — Builder's Workflow

## The daily path

**Always run from the `Shopify_Theme/` directory.** The CLI reads `shopify.theme.toml` from wherever you run it. Running from workspace root drops files in the wrong place.

```bash
cd /Users/lancealfred/Projects/bmbooks-workspace/Theme
```

---

## Commands I actually use

### Push changes to Shopify

```bash
# Push to staging (test here first)
shopify theme push --theme 150391423054

# Push to production (--allow-live required when running non-interactively)
shopify theme push --theme 149898395726 --allow-live
```

Push sends every changed/new file to Shopify. Shopify does a file-by-file diff — only changed files are updated.

### Pull before editing any template

```bash
# Pull a specific file (safe, surgical)
shopify theme pull --only templates/index.json
shopify theme pull --only templates/product.json

# Full pull (everything Shopify has — use to sync after Theme Editor session)
shopify theme pull
```

**Why this matters:** The Theme Editor (Shopify Admin → Customize) writes changes directly to Shopify's copy of `templates/*.json`. Your local copy goes stale the moment anyone uses the Theme Editor. Pushing a stale local copy overwrites those changes. This caused a homepage 404 on 2026-06-12.

**Rule:** Before editing and pushing any `templates/*.json`, always pull it first.

### Local development preview

```bash
shopify theme dev
```

Opens a live preview in your browser at `http://127.0.0.1:9292`. Changes sync automatically. Does NOT touch the live store. Safe for experimentation.

### Check which themes exist on the store

```bash
shopify theme list
```

---

## Theme IDs (memorise these)

| Theme | ID |
|---|---|
| Production (live) | 149898395726 |
| Staging (test copy) | 150391423054 |

---

## The "never push templates without pulling" rule in detail

Theme Editor → saves to Shopify
Your local file → stale immediately

Sequence that's safe:
1. `shopify theme pull --only templates/index.json`
2. Edit the file locally
3. `shopify theme push --theme <ID>`

Sequence that causes data loss:
1. Edit local file (stale copy)
2. Push → overwrites Theme Editor changes

---

## What the CLI won't do

- Won't push `config/settings_data.json` safely if Louisa has made Theme Editor changes — same pull-first rule applies
- Won't resolve merge conflicts — last push wins
- `shopify theme dev` doesn't work with a password-protected store unless you're logged in on the preview URL

---

## Official docs

`shopify theme --help` or https://shopify.dev/docs/api/shopify-cli/theme
