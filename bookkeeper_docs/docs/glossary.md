---
sidebar_position: 7
---

# Glossary

Plain-English explanations of terms used throughout these docs.

---

**Bookscan**
The point-of-sale and inventory system used in the BMBooks shop. It handles in-store sales, stock levels, product details, ordering from suppliers, and reporting to NielsenBookScan. It stores all its data in files on the shop computer.

**BookKeeper for Shopify**
The custom integration built for BMBooks that automatically keeps the Shopify website in sync with Bookscan. Runs on the shop machine in the background every 2 hours.

**CSTATUS**
A field in Bookscan's MASTER.DBF that records the availability status of a book. Common values: `ATT` (active), `OP` (out of print), `RP` (reprinting), `RMC` (under consideration for reprint), `NYPA` (not yet published). BookKeeper uses this to decide whether a book should sync to Shopify — OP, RP, and RMC are excluded.

**DBF / DBF file**
The file format Bookscan uses to store its data — an old but reliable database format. BookKeeper reads these files directly. The main ones are MASTER.DBF (products), PUBLISHER.DBF (publisher details), and WEBLIST.DBF (which products are listed on the website).

**Delta sync**
A smart sync that only sends data that has actually changed since the last run. Instead of re-sending all 38,000 books every 2 hours, BookKeeper compares each book's current details against what it sent last time — and only pushes the differences. Much faster and kinder to the Shopify API.

**Dev store**
A free test version of the Shopify store (bmbooks-dev.myshopify.com) used for development and UAT. Changes here don't affect the real website. Think of it as a practice version.

**Draft**
A product status in Shopify meaning the product exists but is invisible to customers on the website. BookKeeper creates all products as Draft so they can be reviewed before going live. Setting a product to Active makes it visible.

**DHL Express**
The international courier service BMBooks uses for overseas orders. Shopify automatically calculates the correct shipping cost at checkout based on the book's weight and the customer's address.

**eShip / NZ Post**
The shipping platform Louisa uses to generate courier labels for online orders. It connects directly to Shopify after go-live to pull order details.

**Ebility**
The middleware software from Barcode Solutions that previously connected Bookscan to WooCommerce. The Shopify version was never delivered, which is why BookKeeper was built.

**Inventory policy: continue**
A Shopify setting that allows customers to buy a product even when it shows zero stock. This is what makes "Available to order" work — the book isn't blocked from purchase just because there's nothing on the shelf right now.

**ISBN**
International Standard Book Number — the unique 13-digit identifier for every published book (e.g. 9780006546061). BookKeeper uses the ISBN as the link between a Bookscan record and a Shopify product.

**Metafield**
A custom data field in Shopify for storing extra information about a product — things Shopify doesn't have a built-in field for. BookKeeper uses metafields to store author name, ISBN, page count, and publication date.

**Shopify Admin**
The back-end management interface for the Shopify store, accessed at bruce-mckenzie-booksellers.myshopify.com/admin. This is where Louisa manages orders, products, and settings.

**Shopify Payments**
Shopify's built-in payment processor. Handles credit card payments at checkout. Requires bank account and identity verification before it can process real payments.

**Searchanise**
The search and filter app installed on the BMBooks Shopify store. It powers the search bar and category filters that customers use to find books.

**SKU**
Stock Keeping Unit — a unique code used to identify a specific product. In BookKeeper, the SKU is always the book's ISBN.

**State file (sync_state.json)**
A file BookKeeper creates and maintains on the shop machine. It records the last-known state of every synced product so the delta sync knows what has changed. If this file is deleted, the next run will re-sync everything from scratch.

**Task Scheduler**
A built-in Windows tool that runs programs automatically on a schedule. BookKeeper uses it to trigger the sync every 2 hours without anyone having to do anything manually.

**UAT (User Acceptance Testing)**
A structured process of running through test cases to verify that BookKeeper works correctly before going live with real data. Covered in the UAT section of this site.

**Vendor**
What Shopify calls the publisher of a product. BookKeeper maps the publisher name from Bookscan's PUBLISHER.DBF to this field.

**WooCommerce**
The e-commerce plugin previously used on the BMBooks WordPress website. Being replaced by Shopify as part of this migration.
