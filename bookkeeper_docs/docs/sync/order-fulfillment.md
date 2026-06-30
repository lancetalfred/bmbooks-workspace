---
sidebar_position: 3
---

# Order Fulfillment — Manual Process

:::caution Temporary workflow
This manual process is required until the inbound sync is built. Once live, Shopify orders will flow into Bookscan automatically — no manual entry required.
:::

## Overview

When a customer completes checkout on Shopify, an order is created in Shopify Admin. Louisa must then:

1. **In Shopify** — mark the order as fulfilled and (if shipping) enter a tracking number
2. **In Bookscan** — enter the order as a web sale so stock is deducted and the sale is recorded correctly for NielsenBookScan, EDI, and financials

The BookKeeper sync does **not** handle this automatically yet. Stock on the Shopify website will update within the next hourly sync after the Bookscan web sale is saved.

---

## Trigger

Customer completes checkout → Shopify sends Louisa an order notification email → order appears in Shopify Admin → Orders.

---

## Part 1: Shopify — Fulfill the Order

1. Open **Shopify Admin** → **Orders**
2. Click the new order to open it
3. Review:
   - Line items (titles, quantities, prices)
   - Shipping address
   - Shipping method — determines courier and label:
     - **NZ Standard / Tracked** → NZ Post via eShip
     - **International** → DHL label
     - **In-store pickup** → no courier, customer collects
4. Pick and pack the books from the shelf
5. Click **Fulfill items**
6. Enter the tracking number:
   - NZ Post: copy from eShip after generating the label
   - DHL: copy from the DHL label
   - In-store pickup: leave blank
7. Click **Fulfill items** to confirm → Shopify sends the customer an automated shipping/pickup notification email

---

## Part 2: Bookscan — Enter the Web Sale

This step records the sale in Bookscan so stock is deducted and the transaction appears in NielsenBookScan reporting, EDI, and financials.

1. Open **Bookscan**
2. Navigate to **Web Orders** (or equivalent sales entry screen)
3. Create a **new web sale**
4. Enter customer details:
   - Customer name (from the Shopify order)
   - Delivery address (full address from the Shopify order)
5. Add each line item from the Shopify order:

| Shopify field | Bookscan field |
|---|---|
| ISBN / barcode | ISBN |
| Title | Title |
| Quantity | Qty |
| Unit price (NZD, ex. any discounts) | Price |

6. Save the web sale — Bookscan deducts `ONHAND` stock and creates a proper sale record

---

## Stock sync timing

After saving the Bookscan web sale, the next hourly BookKeeper sync will detect the reduced `ONHAND` value and push the updated stock level to Shopify automatically. No manual stock adjustment in Shopify is needed.

**Worst case lag:** up to 1 hour between the Bookscan web sale and the Shopify stock count updating.

---

## In-store pickup

Same workflow as above with two differences:

- **Part 1 (Shopify):** Leave the tracking number blank. Mark as Fulfilled when the customer physically collects their order (not when you pack it).
- **Part 2 (Bookscan):** Same — enter as a web sale with the customer's name and the items collected. Use the store address as the delivery address.

---

## Edge cases

| Situation | What to do |
|---|---|
| **Partial fulfillment** | Fulfill only the available items in Shopify. Enter only those items as a web sale in Bookscan. Repeat when the remaining items are ready. |
| **Cancelled order (before fulfillment)** | Cancel in Shopify Admin → Orders → Cancel order. No Bookscan entry needed — no stock was deducted. |
| **Cancelled order (after fulfillment)** | Refund in Shopify. Manually add the returned stock back in Bookscan (`ONHAND` correction or a return transaction). |
| **Order with a discount code** | Enter the discounted price (what the customer actually paid) in the Bookscan web sale, not the full RRP. |

---

## What changes when the inbound sync is built

Once live, BookKeeper will poll Shopify's Orders API and write each order directly into Bookscan automatically. The entire manual Part 2 process above is eliminated. Shopify fulfillment (Part 1) remains unchanged.
