---
sidebar_position: 1
slug: /intro
---

# BookKeeper for Shopify

**BookKeeper for Shopify** is a custom Python integration that keeps Bruce McKenzie Booksellers' Shopify store in sync with their Bookscan point-of-sale system.

## What it does

BookKeeper runs on the shop computer and syncs the Bookscan database to the Shopify website every hour — products, prices, stock levels, descriptions, and cover images. Only products that have changed since the last run are processed (delta sync).

## Why it exists

Bruce McKenzie Booksellers uses **Bookscan** as their in-store POS and product catalog (~38,000 products). The official Shopify connector from Barcode Solutions was never delivered, so BookKeeper is a custom replacement built to run directly on the shop machine — no cloud server, no external dependencies.

## Key behaviour

- **Delta sync** — only changed products are pushed each hour, keeping API usage low
- **Publish guard** — a book only goes live on the website once it has both a title and a price in Bookscan
- **Available to order** — out-of-stock books remain visible and purchasable
- **DBF schema validation** — if a Bookscan update changes a field name, the sync halts before touching Shopify
