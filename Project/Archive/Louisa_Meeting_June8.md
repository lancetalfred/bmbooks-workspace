# Louisa Meeting — June 8, 2026
**Goal:** Lock down the remaining decisions needed before go-live.

---

## BLOCK 1 — Go-Live Decisions (must resolve today)

---

### 1. Go-live timing
**What it is:** Pick a date and time to flip the switch — activate all 34,500 products and point bmbooks.co.nz at the new site.
**Why it matters:** Everything else (social posts, email to customers, Abbey at Black Sheep) needs to be coordinated around this date. Nothing can be booked until we have it.
**Question:** What date works for you? Do you want to do it together or are you happy for Lance to handle it?

---

### 2. Order fulfillment walkthrough (live demo)
**What it is:** A end-to-end demo of what happens when a customer places an order — from the customer's experience through to Louisa fulfilling and dispatching it.
**Why it matters:** This is the one thing Louisa must be comfortable with before go-live. Everything else can be fixed post-launch. This cannot.

#### Step A — Place two test orders (as a customer)
Use Shopify's test payment gateway so no real money moves.
- **Order 1:** NZ delivery (North Island address) — 1–2 books
- **Order 2:** Australia delivery — 1–2 books
- Show Louisa what the customer sees: product page → cart → checkout → payment → confirmation page

#### Step B — Customer confirmation email
- Open the order confirmation email that lands in the customer's inbox
- Show: what it looks like, what information it contains, BMBooks branding
- Note: Louisa can customise the wording in Shopify admin → Settings → Notifications

#### Step C — Louisa views the new order
- In Shopify admin → Orders — show the new orders appearing
- Walk through the order detail: customer name, address, items, payment status
- Show the difference between NZ and AU orders (shipping method, address format)
- Show how to add an internal note if needed

#### Step D — Tracking number (manual vs automated)
- **Pre-eShip (day one):** Louisa manually enters the NZ Post tracking number
  - Orders → open order → Fulfill → enter tracking number → Send shipment notification to customer
  - Customer receives a shipping notification email with the tracking number
- **Post-eShip (once connected):** eShip generates the label and tracking number automatically
  - eShip prints the NZ Post label directly from the order
  - Tracking number flows back into Shopify automatically — no manual entry
  - Confirm: is eShip already connected and ready, or is this a post-go-live setup step?

#### Step E — Fulfilling the order
- Mark as Fulfilled once the parcel is packed and ready
- Show the fulfillment confirmation email that goes to the customer
- **AU orders:** Louisa calculates actual shipping cost, sends customer a Shopify payment link before dispatching (same process as now — $0 charged at checkout)
- Show how to add the AU shipping charge as a manual payment link

#### Step F — Cancelling an order
- Orders → open order → More actions → Cancel order
- Choose whether to refund the customer (full / partial / none)
- Show the cancellation email that goes to the customer
- Note: a cancelled order cannot be reopened — if a customer wants to amend, cancel and have them re-order

#### Step G — Refunds
- Orders → open order → Refund
- Can refund specific line items or the whole order
- Shopify sends the refund back to the original payment method automatically

---

### 3. Launch communication
**What it is:** Telling customers the new site exists.
**Why it matters:** Returning customers will land on a completely different-looking website with no context. Without a heads-up, some will think the shop has closed or been hacked.
**Questions:**
- Announcement banner on the site? (e.g. "We've got a new look — same great books")
- Email to existing customer list?
- Facebook/Instagram post?
- Does Louisa want to write it, or is Lance drafting?

---

## BLOCK 2 — What Goes on the Website (needs Louisa's call)

---

### 4. Out-of-stock books — confirm the rule
**What it is:** Bookscan has a built-in flag (NOWEB) that marks certain books as "do not put on the website." Lance's recommendation is to follow that flag — if Bookscan says don't show it, Shopify won't show it.
**Why it matters:** Currently only 3 codes are excluded (OP, RP, RUC = 4,850 books hidden). Expanding to the full NOWEB list adds ~2,400 more books that Bookscan itself says shouldn't be on the web — titles like "No Rights in NZ", "Publication Abandoned", "No Longer Available".
**Question A:** Is "follow Bookscan's own NOWEB flag" the right rule — if Bookscan says hide it, Shopify hides it?

Additional codes that would be excluded if we follow NOWEB fully:

| Code | Meaning | Books |
|---|---|---|
| OSI | Out of Stock Indefinitely | 118 |
| NOR | No Rights in NZ | 19 |
| PBA | Publication Abandoned | 16 |
| ASC | Awaiting Supplier Confirm | 14 |
| NLA | No Longer Available | 12 |
| PBD | Publication Delayed | 11 |
| PDR | Publisher Cannot Be Found | 10 |
| ORD | Order Direct | 9 |
| NLD | No Longer Distributed NZ | 8 |
| PUA | Publication Cancelled | 5 |
| CHP | Check Price Each Time | 5 |
| OLD | Old Edition — New Available | 4 |
| INT | Internet Only Purchase | 2 |
| NOT | No Listing Found | 2 |
| WFC | Waiting for Confirmation | 1 |

