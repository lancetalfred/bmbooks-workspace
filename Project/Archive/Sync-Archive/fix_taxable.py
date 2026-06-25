#!/usr/bin/env python3
"""One-off: set taxable=True on all Shopify product variants.

Run once after enabling NZ GST in Shopify tax settings.
~5 hours for 34k products. Safe to re-run — skips already-taxable variants.
"""

import os
import requests
import time
import re

STORE = os.environ.get("SHOPIFY_STORE_URL", "bruce-mckenzie-booksellers.myshopify.com")
TOKEN = os.environ["SHOPIFY_ACCESS_TOKEN"]
BASE  = f"https://{STORE}/admin/api/2024-01"
HDR   = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}


def api_get(url, params=None):
    while True:
        r = requests.get(url, headers=HDR, params=params)
        if r.status_code == 429:
            time.sleep(float(r.headers.get("Retry-After", 2)))
            continue
        r.raise_for_status()
        time.sleep(0.5)
        return r


def set_taxable(variant_id):
    url = f"{BASE}/variants/{variant_id}.json"
    while True:
        try:
            r = requests.put(url, headers=HDR, json={"variant": {"id": variant_id, "taxable": True}})
        except requests.exceptions.ConnectionError:
            print(f"  Connection error — retrying variant {variant_id} in 5s")
            time.sleep(5)
            continue
        if r.status_code == 429:
            time.sleep(float(r.headers.get("Retry-After", 2)))
            continue
        if r.status_code == 422:
            print(f"  Skipped variant {variant_id} (422 — likely gift card or locked variant)")
            time.sleep(0.5)
            return
        r.raise_for_status()
        time.sleep(0.5)
        return


products_done   = 0
variants_updated = 0
url    = f"{BASE}/products.json"
params = {"limit": 250, "fields": "id,variants"}

print("Setting taxable=True on all variants — will take several hours.")
print("Safe to Ctrl-C and re-run; already-taxable variants are skipped.\n")

while url:
    r        = api_get(url, params)
    products = r.json().get("products", [])
    if not products:
        break

    for p in products:
        for v in p["variants"]:
            if not v.get("taxable"):
                set_taxable(v["id"])
                variants_updated += 1
        products_done += 1
        if products_done % 250 == 0:
            print(f"  {products_done:,} products | {variants_updated:,} variants updated")

    nxt    = re.search(r'<([^>]+)>;\s*rel="next"', r.headers.get("Link", ""))
    url    = nxt.group(1) if nxt else None
    params = None

print(f"\nDone. {products_done:,} products | {variants_updated:,} variants updated.")
