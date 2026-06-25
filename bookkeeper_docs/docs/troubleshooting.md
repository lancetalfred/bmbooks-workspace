---
sidebar_position: 6
---

# Troubleshooting

Quick fixes for the most common problems. Start at the top — most issues are solved in the first two sections.

---

## The sync stopped running

**Symptom:** Books on the website aren't updating. The log file hasn't been written to in more than a few hours.

**Most likely cause:** The shop machine was restarted and the script didn't start back up automatically.

**Fix:**
1. Open the shop machine
2. Navigate to the BookKeeper script folder
3. Run: `python bookscan_sync.py`
4. Check that the log shows a new run starting

**Permanent fix:** Make sure the Windows Task Scheduler job is set to run at startup, not just on a schedule. See the [Shop Machine Setup](./setup/shop-machine) guide.

---

## A book isn't showing up on the website

Work through these in order:

**1. Is it listed in Bookscan for the website?**
In Bookscan, check the book's record. The "Web" flag (Tables → Authority Tables → Status) must be active for the book to appear in the sync.

**2. Is it in Shopify as a draft?**
All books sync as Draft — invisible to customers until activated. Go to Shopify Admin → Products, search by ISBN, and check the status. If it's there as a draft, just set it to Active.

**3. Has the sync run since the book was added to Bookscan?**
Check `bookscan_sync.log` for the most recent run time. If the book was just added, wait for the next sync cycle (up to 2 hours), or run a manual sync.

**4. Is the ISBN valid?**
A book with a blank or malformed ISBN will be skipped. Check the ISBN in Bookscan — it should be 13 digits starting with 978 or 979.

---

## A book is showing the wrong price or stock

**Cause:** The sync runs every 2 hours — there's always a short lag between a change in Bookscan and the website updating.

**Fix:** Wait for the next sync cycle. If it's urgent, run a manual sync:
```bash
python bookscan_sync.py
```

If the price is still wrong after the next sync, check the price in Bookscan directly. The sync always uses `MASTER.SELL_PRICE` — if that's wrong in Bookscan, it'll be wrong on the website.

---

## The sync is running but nothing is updating

**Cause:** Delta sync is working correctly — nothing has changed in Bookscan since the last run, so nothing is sent to Shopify.

**How to confirm:** Open `sync_state.json`. If it has a recent `last_run` timestamp, the sync is running fine. It's just not finding any changes to push.

**If you genuinely need to force a full refresh:**
```bash
python bookscan_sync.py --full
```
This re-sends every book regardless of whether it changed. Use sparingly — it takes much longer than a normal run.

---

## The script crashes with a file not found error

**Symptom:** Log shows something like `FileNotFoundError: MASTER.DBF not found`

**Cause:** The DBF path in the script doesn't match where the Bookscan files actually are.

**Fix:** Open `bookscan_sync.py` and check the `DBF_BASE_PATH` setting near the top. It should point to `Z:\bookscan` on the shop machine. If the Z: drive isn't mapped, reconnect it via Windows Explorer.

---

## The script crashes with a Shopify authentication error (401)

**Symptom:** Log shows `401 Unauthorized` or `Invalid API key`

**Cause:** The Shopify access token in the script is wrong or has been revoked.

**Fix:**
1. Go to Shopify Admin → Apps → Develop apps → BookKeeper
2. Click API credentials → Reveal token
3. Copy the token and update `SHOPIFY_ACCESS_TOKEN` in `bookscan_sync.py`

---

## Shopify rate limit error (429)

**Symptom:** Log shows `429 Too Many Requests`

**Cause:** The script is sending API calls faster than Shopify allows. This shouldn't happen under normal conditions — the script has a built-in 0.6 second delay between calls.

**Most likely cause:** Multiple instances of the script are running at the same time.

**Fix:** Open Task Manager on the shop machine and check for multiple Python processes. Kill the extras. Then check Task Scheduler to make sure the job isn't set to run overlapping schedules.

---

## A book has the wrong author name format (ALL CAPS)

