# Bookscan entry box (WooCommerce order page)

A read-only box on each WooCommerce order screen in WP admin. It lays the web order out in the order staff key it into Bookscan as a **till sale** with tender **Web Payments**:

1. **Status banner:** short and factual: *Paid* (green), *Not paid yet* (On hold / Pending), *Pay in store on collection: not paid yet* (WooCommerce marks these Processing anyway), *Shipping to be advised* (overseas $0 shipping), *Already completed*, *Not to be entered* (cancelled, refunded, failed).
2. **Customer:** first name, surname, email, phone and billing address, each with a Copy button. "Deliver to" appears only if it differs.
3. **Lines:** title, ISBN with Copy, an on-screen **EAN-13 barcode** for the till scanner, qty (bold red when more than 1), unit price incl GST, line total. "No ISBN" where there isn't one.
4. **Freight:** the shipping method, plus the amount with Copy when shipping was charged. A $0 amount is never shown (to be advised / collect / free shows the method only). Fees, discount and refund amounts appear where they apply.
5. **Total** with Copy, and the payment method as WooCommerce records it.

**Design rule (Lance, 23 Nov):** facts only, no instructions. Louisa knows the process and talks to the customers, so on-screen guidance could contradict what she's agreed with them.

It writes nothing: not to the order, not to Bookscan. Only users who can edit orders see it. Works with both WooCommerce order storage modes (HPOS and classic).

## Why this exists
Phase 2 research (Notion: *Phase 2 · Online Order Entry: Research*, E1/E2) found web orders are entered as Bookscan till sales with tender WEB, taking about 5 minutes each. December brings 110–135 orders. This box cuts the typing. See `Project/Active/BMBooks_Action_Items.md` (Phase 2).

## Install / rollback
1. WP admin → **Snippets → Add New**.
2. Title: `BMB Bookscan entry box`.
3. Paste everything in `bmb-bookscan-order-box.php` **below** the opening `<?php` line.
4. Choose **Only run in administration area**.
5. **Save Changes and Activate**.

**Rollback:** Snippets → deactivate `BMB Bookscan entry box`. If WP admin won't load, use Code Snippets' safe mode (add `define('CODE_SNIPPETS_SAFE_MODE', true);` to `wp-config.php`) and deactivate it.

## Test checklist
- [ ] Open a recent **Processing** order. The box shows near the top with a green banner.
- [ ] Customer fields match the order; Copy puts the value on the clipboard.
- [ ] Each book line shows its ISBN and barcode. Scan one barcode off the screen with the till scanner into Bookscan's barcode field (at the shop).
- [ ] Remote: in Chrome Remote Desktop on the shop PC, Copy an ISBN and paste it into Bookscan.
- [ ] Freight amount and total match the order.
- [ ] Open an order with 2+ of one book, one with a gift voucher (no ISBN), and one with a different delivery address.
- [ ] A **Completed** order shows the grey "probably already entered" banner.

## Notes from review (2026-11-23)
- Reviewed by reading only (no PHP available locally): no fatal-error risk found. WooCommerce calls are checked against 8.x/9.x, and it works with Code Snippets' eval, HPOS and classic storage.
- Fixed: partly refunded orders now show the quantity, line totals and order total **after refunds**.
- Barcodes are drawn at 3px per bar with crisp edges, so they stay sharp at Windows display scaling. Screen barcodes need an **imager-type** scanner (most laser scanners can't read screens). Test with the shop's scanner.

## Known limits
- No Bookscan customer code: WordPress can't read Bookscan, so staff still search for the customer.
- The freight item code isn't known yet. To confirm with Louisa.
- WordPress only: retired at Shopify go-live (~21 Dec 2026). The Shopify equivalent is a January decision.
