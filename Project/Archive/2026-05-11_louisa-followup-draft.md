# Email draft — Louisa, follow-up on status codes

**To:** bmbooksellers@gmail.com
**From:** lance.t.alfred@gmail.com
**Subject:** Bookscan sync — quick follow-up, just one decision left

---

Hi Louisa,

Thanks for getting back on those — really helpful. Recapping where we've landed:

- **Status codes to never sync:** `OP`, `RP`, `RUC` ✓
- **Departments to exclude:** `VOU`, `FRE`, `TOK`, `AAA` ✓
- **Your spot-check (Question B):** no rush, take your time
- **Anomaly records (Question C):** noted, holding for your sign-off

---

## Quick answer to your "can we update after sync?" question

Yes — and I'll make it easier in advance. I'm going to add the Bookscan **status code** and **department code** into each Shopify product record as hidden tags. That way, if down the line you decide a code should be excluded that we didn't catch today, finding and removing those products is a 30-second filter in the Shopify admin rather than a script run. Same goes for anomaly records — once you decide what to do with them, the cleanup is point-and-click.

So your instinct is right: we can fix things post-sync. I'll just make sure the data's there to make it painless.

---

## One thing worth a second look before we lock in `OP` / `RP` / `RUC`

I ran the full numbers against your latest MASTER file, and the picture for the codes you didn't pick is a lot smaller than the table I sent on Wednesday implied. **Most of those codes don't carry any stock at all.** That matters because if we don't exclude them, they'd appear on Shopify as zero-stock products displaying "Available to order" — customers could attempt to order them, but you wouldn't actually be able to fulfill.

Here's the real-world impact:

| Code(s) | Would sync to Shopify | Of those, with stock |
|---|---:|---:|
| `AD` ("Not To WEB") | 240 | **6** |
| 15 other NOWEB-flagged codes combined (`OSI`, `NOR`, `PBA`, `NLA`, `PBD`, etc.) | 18 | 0 |
| **Total** | **258** | **6** |

The 252 zero-stock products are the real concern — they'd be visible on the site, customers could place orders, but nothing would ship. The six AD books with stock are the only ones with any real upside if synced.

Two ways to handle this:

> **Option 1** — *Follow Bookscan's NOWEB flag.* Exclude everything Bookscan itself flags as Not-For-Web. One rule, covers all 16 codes. Practical effect: 258 books stay off the site, including the six AD books with stock (which I'd want you to look at — see below).
>
> **Option 2** — *Keep `OP` / `RP` / `RUC` only.* The 252 zero-stock NOWEB books will appear on Shopify as "Available to order". You'd want to handle each one if a customer ever tries to order it.

---

## The six AD books that actually have stock

These are the only ones where the decision today matters in any tangible way. They're all flagged `AD` ("Not To WEB") in Bookscan:

| ISBN | Title | Stock | Price |
|---|---|---:|---:|
| 9781576871386 | Juvenile | 1 | $24.99 |
| 9781781318072 | Classic FM Family Music Box | 1 | $34.99 |
| 9781838697068 | Canada – Lonely Planet | 1 | $44.99 |
| 9781838699048 | Montreal And Quebec City – Lonely Planet Pocket | 1 | $24.99 |
| 9781861269720 | Yorkshire Dales – Landscape and Geology | 1 | $59.99 |
| 8057094921768 | Van Eyck – 2026 Bookmark Calendar | 1 | $9.99 |

Two ways to read these:

- They're genuinely "Not To WEB" for an operational reason (returns, supplier issue, sample copies, etc.) → Option 1 catches them correctly
- They got mis-tagged `AD` historically and forgotten → re-categorise them in Bookscan and they'll start syncing automatically next run

---

## What I need from you

> **Question E:** Option 1 (follow NOWEB across the board) or Option 2 (your original `OP` / `RP` / `RUC` only)?

If Option 1, I'll wire it in and we're done with status codes for go-live (your Question B spot-check still applies whenever you get to it).

If Option 2, we're already done — no further changes needed.

No rush — happy to chat through any of this on Monday.

Cheers,
Lance