**Cause:** Author names in Bookscan are stored in ALL CAPS. The script converts them to Title Case on sync. If an author is showing as ALL CAPS in Shopify, that book's record may have been in Shopify before the fix was applied.

**Fix:** Run a full sync to refresh the affected products:
```bash
python bookscan_sync.py --full
```

---

## The log file is getting very large

The log file grows with every sync run indefinitely. It won't cause any problems short-term, but if it gets very large (over a few hundred MB) over months of running, you can safely archive it:

1. Rename `bookscan_sync.log` to `bookscan_sync_archive_YYYY-MM.log`
2. A new `bookscan_sync.log` will be created on the next run automatically

---

## I need to check when the last sync ran

Open `sync_state.json` in the script folder. The `last_run` field shows the exact date and time of the last completed sync in ISO format (e.g. `2026-04-23T14:32:11`).

---

## Books are silently not syncing (422 errors on every book)

**Symptom:** The sync runs through non-book products fine (CDs, calendars, stationery) but every 978-prefix book hits `422 Client Error: unknown for url: .../products.json` and is skipped. Errors counter climbs rapidly.

**Cause:** A Shopify metafield definition has a type mismatch with what the script sends. The most common culprit is `bookscan.pages` being defined as **Integer** in Shopify Admin while the script sends it as a string. Shopify silently rejects the entire product payload when a metafield value doesn't match its definition's type. Non-book products skip the Pages metafield (because `pages=0`), which is why only books fail.

**Fix:**
1. Shopify Admin → **Settings** → **Custom data** → **Products**
2. Click into each of the 6 `bookscan.*` definitions
3. Confirm all are **Single line text** (the `A` icon, not `#` for Integer or a calendar for Date)
4. If any are wrong: Shopify doesn't allow editing the type in place. Delete the definition and recreate it as Single line text. Deletion orphans any existing values for that metafield, but for a small test run that's acceptable.
5. Restart the sync — the GraphQL find_by_sku will idempotently update existing products, and previously-failing books will now succeed.

**How to verify**: filter products tagged with `_cstatus-ACT` and product type Paperback. Open one. Scroll to Metafields. All 6 `bookscan.*` fields should be populated.

---

## Inventory updates failing with "specified inventory item could not be found"

**Symptom:** Log shows repeated `Inventory update non-fatal: inventorySetOnHandQuantities errors: ...The specified inventory item could not be found` warnings on every Update. Product metadata refreshes fine but stock counts don't change.

**Cause (suspected):** Variants created during the early buggy production runs (specifically: products created with the deprecated `inventory_quantity` field on `products.json` before the GraphQL inventory path was added) have a "ghost" `inventoryItem.id` reference. GraphQL returns the gid but the referenced entity doesn't actually exist in Shopify's modern inventory system.

**Scope:** Affects only the ~344 products created during the May 12 backfill's first hour. New products created after the GraphQL inventory path was added are fine. Customer-facing inventory was set correctly at create time.

**Fix:** Run `python Sync/diagnose_inventory.py` to confirm the diagnosis. Most likely remediation is to **delete and recreate** the affected products (the next sync run will create fresh variants with properly-linked inventory items). Alternative: try `productVariantsBulkUpdate` GraphQL mutation as a different path.

This is a one-off cleanup task post-backfill. The 2-hour scheduled sync must not be deployed until this is resolved — otherwise stock changes from in-store sales won't propagate to the website for the affected products.

---

## Duplicate products created on every full-sync restart (historical)

**Symptom (resolved 2026-05-12):** Restarting `--full` sync created duplicate copies of the first 8–30 products processed. Total duplicates grew with each restart.

**Cause:** The original `find_by_sku` used REST `/variants.json?sku={sku}` which doesn't actually filter on Shopify's side — it returned a page of recent variants and matched Python-side. For stores with >50 variants, older products were never found, so the script created duplicates of products that already existed.

**Fix:** Already in place. `find_by_sku` now uses GraphQL `productVariants(query: "sku:...")` which filters server-side reliably. Restarts no longer create duplicates regardless of store size.

