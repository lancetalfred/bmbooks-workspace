---
sidebar_position: 5
---

# Troubleshooting

Quick fixes for the most common problems. Start at the top — most issues are resolved in the first two sections.

---

## A book isn't showing up on the website

Work through these in order:

**1. Does it have a title and a price in Bookscan?**
Books without a title or without a price are held in Draft (hidden from customers). Once both are filled in, the next hourly sync will make it active automatically.

**2. Is it web-listed in Bookscan?**
Check the book's record — the "Web" flag must be active for the book to sync.

**3. Has the sync run recently?**
Check `Z:\BookKeeper\bookscan_sync.log` for today's date. If the book was just added, wait for the next sync (up to 1 hour), or trigger a manual sync (see [Shop Machine Operations](./setup/shop-machine)).

**4. Is the ISBN valid?**
A book with a blank or malformed ISBN will be skipped. It should be 13 digits starting with 978 or 979.

---

## A book is showing the wrong price or stock

The sync runs every hour. If you just changed a price or stock count in Bookscan, wait up to 1 hour for it to appear on the website. If it's still wrong after that, check the value in Bookscan — the website always mirrors exactly what's in Bookscan.

---

## The sync stopped running

Signs something might be wrong:
- Stock levels on the website haven't changed after in-store sales
- A book added to Bookscan yesterday still isn't on the website
- The BookKeeper window shows a red dot

See [Shop Machine Operations](./setup/shop-machine) for step-by-step recovery steps.

---

## DBF schema validation failed

If a sync fails with a message like:

```
RuntimeError: DBF schema validation failed — halting before any Shopify changes:
  • SCHEMA CHANGE in MASTER.DBF: missing fields ['SELL_PRICE']
```

This means Franz Technologies released a BookScan update that renamed or removed a field the sync depends on. The sync has stopped deliberately to prevent corrupt data reaching Shopify. Contact Lance — the script needs updating before it can run again.

---

## Shopify authentication error (401 Unauthorized)

The Shopify access token is missing or expired. This is a technical fix — contact Lance.

---

## The sync is running but nothing seems to update

This is usually normal. The sync only processes products that have changed since the last run (delta sync). If nothing changed in Bookscan, nothing gets sent to Shopify — which is correct behaviour.

To confirm the sync is running fine, check `Z:\BookKeeper\bookscan_sync.log` — look for a recent timestamp and `Sync complete` near the bottom.

---

## Something doesn't look right and I'm not sure what

Run a dry run — it reads all the Bookscan data and shows what it finds, without touching Shopify at all:

```
cd /d Z:\BookKeeper
python bookscan_sync.py --dry-run --once
```

Check the output for unexpected numbers (e.g. 0 products found instead of ~38,000). If you're still stuck, check the log for any `[ERROR]` lines and contact Lance.
