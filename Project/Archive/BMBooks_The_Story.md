# The BookKeeper Chronicles
*Last updated: June 2, 2026*

---

## ACT ONE — The World We Inherited

Picture a bookshop that has outlasted everything. Nearly thirty years on the same street in Palmerston North, next door to the city library, run by a woman named Louisa who knows her customers by name and knows her books like old friends.

But behind the warmth of the shop floor, the machinery is creaking. The website runs on WordPress. The product catalog — 38,000 books — lives in an ancient database format from the 1980s called DBF. And the company that bridges those two worlds, a business called Barcode Solutions, has quietly become the single most dangerous dependency in the operation. They host the website. They own the sync software. And their CEO, Shanti, is the only person on the planet who can make any of it work.

This is the world Lance inherits when he starts the migration to Shopify.

---

## ACT TWO — The Villain Reveals Himself

The plan seems straightforward. Shopify has a connector for Bookscan. Email Shanti, get it set up, go live. Simple.

Shanti doesn't reply.

Lance emails again. Louisa texts him. Lance tries to call. Shanti cancels the call.

Weeks pass.

Then comes the forensic work — the moment our hero starts pulling at threads. Louisa sends over some DLL files from the shop machine. Lance cracks them open and finds the truth: Shanti's entire contribution to the WooCommerce integration was **one class and one method**. A four-function HTTP wrapper. That's it. No secret sauce. No complex engineering. Just a thin wrapper around a public open-source library.

And the Shopify version — `shopifylibrary.dll` — **doesn't exist**. Not installed. Not built. Not started.

Shanti wasn't ignoring them because he was busy. He was ignoring them because he had nothing to give.

The villain in this story doesn't wear a mask. He just doesn't answer his phone.

---

## ACT THREE — We Build It Ourselves

This is where the movie shifts gear.

If the tool doesn't exist, you build it. Lance maps every DBF file on the shop machine — MASTER, PUBLISHER, WEBLIST, WEBMAINCAT, WEBSUBCAT — 133,000 records, joined on ISBN, yielding 38,000 books ready to sync. He writes `bookscan_sync.py` from scratch. Delta sync, MD5 hashing, cover images, category tags, metafields, error handling, logging. The whole thing.

Then comes the remote access saga. The shop machine is Windows-only. Lance is on a Mac. FortiClient won't work. TeamViewer is blocked by his employer. Every door closes. Then Chrome Remote Desktop — a solution so simple it was almost overlooked — opens the last one.

The dev store tests pass. The production dry run against the live store returns **37,998 products, 0 errors**.

Shanti is officially off the critical path. The shop is free.

---

## ACT FOUR — The Arsenal Assembled

With the sync script battle-tested, Lance turns to everything else. The Shopify store takes shape:

The theme goes up in dark purple. The gift cards are configured with data from five years of sales history. Metafield definitions are created with a single API call. Seventy-five collections — smart, tag-driven, SEO-optimised — are built and waiting. The navigation menu goes live. The footer, the homepage sections, the URL redirects, the package profiles, eShip connected for NZ Post label printing and tracking. Every checkbox ticked.

But there is one decision in this act that matters more than the rest.

Louisa isn't technical. If the sync runs silently in the background, she'll have no idea whether the website updated this morning or three weeks ago. She'll phone. She'll worry. She'll lose trust in the whole thing. So Lance builds her a desktop GUI — a small window on her shop computer with a status light, a product count, a last-run timestamp, and a scrolling log. No terminal. No command line. Just a dashboard she can glance at between customers.

It's a forty-minute build. It will save a hundred phone calls.

The store sits behind a password, fully loaded, coiled like a spring.

---

## ACT FIVE — Tuesday

The sync runs.

Chrome Remote Desktop connects Lance to the shop machine. Python is installed. The script copies across. The dry run confirms 37,998 records. And then — with Louisa watching — the first full sync begins.

It doesn't go cleanly at first. Windows Task Scheduler, it turns out, can't resolve mapped network drives. The script reaches for `Z:\bookscan` and finds nothing. One more obstacle, one more morning of diagnosis. The fix is unglamorous: swap every mapped drive path for its UNC equivalent. `Z:\bookscan` becomes `\\Server\c\bookscan`. Redeploy.

The second run completes without error. 34,500 books flow from a 1980s database in Palmerston North to a global e-commerce platform. By morning, the shelves are stocked.

The hourly sync kicks in. Every sixty minutes, the shop machine checks for changes — new stock, price updates, cover images — and pushes them live. Bookscan and Shopify are, for the first time, one system.

---

## ACT SIX — The Last Mile

The store is ready. It just isn't open yet.

Products sit in Draft status, invisible to the public, waiting for the moment Louisa says go. The domain is still pointed at the old WordPress site. A final checklist runs through UAT: mobile review (72% of BMBooks traffic is on phones), email notifications, order fulfillment walkthrough with Louisa, a page-by-page sign-off.

On go-live day, one command bulk-activates 34,500 products. A domain switch, handled with Black Sheep Design, cuts over the URL. Searchanise re-indexes. Collections populate. The store opens.

