---
sidebar_position: 2
---

# Louisa's Guide

Everything you need to know about how BookKeeper works and what — if anything — you need to do.

---

## The short version

BookKeeper runs quietly in the background on the shop computer. Every hour it reads the Bookscan database and updates the Shopify website automatically. You don't need to do anything for it to work.

---

## What it does for you

| What changes in Bookscan | What happens on the website |
|---|---|
| You add a new book with a title and a price | It appears on the website within 1 hour, set to **Active** |
| A book sells in-store | The stock count on the website updates within 1 hour |
| You change a price | The new price shows on the website within 1 hour |
| You change a book's status to **OP**, **RP**, or **RUC** | It disappears from the website within 1 hour |
| You change a book back to **ACT** (active) | It reappears on the website within 1 hour |

---

## When a new book appears on the website

A new book will appear on the website as **Active** (visible to customers) automatically — but only once it has **both** a title and a price greater than $0.

If a book is missing its title, or the price hasn't been entered yet, it will stay in **Draft** (hidden from customers) until both are filled in. Once you add the missing information in Bookscan, the next hourly sync will automatically make it active.

You don't need to do anything in Shopify — it happens on its own.

---

## What customers see for out-of-stock books

If a book has no copies on the shelf, it doesn't disappear from the website. Instead, it shows as **"Available to order"** — customers can still buy it, and you'll order it in when the order comes through.

---

## The 1-hour window

The website updates every hour, not in real time. There's a short window where, for example, a book sold in-store might still show as "in stock" online. In practice this is rarely a problem, but it's worth knowing.

If you need to trigger an update immediately, double-click the **Sync Now** shortcut on the shop computer desktop. You can also click the **Sync Now** button inside the BookKeeper window.

---

## The BookKeeper window

When you open BookKeeper via the desktop shortcut, you'll see:

| What you see | What it means |
|---|---|
| 🟢 **Running** | A sync is in progress — leave it to finish |
| ⚫ **Idle** | No sync running — everything is up to date |
| 🔴 **Idle** (red dot) | Last sync had errors — contact Lance |
| **Last sync:** date/time | When the most recent sync ran |
| **Mode: Delta sync** | Only changed products were processed (normal) |
| **Created: 9** | New books added to the website this sync |
| **Updated: 28** | Existing books updated (price, stock, etc.) |
| **Errors: 0** | Problems during sync — click to see which books |

You can click **Created**, **Updated**, or **Errors** to see a list of exactly which books were affected.

Close the window when you're done — BookKeeper continues running in the background automatically.

---

## What you don't need to do

- ❌ You don't need to log into Shopify to update stock
- ❌ You don't need to add products to Shopify manually
- ❌ You don't need to update prices in two places
- ❌ You don't need to restart anything or press any buttons

Bookscan remains your one source of truth. Whatever is in Bookscan is what appears on the website.

---

## What you do still need to do in Shopify

A small number of things still need to be managed directly in Shopify:

| Task | Where in Shopify | How often |
|---|---|---|
| Process online orders | Orders | Daily |
| Mark orders as fulfilled / shipped | Orders | As needed |
| Update opening hours or store info | Online Store → Pages | When hours change |
| Run promotions or discount codes | Discounts | As needed |
| Review abandoned checkouts | Marketing → Automations | Weekly |

---

## Online orders and stock

When a customer buys online, Shopify records the order. At the moment, you'll need to manually enter the order as a **web sale** in Bookscan — customer name, delivery address, and each line item. This is the same process you use today with WooCommerce orders.

**When you get an online order:**
1. Open the order in Shopify Admin (Orders)
2. Enter it as a web sale in Bookscan — customer details, delivery address, and each line item (ISBN, title, quantity, price)
3. Bookscan will deduct the stock and record the sale correctly

---

## If something looks wrong on the website

If a book is showing the wrong price, wrong stock, or isn't appearing at all:

1. Check it looks correct in Bookscan first — the website always reflects what's in Bookscan
2. If Bookscan looks right, wait for the next sync cycle (up to 1 hour)
3. If it still looks wrong after that, contact Lance

---

## If the sync stops working

Signs that something might be wrong:
- Stock levels on the website haven't changed after in-store sales
- A book you added to Bookscan yesterday still isn't on the website
- The BookKeeper window shows a red dot

**What to do:** Contact Lance. He'll check the log file on the shop computer and fix it. You don't need to do anything technical yourself.

---

## Questions?

Contact Lance: lance.t.alfred@gmail.com
