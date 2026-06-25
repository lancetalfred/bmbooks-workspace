# BMBooks — Phase 2 Plan

**Last updated:** May 5, 2026

---

## Status

Phase 1 (outbound sync) went live May 5, 2026. `bookscan_sync.py` is running on the
shop machine, syncing 38,490 products to Shopify on a 2-hour Task Scheduler cycle.

Phase 2 can begin once Phase 1 has been stable for at least one week.

---

## Overview

Phase 2 has two components:

| Component | Priority | What it does |
|---|---|---|
| Inbound order sync | **#1 — Critical** | Shopify orders → Bookscan web order tables. Eliminates Louisa's manual order re-keying. |
| Sync GUI | #2 — Quality of life | tkinter desktop app replacing the `Sync Now.bat` shortcut |

Cover images are already complete — handled in Phase 1 via `Z:\bookscan\catalog`.

---

## Component 1 — Inbound Order Sync

### The problem

Every Shopify order requires Louisa to manually enter a full web sale in Bookscan —
customer name, delivery address, and every line item. Her words: *"we physically have
to cut and paste every fucking line."* This is the single biggest ongoing daily cost
and gets worse as online order volume grows.

### The solution — confirmed architecture (May 5, 2026)

Bookscan already has dedicated web order tables: `WEBORDHD.DBF` (order header) and
`WEBORDLN.DBF` (line items). These are the same tables the old WooCommerce middleware
wrote to. Both are currently empty — the middleware is gone.

Phase 2 writes Shopify orders directly into these tables. Bookscan processes them as
normal web sales — stock deducts, NielsenBookScan reporting works, EDI triggers work,
financials are correct. Nothing needs to change in Bookscan itself.

```
Customer buys on Shopify
        ↓
Shopify order created
        ↓
order_sync.py polls Orders API (every 2 hours)
        ↓
Writes 1 record → WEBORDHD.DBF  (customer + address + totals)
Writes N records → WEBORDLN.DBF  (one per line item)
        ↓
Bookscan processes web order natively
(stock deducted, NielsenBookScan, EDI, financials — all normal)
        ↓
Next bookscan_sync.py run picks up updated stock → Shopify updated
```

### Field mapping

**WEBORDHD.DBF — one record per order**

| Shopify | DBF field |
|---|---|
| Order number | `CUSTORDNO` |
| Order date | `ORDDATE` |
| Total price | `ORDTOTAL` |
| Shipping cost | `SHIPPING` |
| Email | `EMAIL` |
| Billing first/last name | `FIRSTNAME` / `LASTNAME` |
| Billing address 1/2 | `ADD1` / `ADD2` |
| Billing city/province/postcode/country | `CITY` / `STATE` / `PCODE` / `COUNTRY` |
| Shipping address 1/2 | `DADD1` / `DADD2` |
| Shipping city/province/postcode/country | `DCITY` / `DSTATE` / `DPCODE` / `DCOUNTRY` |
| Shipping name | `DCONTACT` |
| Phone | `PHONE` |
| Order notes | `COMMENTS` |
| Tracking number (on fulfillment) | `SHIPNO` |
| CC fields | Leave blank — Shopify handles payment |

**WEBORDLN.DBF — one record per line item**

| Shopify | DBF field |
|---|---|
| Order number | `ORDERNO` |
| `line_item.sku` | `ISBN` |
| `line_item.title` | `TITLE` |
| `line_item.quantity` | `QTY` |
| `line_item.price` | `SELL_PRICE` |

### New dependency

`dbfread` is read-only. Phase 2 requires the `dbf` library:
```
pip install dbf
```

### Open questions (resolve in Stage 1)

| Question | Why it matters |
|---|---|
| How does `ORDERNO` auto-increment? | Do we set it, or does Bookscan manage it? |
| Is `IDPRODUCT` required? | Can we look it up from MASTER.DBF by ISBN, or leave blank? |
| Is `BL_CODE` required? | What is it? Can we leave blank? |
| Does Bookscan auto-process new WEBORDHD records? | Or does Louisa need to trigger something after records are written? |

---

## Build Plan — Stage by Stage

### Stage 1 — Research (1 session, Chrome Remote Desktop)

Before writing code, resolve the four open questions above:

1. Ask Louisa to enter a web sale manually — watch exactly what she does and what
   she clicks AFTER saving. Does Bookscan auto-pick up new records, or is there a
   "Process web orders" step?
