---
sidebar_position: 2
---

# Configuration

All configuration is at the top of `bookscan_sync.py`.

## Settings

```python
# Shopify store — change to live store URL for production
SHOPIFY_STORE_URL    = "bruce-mckenzie-booksellers.myshopify.com"

# Access token from Shopify Admin > Apps > Develop apps
SHOPIFY_ACCESS_TOKEN = "shpat_xxxxxxxxxxxx"

# DBF files — Z:\bookscan on the shop machine
DBF_BASE_PATH = r"Z:\bookscan"

# Sync settings
SYNC_INTERVAL_HOURS = 2       # how often to run automatically
MAX_PRODUCTS        = None    # None = all products (set to 20 for testing)
```

## Production vs dev

| Setting | Dev (UAT) | Production |
|---|---|---|
| `SHOPIFY_STORE_URL` | `bmbooks-dev.myshopify.com` | `bruce-mckenzie-booksellers.myshopify.com` |
| `SHOPIFY_ACCESS_TOKEN` | Dev store token | Live store token |
| `DBF_BASE_PATH` | Local `SABSSAVE/` folder | `Z:\bookscan` |
| `MAX_PRODUCTS` | `20` | `None` |

## CLI flags

| Flag | Effect |
|---|---|
| *(none)* | Delta sync — only changed products |
| `--full` | Full sync — all web-listed products regardless of state |
| `--dry-run` | Show what would sync, no API calls made |

## Running manually

```bash
# Delta sync
python bookscan_sync.py

# Full sync
python bookscan_sync.py --full

# Dry run (safe to run any time)
python bookscan_sync.py --dry-run
```
