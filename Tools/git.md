# Git — Builder's Workflow

## Status (2026-06-14)

Git is not yet set up for this workspace. This file is a placeholder — the workflow decisions have been made, the commands are ready to run when GitHub is configured.

---

## What will go in the repo

**In scope (code):**
- `Theme/` — full Shopify theme
- `Sync/` — Python scripts only (NOT the data files)
- `Tools/` — these builder's manuals

**Out of scope (personal thinking, not code):**
- `Project/` — markdown planning docs
- `Memo/` — email drafts
- `Legacy/` — historical docs

**Out of scope (sensitive):**
- `Reports/` — customer order data (CSV/XLSX)
- `Sync/SABSSAVE/` — raw DBF files (stock/customer data from Bookscan)
- `Sync/sync_state.json` — live API sync state
- `Sync/bookscan_sync.log` — log file
- `.env` — API tokens

---

## .gitignore (ready to create)

```gitignore
# Sensitive data
Sync/SABSSAVE/
Sync/*.dbf
Sync/sync_state.json
Sync/*.log
Reports/
*.csv
*.xlsx

# Credentials
.env
*.key
*.pem

# Node / build artifacts
node_modules/
.DS_Store
```

---

## Initial setup commands (run once)

```bash
cd /Users/lancealfred/Projects/bmbooks-workspace
git init
git remote add origin <GITHUB_URL>

# Create .gitignore first, then:
git add Theme/ Sync/*.py Tools/
git commit -m "Initial commit — Shopify theme + sync scripts"
git push -u origin main
```

---

## Daily workflow (once repo is set up)

```bash
# Before starting work — pull any remote changes
git pull

# After making changes
git status                          # what changed?
git diff Theme/snippets/card-gallery.liquid   # review before staging
git add Theme/snippets/card-gallery.liquid
git commit -m "Fix: eager loading guard on card gallery"
git push
```

---

## Pre-push checklist

Before every push:
- [ ] `git status` — no sensitive files staged
- [ ] No `templates/*.json` changes unless you just pulled them from Shopify first
- [ ] No `.env`, no `*.dbf`, no `Reports/`

---

## Notes

- Repo is private (Louisa's permission needed to make it public — linked to BMBooks case study)
- API token in `bookscan_sync.py` is currently hardcoded — move to `.env` before first commit
- `shopify.theme.toml` in `Theme/` is safe to commit (contains store URL and theme IDs, no secrets)

---

## Official docs

`git --help` or https://git-scm.com/docs
