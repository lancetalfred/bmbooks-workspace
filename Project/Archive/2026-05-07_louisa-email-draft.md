# Email draft — Louisa, status codes & department exclusions

**To:** bmbooksellers@gmail.com
**From:** lance.t.alfred@gmail.com
**Subject:** Bookscan sync — quick sign-off on status codes & departments

---

Hi Louisa,

Thanks for running the purge — really helpful to be working off the cleaned data.

I've pulled the full list of status codes and departments straight out of the Bookscan tables so we can lock down what the sync tool should and shouldn't push to Shopify. For each code I've included a real book example — title and ISBN/SKU — so you can look it up in Bookscan and check that the code matches what you see on screen.

A small heads-up first: a few codes I jotted down on our call didn't quite match what's actually in the data. Most likely I just misheard:

- "ATT" → actually **`ACT`** (Active)
- "NYPA" → actually **`NYP`** (Not Yet Published)
- "RMC" → actually **`RUC`** (Reprint Under Consideration)
- "MLIP" and "TLE" → couldn't find these in the data — were these something else?
- "GFA" department → likely **`GFS`** ("Gifts - non web") — does that ring a bell?

---

## Master record count — before vs after your purge

| | Total records in MASTER |
|---|---:|
| Before purge (2026-04-13) | 133,752 |
| After purge (2026-05-07) | **117,282** |
| Removed | −16,470 (−12%) |

Almost all of the removals were old `ACT` (Active) records — likely dead SKUs you cleaned up. Good baseline to work from.

---

## Section 1 — Status codes (CSTATUS field on Title Master)

The Bookscan status table has 30 codes, and each one has a built-in **"Not for Web"** flag. My recommendation is for the sync tool to follow that flag by default — but I'd love your confirmation on two things:

> **❓ Question A:** Does the split below (web-allowed vs not-for-web) match how you'd want the website to behave? In other words — is "Bookscan says NOWEB=True" a fair definition of "do not put on Shopify"?
>
> **❓ Question B:** For each code below, can you check a sample book in Bookscan and confirm the code on screen matches what's in the table? I've included a real book per code so you can look one up.

### 1a — Web-allowed statuses (NOWEB=False) → would sync to Shopify

| Code | Meaning | Books with this status | Example title | ISBN/SKU |
|---|---|---:|---|---|
| ACT | Active | 110,206 | Classroom Set Of Dice | 011083117028 |
| NYP | Not Yet Published | 323 | Diary Of A Wombat | 9780007212071 |
| TOR | To Order | 199 | Tied Up In Tinsel | 9780008511012 |
| TOS | Temporarily out of Stock | 98 | Political Globe - 28cm | 4893338928070 |
| POD | Print On Demand | 64 | Fish In the Swim of the World | 9781761047343 |
| BO | Back Order | 4 | How To Drive | 9781447272847 |

### 1b — Not-for-web statuses (NOWEB=True) → would NOT sync to Shopify

| Code | Meaning | Books with this status | Example title | ISBN/SKU |
|---|---|---:|---|---|
| OP | Out of Print | 4,758 | Kandinsky Eraser | 4031172431282 |
| AD | Not To WEB | 1,159 | Foam Dice 50mm Assorted | 50MMDICE |
| OSI | Out of Stock Indefinitely | 118 | Villazon Verdi | 028947794608 |
| RP | Reprinting | 54 | Against The Odds (NZ Women Doctors) | 9781991016980 |
| RUC | Reprint Under Consideration | 38 | Room Of Ones Own - Penguin Notebook | 5060121244245 |
| NOR | No Rights in NZ | 19 | On Killing | 9780316040938 |
| PBA | Publication Abandoned | 16 | Magic of Sleep / Science of Dreams | 9780241444146 |
| ASC | Awaiting Supplier Confirm | 14 | What Am I Supposed To Eat | 9780473397081 |
| NLA | No Longer Available | 12 | Yikerz | 824284900456 |
| PBD | Publication Delayed | 11 | Sword Of Shadows - 5 | 5SWORDOFSHADO |
| PDR | Publisher Cannot Be Found | 10 | Footsteps Of Fire (Ngati Dread) | 9780473135225 |
| ORD | Order Direct | 9 | Animal Welfare in New Zealand | 9780473244262 |
| NLD | No Longer Distributed NZ | 8 | Thank You for Feeding Freckle | 9781922385017 |
| PUA | Publication Cancelled | 5 | Life On A Knife's Edge | 9780241461846 |
| CHP | Check Price Each Time | 5 | Te Kakano - Te Whanake 1 | 9780582543287 |
| OLD | Old Edition - New Available | 4 | Last Kings of Shanghai | 9780735224414 |
| INT | Internet Only Purchase | 2 | Road to Monaco (Ganley) | 9780993139505 |
| NOT | No Listing Found | 2 | Te Poi Koiora | 9781486001569 |
| WFC | Waiting for Confirmation | 1 | 5 May Series | MAYSERI5 |
| RE, SOR, SOE, OIW, OC | (various) | 0 | (no books currently use these) | — |