**Cleanup:** Run `python Sync/dedupe.py --execute` once post-backfill to remove duplicates. Confirmed count from May 15 dry run: 40 extra products across 32 SKUs.

---

## Sync stopped because the shop machine was logged out

**Symptom:** Sync was running, you walked away, came back, the Command Prompt window is gone and the log file's last entry is hours old.

**Cause:** Logging out of the Windows user account kills all running processes including Python. **Disconnecting** from Chrome Remote Desktop is fine (the session continues in the background); **Signing out** of Windows is not.

**Fix:**
1. Reconnect via Chrome Remote Desktop
2. Sign back in if needed
3. Open Command Prompt → `cd C:\BookKeeper` → `python bookscan_sync.py --full`
4. The GraphQL find_by_sku will idempotently update everything already synced and resume Creates from where it left off. **No duplicates** will be created.

**Permanent fix:** Once Windows Task Scheduler is configured (post-launch step), the sync runs as a scheduled job and survives logouts.

**Avoiding it:** When stepping away from the shop machine, close the Chrome Remote Desktop browser tab instead of using Start → Sign Out. To lock the workstation without killing processes, use **Start → Lock** (not Sign Out).

---

## Sync is running but processing all products instead of skipping unchanged ones

**Symptom:** Log says "Mode: delta sync" but then immediately says "Processing all X products" and every product shows as Updated rather than being skipped.

**Cause:** `sync_state.json` on the shop machine is empty or missing. This happens when the file is deleted, or when multiple interrupted runs left it in an inconsistent state. Without prior hashes, every product looks "new" to the delta logic.

**Impact:** Functionally harmless — every product gets re-sent to Shopify, which is idempotent (Shopify just ignores unchanged values). The only cost is time: processing all ~36,000 products takes ~50 hours vs the normal ~5–15 minutes for a delta run.

**Fix options:**
1. **Let it run** — `sync_state.json` will be fully repopulated once the run completes. All future runs will be fast delta runs again.
2. **Stop and rebuild** — kill the process (`taskkill /f /im python.exe`), then run `python bookscan_sync.py --full`. The `--full` flag forces a complete run and saves hashes as it goes, but takes the same ~50 hours. Only useful if you need the run to do something specific `--full` provides.

**Preventing it:** Don't interrupt the sync mid-run if avoidable. Always start the sync with `start /b python bookscan_sync.py` so it survives CRD session disconnects.

---

## Command Prompt closed mid-sync / CRD session dropped

**Symptom:** You were watching the sync run in a Command Prompt window. The Chrome Remote Desktop session dropped (or the window was closed). When you reconnect, the sync is no longer running.

**Cause:** If the sync was started in a regular `cmd` window (`python bookscan_sync.py`), the Python process is a child of that window and dies when the window closes. Disconnecting from Chrome Remote Desktop does **not** kill the session — but if the CRD tab in Chrome was closed abruptly, Windows may have ended the session entirely, taking the cmd window with it.

**Fix:**
1. Reconnect via Chrome Remote Desktop
2. Check if Python is still running: `tasklist | findstr python`
3. Check where the log left off: `powershell -command "Get-Content C:\BookKeeper\bookscan_sync.log -Tail 5"`
4. Restart: `cd C:\BookKeeper && start /b python bookscan_sync.py`

**The `start /b` flag** runs the script as a detached background process. It survives CRD disconnects because it's no longer tied to the cmd window's lifetime. Use it for every manual sync run.

**Progress after restart:** The delta sync will skip everything already saved in `sync_state.json`. If the previous run was far along, the restart will pick up close to where it left off.

---

## Something's wrong and I'm not sure what

Run a dry run first — it reads all the Bookscan data and logs what it finds, without touching Shopify at all:

```bash
python bookscan_sync.py --dry-run
```

Check the output for any errors or unexpected numbers (e.g. 0 products found instead of ~38,000). This is usually enough to point you at the problem.

If you're still stuck, check `bookscan_sync.log` for the most recent run and look for any `[ERROR]` lines.