---

### 5. Books with unusual/missing status codes
**What it is:** ~140 books have status codes that aren't in Bookscan's own table — numeric codes (10, 21, 40 etc.) or what look like typos (AC instead of ACT, PO instead of POD).
**Why it matters:** The sync tool doesn't know what to do with these. Currently it passes them through to Shopify. They could be fine, or they could be books that shouldn't be on the site.
**Question C:** For each group, what should the sync do?
- **Hold them back** (don't show on website) until Louisa fixes them in Bookscan
- **Treat them as the nearest valid code** (e.g. AC → ACT = Active)
- **Sync them as-is** and clean up later

| Code | Books | Example |
|---|---|---|
| (blank) | 69 | Letters from Father Christmas |
| 10 | 20 | Quite (Claudia Winkleman) |
| 21 | 19 | Stone Cold |
| 40 | 10 | Collins English Dictionary |
| 22 | 8 | Yuli: The Carlos Acosta Story |
| AC | 4 | Campbell Biology (typo for ACT?) |

---

### 6. Departments to exclude from the website
**What it is:** Bookscan organises stock into departments. Some departments are internal (vouchers, freight) and should never appear as products on the website. Lance has already excluded AAA, VOU, FRE, TOK. Five more need a decision.
**Why it matters:** Getting this wrong puts internal SKUs (like "DHL Fast Freight" or "$90 BMB Voucher") on the public website.
**Question D:** For each of these — exclude from website or include?

| Code | Name | Books | Example | Lance's read |
|---|---|---|---|---|
| GFS | Gifts - non web | 111 | UFO Spacey | Exclude — name says "non web" |
| SPE | Specials | 22 | One Minute Crying Time | Your call |
| XXX | (no name) | 8 | Paris Book of Labels | Your call |
| MAG | Magazines | 2 | Takahe Magazine #92 | Your call |
| (blank) | No dept set | 145 | Letters from Father Christmas | Your call |

---

## BLOCK 3 — Website Naming & Navigation (Louisa's preference)

---

### 7. New genre collection names
**What it is:** The site now has five new genre sections — Romance, Horror, Manga, Thriller, and Translated Fiction — each with hundreds of books. They need names for the navigation menu.
**Why it matters:** These are customer-facing labels. "Thriller" vs "Crime & Thriller" is a meaningful choice — Crime Fiction is the existing collection and Thriller is new.
**Questions:**
- Crime Fiction + Thriller: keep separate, or merge as "Crime & Thriller"?
- Romance, Horror, Manga — happy with those names?
- Translated Fiction — in the nav, or footer/hidden for now (only 29 books)?

---

### 8. Duplicate collections — pick one name each
**What it is:** Four sets of collections that are accidentally showing the same books under different names. Need to pick one name per group and retire the others.
**Why it matters:** Customers (and Google) see duplicate pages — bad for navigation and SEO.
**Decision needed — one name per row:**

| Group | Option A | Option B | Option C | Books |
|---|---|---|---|---|
| History | History & Politics | Non-Fiction | Politics | 2,702 |
| Gifts | Gifts | Gifts & Stationery | Stationery | 2,000 |
| Biography | Biographies (1,512) | Biography (1,369) | — | — |
| Garden | Gardening | The Garden | — | 346 |

---

## BLOCK 4 — Quick Confirms (yes/no)

---

### 9. NZ shipping rates
**What it is:** Simplifying NZ shipping to 3 flat rates: North Island $10.99, South Island $13.99, Rural $16.99.
**Why it matters:** The current setup is complex. Flat rates are easier for customers to understand and reduce abandoned carts.
**Status:** Text sent — awaiting reply. Confirm yes/no today.

### 10. Founding year — 1996 or 65 years?
**What it is:** Google Business Profile shows the store opened December 1996 — making it ~29 years old, not 65. The "65 years" claim has appeared in some marketing copy.
**Why it matters:** Using the wrong number publicly is a credibility risk.
**Question:** Can Louisa confirm the correct founding year?

### 11. Bookscan categories going forward
**What it is:** Now that the site automatically assigns genres (Romance, Horror, Manga etc.) from Nielsen's BIC codes, there are two paths for new books: (A) Louisa continues assigning SUBCAT in Bookscan manually, or (B) the enrichment script handles new books automatically.
**Why it matters:** Determines whether Louisa needs to do anything differently when adding new stock.
**Question:** Would Louisa be willing to add Romance, Horror, Manga, Thriller as Bookscan categories so new books get assigned correctly at the source? (Not urgent — worth flagging.)

---

## DEFER — No action today

- Format codes (FO, CS, SL etc.) — post-go-live, 10-min session
- Bookscan back-population (Phase 2)
- Status code spot-check (Question B) — Louisa can do async
- AU shipping — already confirmed ($0 at checkout, manual invoice)

---

*Items 7, 11 from original agenda already answered — skipped.*
