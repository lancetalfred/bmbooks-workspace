# BMBooks — System Architecture

*Current state and future migration paths*

**Last updated:** April 13, 2026

---

## Current Architecture (WooCommerce)

```
┌─────────────────────────────────┐
│  Bookscan / Ebility             │
│  Shop PC (local)                │
│  Z:\bookscan (data on server)   │
└────────────┬────────────────────┘
             │
             │  woolibrary.dll
             │  e-Comms runs every 2 hours
             │
      ┌──────┴──────────────────────────────────┐
      │                                         │
      ▼  OUTBOUND (products + stock)            │  INBOUND (orders)
┌─────────────────────┐              ┌──────────┴───────────────────────┐
│ WooCommerce         │              │ Barcode Solutions                │
│ REST API            │              │ Heroku Middleware                │
│ (Book Hub key ID:7) │              │ booksellers-155024375aa1         │
└─────────┬───────────┘              │ .herokuapp.com                   │
          │                          └──────────┬───────────────────────┘
          ▼                                     ▲
┌─────────────────────┐              ┌──────────┴──────────┐
│ WooCommerce Site    │──webhooks───▶│ 3 active webhooks   │
│ A2 Hosting          │              │ product.created     │
│ (Shanti reseller)   │              │ product.updated     │
└─────────────────────┘              │ product.deleted     │
          │                          └─────────────────────┘
          │ REST API v3
          ▼
┌─────────────────────┐
│ eShip (NZ Post)     │  pulls "completed" orders
│                     │  writes tracking note back
└─────────────────────┘
```

---

## Future Architecture — Option A (Shanti delivers)

Clean path. Shanti installs `shopifylibrary.dll` and updates the Heroku middleware for Shopify
webhooks. Everything works the same way as now, just pointed at Shopify instead of WooCommerce.

```
┌─────────────────────────────────┐
│  Bookscan / Ebility             │
│  Shop PC (local)                │
└────────────┬────────────────────┘
             │
             │  shopifylibrary.dll  ← needs to exist at
             │  e-Comms every 2hrs    C:\Program Files (x86)\Bookscan\
             │
      ┌──────┴──────────────────────────────────┐
      │                                         │
      ▼  OUTBOUND (products + stock)            │  INBOUND (orders)
┌─────────────────────┐              ┌──────────┴───────────────────────┐
│ Shopify Admin API   │              │ Barcode Solutions                │
│                     │              │ Heroku Middleware                │
│                     │              │ (updated for Shopify)            │
└─────────┬───────────┘              └──────────┬───────────────────────┘
          │                                     ▲
          ▼                          ┌──────────┴──────────┐
┌─────────────────────┐              │ Shopify webhooks    │
│ Shopify Store       │──webhooks───▶│ order.created etc   │
│ (bmbooks.co.nz)     │              └─────────────────────┘
└─────────────────────┘
          │
          │ native integration
          ▼
┌─────────────────────┐
│ eShip (NZ Post)     │
│ eShip > Integrations│
│ > Shopify           │
└─────────────────────┘
```

**Risk:** 100% dependent on Shanti. `shopifylibrary.dll` confirmed absent from `C:\Program Files (x86)\Bookscan\` (screenshot 12 April 2026) — this is not a config change, Barcode Solutions must build and install a new DLL. Significant development work. Do not rely on this path.

---

## Future Architecture — Option B (Custom Python — CONFIRMED PATH)

POC confirmed working 13 April 2026. Shanti is off the critical path entirely.
Everything runs on the shop machine — no cloud server, no Google Drive, no external dependency.

```
┌──────────────────────────────────────────────────────────┐
│  SHOP MACHINE (always on)                                │
│                                                          │
│  Z:\bookscan\*.dbf  (product + stock data)               │
│                                                          │
│  ┌─────────────────────────────────────────────────┐     │
│  │  BMBooks Sync Tool (Python + tkinter GUI)        │     │
│  │                                                  │     │
│  │  [  Synchronize Now  ]  — manual trigger         │     │
│  │  Live activity log + summary stats               │     │
│  │  Also runs automatically via Task Scheduler      │     │
│  └──────────────┬───────────────────────────────────┘     │
│                 │                                        │
│    OUTBOUND (every 2 hrs, delta only)                    │
│    Read changed DBF records → push to Shopify API        │
│                 │                                        │
│    INBOUND (every 2 hrs, Phase 2)                        │
│    Poll Shopify for new orders → deduct stock in DBF     │
│                                                          │
└──────────────────────────────────────────────────────────┘
             │                        ▲
             │ Shopify Admin API       │ Shopify Admin API
             ▼  (products/stock)      │  (orders)
┌─────────────────────────────────────────────┐
│  Shopify Store (bmbooks.co.nz)              │
│                                             │
│  Products, inventory, metafields            │
│  (author, ISBN, pub date, pages)            │
└─────────────────────────────────────────────┘
             │
             │ native integration
             ▼
┌─────────────────────┐
│  eShip (NZ Post)    │
└─────────────────────┘
```

**Phase 1 — Outbound sync (products + stock):**
- Reads Bookscan DBF files directly from Z:\bookscan
- Delta sync — only processes records changed since last run (2–5 min per cycle)
- Pushes title, price, ISBN, weight, format, description, author, stock to Shopify
- Runs every 2 hours via Windows Task Scheduler
- Manual trigger available via GUI ("Synchronize Now" button)
- POC confirmed working with WooCommerce CSV data (13 April 2026)

**Phase 2 — Inbound sync (Shopify orders → Bookscan stock):**
- Same script, same schedule — polls Shopify for new orders since last run
- Deducts quantities from Bookscan stock DBF
- No webhook server needed — polling approach is simpler and more reliable
- Requires DBF write safety confirmation (file locking while Bookscan is running)

**GUI (Phase 2):**
- tkinter desktop app — one window, one button
- Same UX as current Bookscan eComms > Synchronize
- Shows live activity log and summary: products updated, orders processed, errors
- Louisa or any staff member can trigger manually

---

## Comparison

| | Option A (Shanti) | Option B (Custom) |
|---|---|---|
| Dependency | Barcode Solutions | Lance / us |
| Build time | Days (if he delivers) | 1–2 weeks |
| Reliability | Unknown | High (we control it) |
| Products → Shopify | shopifylibrary.dll | Python + DBF files |
| Orders → Bookscan | Updated Heroku middleware | Python webhook receiver |
| Long-term | Fragile (tied to Shanti) | Owned by BMBooks |

**Recommendation:** Option B is the confirmed path. Shanti is off the critical path.
- shopifylibrary.dll confirmed absent (13 April 2026)
- Shanti unresponsive to email and text from Louisa
- POC confirmed working (13 April 2026) — all tests passed
- Option A is no longer being pursued
