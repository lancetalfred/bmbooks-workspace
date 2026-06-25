---
sidebar_position: 1
---

# Requirements

## Shop machine

- Windows PC (the Bookscan machine, always on)
- Python 3.10 or later
- Access to `Z:\bookscan\` (Bookscan database files)
- Internet access (for Shopify API calls)

## Python dependencies

Install via:

```bash
pip install -r requirements.txt
```

| Package | Purpose |
|---|---|
| `dbfread` | Read Bookscan FoxPro DBF files |
| `requests` | Shopify Admin API calls |
| `schedule` | 2-hour automated sync loop |

## Shopify

- A **custom app** in the Shopify store with these scopes:
  - `write_products`
  - `read_products`
  - `write_inventory`
  - `read_inventory`
  - `read_locations`
- Four **metafield definitions** under namespace `bookscan`:
  - `bookscan.author` — Single line text
  - `bookscan.isbn` — Single line text
  - `bookscan.pages` — Single line text
  - `bookscan.publication_date` — Single line text

## Files

| File | Location | Purpose |
|---|---|---|
| `bookscan_sync.py` | Shop machine | Main sync script |
| `requirements.txt` | Shop machine | Python dependencies |
| `sync_state.json` | Same folder as script | Delta sync state (auto-created) |
| `bookscan_sync.log` | Same folder as script | Run log (auto-created) |
