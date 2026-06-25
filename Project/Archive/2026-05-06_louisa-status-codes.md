# Memo — 2026-05-06 (updated 2026-05-07)

## Topic: Louisa call — Bookscan status codes, departments, and sync behaviour

---

## Update 2026-05-07 — full lists pulled from refreshed DBFs

Louisa ran a purge on MASTER and related DBFs on the server. Fresh copies of `MASTER.DBF`, `STATUS.DBF`, and `DEPT.DBF` taken **2026-05-07** and saved to `Sync/SABSSAVE/`. Old Apr 13 copies preserved as `*.DBF.2026-04-13` for diff.

**Purge impact:** MASTER dropped from 133,752 → 117,282 records (−12%), almost all from `ACT`-status SKUs. Anomaly codes and exclusion candidates essentially unchanged.

---

## Key Finding: Status field — confirmed from data

- DBF field name on MASTER.DBF: **`CSTATUS`** (3 chars, type C) ✅ confirmed
- Department field on MASTER.DBF: **`DEPARTMENT`** (3 chars, type C) ✅ confirmed
- Lookup tables: `STATUS.DBF` (30 status codes) and `DEPT.DBF` (78 departments)
- **`STATUS.DBF` has a `NOWEB` boolean column** — Bookscan's own opinion on which statuses shouldn't be web-visible. Strong default for the sync filter.

---

## ⚠️ Corrections to codes captured on the call

What Louisa recalled didn't quite match the actual data. Worth flagging gently in the email so she can verify on screen.

| Memo said | Actual code | Notes |
|---|---|---|
| `ATT` (Active) | **`ACT`** | 110,206 records — definitely the active code |
| `NYPA` | **`NYP`** | Not Yet Published, 323 records |
| `RMC` (under consideration) | **`RUC`** | Reprint Under Consideration, 38 records |
| `MLIP`, `TLE` | *don't exist* | Ask Louisa what she meant |
| `GFA` (dept) | **`GFS`** ? | "Gifts - non web" — name is a strong hint |

---

## Status codes — full list with sync recommendation

Default rule: follow Bookscan's `NOWEB` flag.

### Web-allowed (NOWEB=False) → sync candidates

| Code | Name | Records |
|---|---|---:|
| ACT | Active | 110,206 |
| NYP | Not Yet Published | 323 |
| TOR | To Order | 199 |
| TOS | Temporarily out of Stock | 98 |
| POD | Print On Demand | 64 |
| BO | Back Order | 4 |

### NOT for web (NOWEB=True) → exclude candidates

| Code | Name | Records |
|---|---|---:|
| OP | Out of Print | 4,758 |
| AD | Not To WEB | 1,159 |
| OSI | Out of Stock Indefinitely | 118 |
| RP | Reprinting | 54 |
| RUC | Reprint Under Consideration | 38 |
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
| OLD | Old Ed - New Ed Available | 4 |
| INT | Internet Only Purchase | 2 |
| NOT | No Listing Found | 2 |
| WFC | Waiting for Confirmation | 1 |
| RE, SOR, SOE, OIW, OC | (various) | 0 |

### Anomalies — need Louisa's judgment

| Code | Records | Likely |
|---|---:|---|
| *(blank)* | 69 | No status set |
| `10`, `21`, `40`, `22`, `31`, `30`, `47`, `97`, `43` | 68 total | Legacy numeric codes |
| `AC` | 4 | Typo for `ACT`? |
| `PO` | 1 | Typo for `POD`? |

---

## Departments — full list

### Probably-exclude candidates (operational / non-retail)

| Code | Name | Records |
|---|---|---:|
| AAA | Dept To Be Assigned | 2,754 |
| GFS | Gifts - non web | 111 |
| SPE | Specials | 22 |
| VOU | BMB Vouchers | 14 |
| FRE | Freight | 9 |
| XXX | *(blank name)* | 8 |
| TOK | Tokens | 7 |
| MAG | Magazines and Newspapers | 2 |
| MON, EXP, POS, STK, FUN, KIT | (zero records each) | 0 |
| *(blank dept)* | 145 | No dept set |

### Retail departments (sorted by stock count)

CHI Childrens (23,895) · FIC Fiction (8,546) · HIS History and Politics (5,514) · ART Art/Design/Phot/Anti (4,771) · FOO Food and Wine (4,105) · CRI Crime Fiction (3,798) · BIO Biography/Autobgrphy (3,785) · EDU Educational (3,655) · CLA Classics (3,256) · STA Stationery (2,988) · CRA Craft (2,900) · JUV Juvenile (2,853) · SFF Sci-Fi Fantasy (2,622) · SCI Science (2,253) · PSY Psychology/Self Help (2,218) · CAL Calendar (1,964) · MUS Music/PerfArts (1,852) · GAM Games (1,714) · GRA Graphic Novels (1,621) · POE Poetry (1,520) · ENV Envrmnt/NatHst/Anmls (1,511) · SPO Sport (1,498) · BUS Business (1,486) · TRL Travel Literature (1,398) · HEA Health (1,276) · HIF Historical Fiction (1,260) · CDS CD Musical Recording (1,216) · GIF Gift books (1,176) · TRG Travel Guides (1,159) · REF Reference (1,106) · GAR Gardening (1,034) · NZF NZ Fiction (994) · LAN Languages (964) · MOT Motoring (911) · REL Religion (822) · NEW New Age (818) · EDS Study Guides (753) · NZH NZ Hist Maori Ref (727) · HUM Humour (705) · PHI Philosophy (667) · NZB NZ Biography (594) · MAP Maps (499) · FAS Fashion (499) · CAR Cards and Wrap (486) · NZE NZ Environment (485) · MAO Te Ao Maori (452) · FAM Family (440) · EMA Te Reo Maori/NZ (427) · TNZ Travel - NZ Aust Pac (312) · GEN Gender (293) · EEA Early Learning Educa (263) · CHR Christmas (257) · NZS NZ Sociology (254) · NZA NZ Art/Maori Art (250) · ESS Essays (236) · AUD Audio (202) · MYT Mythology (188) · PLA Plays (181) · COM Computing (134) · TCR True Crime (124) · ATG Atlases/Geography (120) · NZM NZ Military (103) · YOG Yoga Tai Chi (53) · NZL NZ Literature (47)

---

## Action items

- [x] Lance to verify `CSTATUS` field name on shop machine — done from DBF, field is `CSTATUS` (3 chars)
- [x] Pull full status code list and department list from Bookscan DBFs
- [x] Refresh DBFs after Louisa's purge
- [ ] Email Louisa with the lists for sign-off (in progress — see `2026-05-07_louisa-email-draft.md`)
- [ ] Update `bookscan_sync.py` to filter out excluded statuses + departments once Louisa confirms
- [ ] Lance to show Louisa the sync tool UI (she wants to see how it works)
- [ ] Louisa to demo how books are added to Bookscan via Nielsen/title page upload — understand the flow for Lance

---

## Separate issue noted: Nielsen price sync gap

Bookscan pulls book data (including price) from Nielsen/title page when a book is first added. But price updates from Nielsen are **not automatically synced** — they only update if manually triggered in Bookscan. This means:

- A book's price can go stale in Bookscan
- Customer buys on Shopify at old price
- Louisa reorders and discovers price has increased
- BMBooks wears the difference

Existing problem predating Shopify. Not in scope to fix now but worth flagging as a future improvement (scheduled Nielsen price delta sync).

---

## Next session

Louisa available Monday (Ted back in school full day). Lance to message to confirm time.