---

## Section 2 — Status code anomalies (need your call)

These are records where the status code either **isn't in the Bookscan status table** or looks like a typo. Roughly 140 books in total. I'd like your guidance on each group:

| Status code | Books | Example | ISBN/SKU | What I think this is |
|---|---:|---|---|---|
| *(blank)* | 69 | Letters from Father Christmas | 9780001374638 | No status set |
| `10` | 20 | Quite (Claudia Winkleman) | 9780008421663 | Legacy numeric code? |
| `21` | 19 | Stone Cold | 9780141368993 | Legacy numeric code? |
| `40` | 10 | Collins English Dictionary | 9780007426942 | Legacy numeric code? |
| `22` | 8 | Yuli: The Carlos Acosta Story | 9780007250783 | Legacy numeric code? |
| `31` | 7 | Natural Way to Draw | 9780285638389 | Legacy numeric code? |
| `30` | 2 | Code Name Verity | 9781405278423 | Legacy numeric code? |
| `47` | 1 | Black Stallion Legend | 9780394960265 | Legacy numeric code? |
| `97` | 1 | Haruru Mai (Briar Grace-Smith) | 9780908607440 | Legacy numeric code? |
| `43` | 1 | Adventures Of Superman Vol. 2 | 9781401250362 | Legacy numeric code? |
| `AC` | 4 | Campbell Biology | 9780134093413 | Typo for `ACT`? |
| `PO` | 1 | Christian Slaves, Muslim Masters | 9781403945518 | Typo for `POD`? |

> **❓ Question C:** For each row above, what should the sync do — hold these back, treat them as the "corrected" version, or sync as-is until you fix them in Bookscan?

---

## Section 3 — Departments to exclude from sync

You confirmed `AAA` on the call. Below are the other operational / non-retail departments — for each one I'd like a yes/no on whether it should be excluded.

**My recommendation is to exclude these three:**

- **`VOU` (BMB Vouchers)** — we're setting up Shopify's built-in digital vouchers, so the Bookscan voucher SKUs shouldn't double up on the site
- **`FRE` (Freight)** — Shopify has its own freight handling at checkout; the DHL Fast Freight SKU isn't a retail product
- **`TOK` (Tokens)** — same logic as vouchers, not really a sellable book product

For the rest in the table — let me know how you'd like the sync to handle them.

> **❓ Question D:** Confirm the three exclusions above, and tell me which of the others (if any) should also be excluded.

| Code | Name | Books | Example | ISBN/SKU | Lance's rec |
|---|---|---:|---|---|---|
| AAA | Dept To Be Assigned | 2,754 | Colour Mini Puzzles | 4031172172017 | **Exclude** (already confirmed) |
| GFS | Gifts - non web | 111 | UFO Spacey | 678643808750 | Name says "non web" — your call |
| SPE | Specials | 22 | One Minute Crying Time | 9780995122956 | Your call |
| VOU | BMB Vouchers | 14 | $90 BMB Voucher | BMBVOU90 | **Exclude** (Shopify digital vouchers instead) |
| FRE | Freight | 9 | DHL Fast Freight | DHLFASTF | **Exclude** (Shopify built-in freight) |
| XXX | *(blank name)* | 8 | Paris Book of Labels | 9780735329379 | Your call |
| TOK | Tokens | 7 | Book Token $10 | 9415555260105 | **Exclude** (same as vouchers) |
| MAG | Magazines and Newspapers | 2 | Takahe Magazine #92 | TAKAHE92 | Your call |
| MON, EXP, POS, STK, FUN, KIT | (no books currently) | 0 | — | — | No-op (zero books) |
| *(blank dept)* | No dept set | 145 | Letters from Father Christmas | 9780001374638 | Your call |

---

## Summary of what I need from you

1. **Question A** — Confirm "follow Bookscan's NOWEB flag" is the right rule for what syncs to Shopify
2. **Question B** — Spot-check a few codes in Bookscan to confirm they match the table above
3. **Question C** — How to handle the anomaly statuses (blanks, numerics, AC/PO typos)
4. **Question D** — Confirm `VOU`, `FRE`, `TOK` for exclusion (plus `AAA`), and tell me which of the others should also be excluded

Take your time — happy to chat through any of these on Monday too if it's easier.

Cheers,
Lance