2. Inspect a real WEBORDHD record after she saves it — note the ORDERNO value,
   IDPRODUCT value, BL_CODE value.
3. Run `python -c "from dbfread import DBF; d=DBF(r'Z:\bookscan\WEBORDHD.DBF'); print(list(d)[-1])"` to see the last real record.

### Stage 2 — Build (local dev)

New script: `Sync/order_sync.py`

```
order_sync.py
├── poll_shopify_orders()      — GET /orders.json, filter paid + unprocessed
├── write_order_header()       — write 1 record to WEBORDHD.DBF
├── write_order_lines()        — write N records to WEBORDLN.DBF
├── load_processed_orders()    — read processed_orders.json
├── save_processed_orders()    — write processed_orders.json
└── run_order_sync()           — main loop, --dry-run / --full flags
```

Test against:
- Dev Shopify store (bmbooks-dev.myshopify.com) for order data
- Local SABSSAVE DBF copy for write testing

### Stage 3 — UAT (shop machine, Chrome Remote Desktop)

| # | Test | Pass condition |
|---|---|---|
| TC01 | Dry run — no writes | Shows orders that would be written, no DBF changes |
| TC02 | Single order written to WEBORDHD | Record visible and correct in Bookscan |
| TC03 | Line items written to WEBORDLN | All items visible, ISBN/qty/price correct |
| TC04 | Duplicate prevention | Running twice — no duplicate records |
| TC05 | File locking safety | Sync runs while Bookscan is open — no crash |
| TC06 | Multi-item order | 3-item order = 1 header + 3 line records |
| TC07 | NZ address | All address fields map correctly |
| TC08 | International address | Country, province, postcode all correct |
| TC09 | Stock deducted in Bookscan | After Bookscan processes web order, ONHAND reduced |
| TC10 | Outbound sync reflects updated stock | Next bookscan_sync.py run shows new stock on Shopify |
| TC11 | Error handling | Bad ISBN on line item — order still writes, error logged |
| TC12 | Louisa sign-off | Louisa confirms web sale looks correct in Bookscan UI |

### Stage 4 — Deploy to production

1. Update `order_sync.py` config → live Shopify store
2. Copy to `C:\BookKeeper\` on shop machine
3. `pip install dbf` on shop machine
4. Add to Task Scheduler — `BookKeeper Order Sync`, every 2 hours, offset 1 hour
   from outbound sync (so they don't overlap)
5. Monitor first 5 real orders manually
6. Louisa confirms she no longer needs to re-key orders

---

## Component 2 — Sync GUI

Lower priority. Build after inbound order sync is stable.

A tkinter desktop window replacing the `Sync Now.bat` shortcut:

```
┌─────────────────────────────────────────────┐
│  BMBooks BookKeeper                         │
│                                             │
│  Last sync:   2026-05-05 14:02              │
│  Next sync:   2026-05-05 16:02              │
│                                             │
│  [ Sync Now ]                               │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ 14:02:01 Loading publisher data...  │   │
│  │ 14:02:03 38,490 products read       │   │
│  │ 14:02:04 Delta: 12 changed          │   │
│  │ 14:02:05 3 new orders written       │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Products: Updated 12  Errors: 0           │
│  Orders:   Written 3   Errors: 0           │
└─────────────────────────────────────────────┘
```

New file: `Sync/bookkeeper_gui.py`
- Runs both `bookscan_sync.py` and `order_sync.py` in a background thread
- Live log output in the scroll area
- Task Scheduler still handles automated 2-hour runs independently

Optional: package as `.exe` via PyInstaller so Python doesn't need to be visible.

---

## Files

| File | Status | Purpose |
|---|---|---|
| `Sync/bookscan_sync.py` | ✅ Live | Outbound sync — Bookscan → Shopify |
| `Sync/order_sync.py` | ⏳ To build | Inbound sync — Shopify orders → Bookscan |
| `Sync/bookkeeper_gui.py` | ⏳ To build | tkinter GUI wrapper |
| `Sync/processed_orders.json` | ⏳ Created on first run | Tracks written Shopify order IDs |
| `Sync/requirements.txt` | ✅ Exists | Add `dbf` before Phase 2 deploy |

---

## Prerequisites before starting

- Phase 1 stable for at least 1 week (no errors in `bookscan_sync.log`)
- Stage 1 research session with Louisa completed (open questions answered)
- `dbf` library tested on local SABSSAVE copy
