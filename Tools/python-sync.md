# Python Sync Scripts — Builder's Workflow

## Scripts overview

| Script | What it does | Run from |
|---|---|---|
| `bookscan_sync.py` | Hourly sync: reads DBF files, pushes products to Shopify | Shop machine (Windows) |
| `genre_enrichment_v2.py` | Batch-enriches products with BIC genre tags | Local (Mac) or shop machine |
| `bookkeeper_gui.py` | GUI wrapper for sync operations | Shop machine |
| `fix_taxable.py` | One-time fix — already run (2026-05-29) | Completed |

---

## bookscan_sync.py

### What it reads

| File | Location | Contents |
|---|---|---|
| `WEBLIST.DBF` | `\\Server\c\bookscan\` | Product list — ISBNs to sync |
| `MASTER.DBF` | `\\Server\c\bookscan\` | Full bibliographic data (title, author, price) |
| `PUBLISHER.DBF` | `\\Server\c\bookscan\` | Publisher/vendor data |

### How the hourly sync runs

On the shop machine the script runs via Task Scheduler. To check status:
- Open `Sync/bookscan_sync.log` — but **never read the full file** (it grows large)
- Grep for recent errors: `grep -i "error\|fail" bookscan_sync.log | tail -20`
- Check last sync time: `grep "Sync complete" bookscan_sync.log | tail -5`

### Running manually (shop machine)

```cmd
cd Z:\BookKeeper\Sync
python bookscan_sync.py
```

### Common failures

| Symptom | Cause | Fix |
|---|---|---|
| `PermissionError: MASTER.DBF` | Bookscan.exe has the file locked | Wait for Bookscan to close, retry |
| `ShopifyAPI rate limit` | Too many API calls (429) | Script retries automatically with backoff |
| `sync_state.json corrupt` | Interrupted sync mid-write | Delete sync_state.json, re-run (full resync) |
| Products not updating | sync_state.json has stale timestamps | Check timestamps in the file, delete if wrong |

### API token

Currently hardcoded in the script. **Must move to `.env` before GitHub commit.**

```python
# Replace hardcoded token with:
import os
from dotenv import load_dotenv
load_dotenv()
API_TOKEN = os.environ["SHOPIFY_API_TOKEN"]
```

---

## genre_enrichment_v2.py

### What it does

Reads BIC subject codes from Bookscan data, maps them to genre tags, and applies those tags to Shopify products in batches.

### Running (batch mode — all untagged products)

```bash
cd /Users/lancealfred/Projects/bmbooks-workspace/Sync
python genre_enrichment_v2.py
```

### Running (single product, for testing)

```bash
python genre_enrichment_v2.py --isbn 9781234567890
```

### Key internals

- `SKIP` list — ISBNs to never touch (manually curated exceptions)
- `DUAL_TAG_PAIRS` — books that get two genre tags (e.g., Crime + Thriller)
- `BINDING_MAP` — maps Bookscan binding codes to human labels (26 unknown codes remain)

### After running

Check the Shopify admin for the affected collections — new products should appear within 1–2 minutes (Shopify's smart collection index lag).

---

## Environment setup (local Mac)

```bash
cd /Users/lancealfred/Projects/bmbooks-workspace/Sync
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # if requirements.txt exists; otherwise pip install shopify requests python-dotenv
```

---

## Official docs

- Shopify Admin API: https://shopify.dev/docs/api/admin
- `dbfread` (DBF parsing): https://dbfread.readthedocs.io