Twenty-nine years of bookselling. Thirty minutes of commands.

---

## THE POST-CREDITS SCENE — The Real Fight

But as the credits begin to roll, the camera lingers on Louisa at her desk.

A Shopify order notification appears on her screen. She opens it, opens Bookscan, and begins to type. Customer name. Delivery address. ISBN. Title. Quantity. Price. Line by line, by hand, the same way she has done it for every single online order.

*"We physically have to cut and paste every fucking line."*

Phase 1 solved the outbound problem — books flowing from Bookscan to Shopify. But the inbound problem — every online order feeding back into Bookscan manually — that's the fight that's still coming.

Phase 2 is already scoped. Poll the Shopify orders API. Parse the line items. Write back to the Bookscan DBF directly. The architecture is understood. The file-locking risks are identified. The only thing standing between Louisa and a fully automated loop is time.

Unlike Shanti, we know exactly what we're building.

---

*To be continued.*

---

## ACT EIGHT — Louisa Sees It

There is a moment in every migration when the work stops being theoretical.

For BMBooks, that moment happened on a Sunday morning in June. Lance shared his screen, Louisa put down whatever she was doing, and for the first time the store appeared as something real — not a staging URL, not a work in progress, but a bookshop. Her bookshop. On the internet.

She noticed the cream background immediately. *"I didn't even notice. That's great."* That is the correct response to a good design decision. The best ones go unnoticed.

She noticed the mega menu — Fiction with its subcategories, Crime & Thriller, now Horror and Manga and Romance alongside it, the Manawatū section front and centre. She noticed the breadcrumbs on the product page, the book details pulling from Bookscan, the wishlist working exactly as you'd expect. She noticed that the test order went through without a problem, that the fulfillment flow was simpler than WooCommerce, that the abandoned checkout was right there in the orders tab.

She also noticed things that needed work. The "available to order" messaging was wrong — it said one to two business days, which is only true on a good day when the book happens to be warehoused in Auckland. She noticed that Australian customers pay upfront and sometimes cancel when they find out what shipping costs, losing Louisa the transaction fee both ways. She noticed that gift cards are complicated when someone wants a physical voucher to give as a present.

These are not failures. These are exactly the things you find when you show a real operator a real system. Every one of them is a solvable problem.

Meanwhile, in Australia, a company called FRANZ Technologies sent a letter. They had acquired Bookscan from Shanti. Michael and Vincent were staying on. Monthly releases were planned.

And on the shop machine in Palmerston North, the old WordPress site was returning 403 Forbidden — the IP blocked during the handover. Lance found the public IP, drafted the email to FRANZ, and moved on.

The old site going dark is not a crisis. It is a calendar.

*To be continued.*

---

## ACT SEVEN — The Invisible Librarian

There is a librarian at every bookshop who nobody sees.

Not Louisa. Louisa is very visible — behind the counter, recommending books, knowing her regulars by name. The invisible librarian is the one who decided, thirty years ago, that this book goes on *this* shelf, under *this* sign. Who built the system of labels that lets a customer walk in, say "I want something scary", and be pointed to exactly the right place.

For thirty years, that invisible librarian at BMBooks has been Louisa and her staff, entering categories by hand into Bookscan. And over thirty years, the categories have drifted. Romance was never set up as a category — those books were filed under "General Fiction" and hoped to be found. Horror the same. The shop carries 220 romance novels and 130 horror novels. Not one of them had a sign.

The fix, it turned out, was already sitting in the database.

Nielsen — the same company that runs Bookscan — classifies every published book in the English-speaking world using a system called BIC. Publishers submit a BIC code when they register a title. It's the professional standard. And that code, it turns out, had been flowing silently into the shop's DBF files for years, filed away in a field called `BICMAIN` in `PUBLISHER.DBF`, covering 90% of the catalogue. Nobody had looked at it.

Once the field was found, the rest was cartography.

A script read each book's BIC code, cross-referenced it against a 2,616-entry taxonomy, and mapped it to a BMBooks genre tag. Romance novels — wherever they were hiding — surfaced. Horror books, Manga, Thrillers: all found. Books that belonged in two collections were flagged for both. A historical romance would appear in Historical Fiction *and* Romance. Lovecraft would appear in Classics *and* Horror. Dante's *Inferno* — correctly identified as Poetry — would finally appear alongside Yeats and Sappho.

But before a single tag touched the live store, the dataset was stress-tested.

A validation agent was run across all 3,680 proposed changes. It came back with six systematic errors — places where the BIC code taxonomy had been misread and was about to tag graphic design books as Architecture, art history books as Craft, and parenting books as Psychology. Each one fixed. The final number: 3,166 changes, all correct.

*"My job depends on this,"* Lance said before running the validation.

That is the right sentence. Not because the stakes are dramatic — the world will not end if a quilting book is briefly miscategorised. But because it's the correct way to approach a catalogue of 43,000 books that a real woman has spent thirty years building. You don't rush it. You check it twice. You run the agent. You fix the errors.

The invisible librarian, for the first time in thirty years, has an assistant.

---

*To be continued.*
