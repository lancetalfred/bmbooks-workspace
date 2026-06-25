---
sidebar_position: 2
---

# Inbound Sync — Shopify → Bookscan

:::caution Phase 2 — In development
Inbound order sync is not yet live. Until it is, Louisa must manually enter each online order as a web sale in Bookscan.
:::

## How it works

When a customer buys online, Shopify creates an order. BookKeeper polls Shopify's Orders API and writes the order directly into Bookscan's web order tables — exactly the same way the old WooCommerce middleware did.

```
Customer buys online
       ↓
Shopify order created
       ↓
BookKeeper polls Orders API (every 2 hours)
       ↓
Writes record to WEBORDHD.DBF (order header)
Writes record(s) to WEBORDLN.DBF (line items)
       ↓
Bookscan processes the web order normally
(stock deducted, NielsenBookScan, EDI, financials all update)
       ↓
Next outbound sync reflects updated stock on Shopify
```

## DBF architecture — confirmed May 5, 2026

Inspected live on shop machine via Chrome Remote Desktop. Both tables are currently empty (the WooCommerce middleware that previously wrote here is gone).

### WEBORDHD.DBF — Order header

One record per Shopify order.

| Shopify field | DBF field | Notes |
|---|---|---|
| Order number | `CUSTORDNO` | Shopify order ID — used to prevent double-processing |
| Order date | `ORDDATE` | |
| Total price | `ORDTOTAL` | |
| Shipping cost | `SHIPPING` | |
| Email | `EMAIL` | |
| Billing first name | `FIRSTNAME` | |
| Billing last name | `LASTNAME` | |
| Billing company | `COMPANY` | |
| Billing address 1 | `ADD1` | |
| Billing address 2 | `ADD2` | |
| Billing city | `CITY` | |
| Billing province | `STATE` | |
| Billing postcode | `PCODE` | |
| Billing country | `COUNTRY` | |
| Shipping address 1 | `DADD1` | |
| Shipping address 2 | `DADD2` | |
| Shipping city | `DCITY` | |
| Shipping province | `DSTATE` | |
| Shipping postcode | `DPCODE` | |
| Shipping country | `DCOUNTRY` | |
| Shipping name | `DCONTACT` | |
| Phone | `PHONE` | |
| Order notes | `COMMENTS` | |
| Tracking number | `SHIPNO` | Written when order is fulfilled |
| — | `CCTYPE` / `CCNAME` / `CCNUMBER` / `CCEXPIRY` | Left blank — Shopify handles payment |
| — | `PROCESSED` | Set by Bookscan when order is processed |

Auto-generated fields: `ORDERNO` (Bookscan internal sequence), `TAXES`, `FREIGHT`, `DCOLLECT`, `CUSTUID`, `FAX`.

### WEBORDLN.DBF — Order lines

One record per line item per order.

| Shopify field | DBF field | Notes |
|---|---|---|
| Order number | `ORDERNO` | Links to WEBORDHD |
| `line_item.sku` | `ISBN` | |
| `line_item.title` | `TITLE` | |
| `line_item.quantity` | `QTY` | |
| `line_item.price` | `SELL_PRICE` | |
| — | `BL_CODE` | Book list code — leave blank or derive |
| — | `IDPRODUCT` | Bookscan internal ID — look up from MASTER.DBF by ISBN |
| — | `PROCESSED` | Set by Bookscan when line is processed |

## Why this approach is better than writing to MASTER.ONHAND

The earlier design proposed deducting stock directly from `MASTER.ONHAND`. This was wrong — it would update stock numbers but create no sale record, breaking:
- NielsenBookScan sales reporting (industry-wide data BMBooks contributes to)
- Bookscan's own financial reports
- EDI reordering triggers

Writing to WEBORDHD + WEBORDLN is the correct approach because Bookscan processes these as proper web sales — stock is deducted internally through its own order workflow, and everything downstream (reporting, financials, EDI) works as normal.

## Why polling (not webhooks)

The WooCommerce system used webhooks via a Barcode Solutions Heroku middleware server. BookKeeper uses **polling** instead because:
- No public URL needed on the shop machine
- Self-contained — no external infrastructure
- Volume is low enough that a 2-hour lag is acceptable

## Order tracking

Processed Shopify order IDs are stored in `processed_orders.json` to prevent duplicate writes across runs.

## DBF write library

`dbfread` is read-only. Phase 2 requires the `dbf` library (`pip install dbf`) which supports both reading and writing Bookscan's DBF format.

## DBF write safety

Writing to DBF files while Bookscan is running carries a risk of file locking. BookKeeper uses retry logic with a short delay if a file is locked. If writing fails after retries, the order is logged and flagged for manual processing — the sync never silently drops an order.

## Manual workaround (until Phase 2 is live)

When a Shopify order arrives, Louisa manually enters it as a **web sale** in Bookscan — customer name, delivery address, and every line item (ISBN, title, quantity, price). This is the single biggest daily pain point: a single multi-item order takes several minutes to key in.

Phase 2 eliminates this entirely.
