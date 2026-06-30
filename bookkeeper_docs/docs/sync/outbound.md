---
sidebar_position: 1
---

# What syncs to the website

A quick reference for what BookKeeper does and doesn't send to Shopify.

---

## What appears on the website

A product appears on the website if it meets **all three** of these conditions in Bookscan:

1. It is web-listed (marked in WEBLIST)
2. Its status code is not excluded (e.g. not OP, RP, RUC, NLA, OSI)
3. Its department is a book department (not Audio, Magazines, Gifts, etc.)

---

## When a product is visible vs hidden

| Condition | Status on website |
|---|---|
| Title present + price > $0 | **Active** — visible to customers |
| Price = $0 (no price set yet) | **Draft** — hidden until price is added |
| Title missing | **Draft** — hidden until title is added |
| Status changed to OP / RP / RUC / NLA / OSI | **Draft** — hidden automatically |
| Marked inactive in WEBLIST | Removed from sync entirely |

Once a hidden product gets its missing information (title or price) in Bookscan, the next hourly sync will automatically make it visible. No action needed in Shopify.

---

## What fields sync

Every time a product is created or updated, BookKeeper sends:

| Website field | Where it comes from in Bookscan |
|---|---|
| Title | MASTER.DBF → TITLE |
| Author | MASTER.DBF → AUTHOR |
| Publisher | PUBLISHER.DBF → PUBLISHER |
| Price | MASTER.DBF → SELL_PRICE |
| Stock count | MASTER.DBF → ONHAND |
| Format (Paperback, Hardback, etc.) | MASTER.DBF → BINDING |
| Description / blurb | PUBLISHER.DBF → BLURB |
| Categories / genre tags | WEBMAINCAT + WEBSUBCAT |
| Cover image | Image folder on shop machine (best available resolution) |

---

## What doesn't sync

- Customer orders — these must be entered manually in Bookscan until Phase 2 is built
- Shopify-specific content (banners, promotional text, collection images) — managed directly in Shopify
- Manually curated collections (Staff Picks, NZ Authors) — managed directly in Shopify

---

## How often

Every hour, automatically. Only products that have changed since the last run are processed (delta sync). A full sync of all ~38,000 products only happens if forced manually.
