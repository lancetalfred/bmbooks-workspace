---
sidebar_position: 1
---

# Shop Machine Operations

Runbook for Lance — what to do when something needs attention on the shop machine.

**Access:** Chrome Remote Desktop → shop machine (Windows, `Z:\BookKeeper`)

---

## Checking the sync ran

The sync runs automatically every hour via Windows Task Scheduler. To confirm it ran:

1. Open `Z:\BookKeeper\bookscan_sync.log` in Notepad
2. Look for the most recent entry — should show today's date/time
3. Check for `Sync complete` near the bottom and an error count of 0

Alternatively, open the BookKeeper GUI shortcut on the desktop — the **Last sync** timestamp tells you when it last ran.

---

## Manually triggering a sync

If Louisa needs an immediate update (e.g. after a large stock change):

```
cd /d Z:\BookKeeper
python bookscan_sync.py --once
```

This runs one delta sync and exits. The hourly scheduled task continues as normal.

For a full sync of all products (slower, ~2–3 hours):

```
python bookscan_sync.py --full --once
```

---

## If the sync has stopped

**Step 1:** Check whether the scheduled task is still active.
- Open Task Scheduler (search in Start menu)
- Find the BookKeeper task
- Check its status — if it shows **Disabled** or **Ready** with an old Last Run time, right-click → Run

**Step 2:** Check the environment variable is still set.

```
python -c "import os; t=os.environ.get('SHOPIFY_ACCESS_TOKEN','NOT SET'); print(f'Starts with: {t[:6]}, length: {len(t)}')"
```

Expected: `Starts with: shpat_, length: 38`

If it shows `NOT SET`, the environment variable was lost (can happen after a Windows update or profile reset). Re-run:

```
setx SHOPIFY_ACCESS_TOKEN "<token>"
```

Then close the terminal, open a new one, and confirm it shows `shpat_` again before restarting the scheduled task.

**Step 3:** Check the log for errors.

```
type Z:\BookKeeper\bookscan_sync.log | more
```

Look for `ERROR` or `RuntimeError` lines near the end. Common causes are in the [Troubleshooting](../troubleshooting) doc.

---

## Deploying an updated script

When `bookscan_sync.py` or another script is updated via GitHub:

1. On your Mac: `git pull` on `main` to get the latest
2. Copy the updated file from your Mac's `Sync/` folder to `Z:\BookKeeper\` on the shop machine via Chrome Remote Desktop drag-and-drop (or copy-paste)
3. Run a dry-run to confirm it starts cleanly:

```
cd /d Z:\BookKeeper
python bookscan_sync.py --dry-run --once
```

4. If the dry-run passes, the next scheduled hourly run will use the new version

---

## DBF schema alert

If a sync fails with a message like:

```
RuntimeError: DBF schema validation failed — halting before any Shopify changes:
  • SCHEMA CHANGE in MASTER.DBF: missing fields ['SELL_PRICE'] — Franz may have renamed...
```

This means Franz Technologies released a BookScan update that changed a field name. **Do not attempt a workaround.** The sync is intentionally stopped to prevent corrupt data reaching Shopify. Contact Lance — the field mapping in `bookscan_sync.py` needs updating before the sync can run again.

---

## Key file locations

| File | Path | Purpose |
|---|---|---|
| Main sync script | `Z:\BookKeeper\bookscan_sync.py` | Hourly sync |
| Sync log | `Z:\BookKeeper\bookscan_sync.log` | Check what ran |
| State file | `Z:\BookKeeper\sync_state.json` | Delta sync hashes — do not edit |
| Bookscan data | `\\Server\c\bookscan\*.DBF` | Source data (read-only) |
