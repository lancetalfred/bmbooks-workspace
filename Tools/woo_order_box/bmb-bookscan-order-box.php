<?php
/**
 * BMBooks – "Bookscan entry" box on the WooCommerce order screen.
 *
 * Read-only helper for Christmas 2026. It lays out a web order in the order staff
 * key it into Bookscan as a till sale (tender: Web Payments):
 *   status → customer → delivery address → book lines (ISBN, barcode, qty, price)
 *   → freight line → total.
 * It writes nothing: not to the order, not to Bookscan. Admin users only.
 *
 * Install (Code Snippets plugin):
 *   Snippets → Add New → title "BMB Bookscan entry box" → paste everything BELOW
 *   the opening "<?php" line → choose "Only run in administration area"
 *   → Save Changes and Activate. Rollback: Deactivate the snippet.
 *
 * Works with both WooCommerce order storage modes (HPOS and classic posts).
 */

if ( ! defined( 'ABSPATH' ) ) {
	return;
}

add_action( 'add_meta_boxes', 'bmb_bs_register_box', 30 );

if ( ! function_exists( 'bmb_bs_register_box' ) ) {
	/**
	 * Register the box on the order edit screen (classic and HPOS screen ids).
	 */
	function bmb_bs_register_box() {
		if ( ! function_exists( 'wc_get_order' ) ) {
			return;
		}
		$screens = array( 'shop_order' );
		if ( function_exists( 'wc_get_page_screen_id' ) ) {
			$screens[] = wc_get_page_screen_id( 'shop-order' );
		}
		foreach ( array_unique( $screens ) as $screen ) {
			add_meta_box( 'bmb-bookscan-entry', 'Bookscan entry (Built by Lance Alfred)', 'bmb_bs_render_box', $screen, 'normal', 'high' );
		}
	}
}

if ( ! function_exists( 'bmb_bs_money' ) ) {
	/**
	 * Plain 2-decimal amount for copying into Bookscan (no currency symbol).
	 */
	function bmb_bs_money( $amount ) {
		return number_format( (float) $amount, 2, '.', '' );
	}
}

if ( ! function_exists( 'bmb_bs_copy_row' ) ) {
	/**
	 * One labelled value with a Copy button. Empty values are skipped.
	 */
	function bmb_bs_copy_row( $label, $value, $mono = false ) {
		$value = trim( (string) $value );
		if ( '' === $value ) {
			return;
		}
		printf(
			'<div class="bmb-bs-row"><span class="bmb-bs-label">%1$s</span><span class="bmb-bs-val%2$s">%3$s</span><button type="button" class="button button-small bmb-bs-copy" data-copy="%4$s" aria-label="Copy %1$s">Copy</button></div>',
			esc_html( $label ),
			$mono ? ' bmb-bs-mono' : '',
			esc_html( $value ),
			esc_attr( $value )
		);
	}
}

if ( ! function_exists( 'bmb_bs_ean13_svg' ) ) {
	/**
	 * Inline SVG EAN-13 barcode for a valid 13-digit code (ISBN-13), else ''.
	 * Drawn at 2px per module with quiet zones so a till scanner can read it off the screen.
	 */
	function bmb_bs_ean13_svg( $code ) {
		if ( ! preg_match( '/^\d{13}$/', $code ) ) {
			return '';
		}
		$d   = array_map( 'intval', str_split( $code ) );
		$sum = 0;
		for ( $i = 0; $i < 12; $i++ ) {
			$sum += $d[ $i ] * ( ( $i % 2 ) ? 3 : 1 );
		}
		if ( ( 10 - $sum % 10 ) % 10 !== $d[12] ) {
			return ''; // Bad check digit: not a real EAN, don't draw a misleading barcode.
		}
		$l_codes = array( '0001101', '0011001', '0010011', '0111101', '0100011', '0110001', '0101111', '0111011', '0110111', '0001011' );
		$g_codes = array( '0100111', '0110011', '0011011', '0100001', '0011101', '0111001', '0000101', '0010001', '0001001', '0010111' );
		$r_codes = array( '1110010', '1100110', '1101100', '1000010', '1011100', '1001110', '1010000', '1000100', '1001000', '1110100' );
		$parity  = array( 'LLLLLL', 'LLGLGG', 'LLGGLG', 'LLGGGL', 'LGLLGG', 'LGGLLG', 'LGGGLL', 'LGLGLG', 'LGLGGL', 'LGGLGL' );

		$pattern = $parity[ $d[0] ];
		$bits    = '101';
		for ( $i = 1; $i <= 6; $i++ ) {
			$bits .= ( 'L' === $pattern[ $i - 1 ] ) ? $l_codes[ $d[ $i ] ] : $g_codes[ $d[ $i ] ];
		}
		$bits .= '01010';
		for ( $i = 7; $i <= 12; $i++ ) {
			$bits .= $r_codes[ $d[ $i ] ];
		}
		$bits .= '101';

		$module = 3; // 3px per bar stays sharp at Windows display scaling (125%/150%).
		$quiet  = 11;
		$height = 56;
		$width  = ( strlen( $bits ) + $quiet * 2 ) * $module;
		$rects  = '';
		$len    = strlen( $bits );
		for ( $i = 0; $i < $len; $i++ ) {
			if ( '1' === $bits[ $i ] ) {
				$rects .= '<rect x="' . ( ( $quiet + $i ) * $module ) . '" y="0" width="' . $module . '" height="' . $height . '"/>';
			}
		}
		return '<svg class="bmb-bs-barcode" xmlns="http://www.w3.org/2000/svg" width="' . $width . '" height="' . $height
			. '" viewBox="0 0 ' . $width . ' ' . $height . '" shape-rendering="crispEdges" role="img" aria-label="Barcode ' . esc_attr( $code ) . '">'
			. '<rect width="' . $width . '" height="' . $height . '" fill="#ffffff"/><g fill="#000000">' . $rects . '</g></svg>';
	}
}

if ( ! function_exists( 'bmb_bs_pays_on_collection' ) ) {
	/**
	 * True when the customer pays in store at pickup (WooCommerce still marks these "Processing").
	 */
	function bmb_bs_pays_on_collection( $order ) {
		return 'cod' === $order->get_payment_method()
			|| (bool) preg_match( '/in ?store|on collection|upon collection/i', (string) $order->get_payment_method_title() );
	}
}

if ( ! function_exists( 'bmb_bs_status_banner' ) ) {
	/**
	 * Tell staff whether this order should be entered now.
	 */
	function bmb_bs_status_banner( $order, $tba_shipping = false ) {
		$status = $order->get_status();
		$name   = wc_get_order_status_name( $status );
		if ( 'processing' === $status && bmb_bs_pays_on_collection( $order ) ) {
			$class = 'warn';
			$text  = 'Pay in store on collection: not paid yet';
		} elseif ( 'processing' === $status && $tba_shipping ) {
			$class = 'warn';
			$text  = 'Shipping to be advised';
		} elseif ( 'processing' === $status ) {
			$class = 'ok';
			$text  = 'Paid';
		} elseif ( 'completed' === $status ) {
			$class = 'muted';
			$text  = 'Already completed';
		} elseif ( in_array( $status, array( 'on-hold', 'pending' ), true ) ) {
			$class = 'warn';
			$text  = 'Not paid yet';
		} else {
			$class = 'stop';
			$text  = 'Not to be entered';
		}
		printf(
			'<div class="bmb-bs-banner bmb-bs-%1$s"><strong>%2$s</strong> · %3$s</div>',
			esc_attr( $class ),
			esc_html( $name ),
			esc_html( $text )
		);
	}
}

if ( ! function_exists( 'bmb_bs_assets' ) ) {
	/**
	 * Inline CSS + copy-button script, printed once per page.
	 */
	function bmb_bs_assets() {
		static $done = false;
		if ( $done ) {
			return;
		}
		$done = true;
		?>
<style>
#bmb-bookscan-entry .inside{margin:0;padding:0 12px 12px}
.bmb-bs-banner{padding:8px 12px;border-radius:4px;margin:12px 0}
.bmb-bs-ok{background:#ddf1ec;color:#0b5a4c}
.bmb-bs-muted{background:#ecebf0;color:#3f3a4f}
.bmb-bs-warn{background:#fbebd3;color:#7a4200}
.bmb-bs-stop{background:#f8dcdc;color:#8a1f1f}
.bmb-bs-step{margin:14px 0 6px;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#5b566b}
.bmb-bs-row{display:flex;align-items:center;gap:10px;padding:3px 0;max-width:560px}
.bmb-bs-label{width:110px;color:#5b566b;flex-shrink:0}
.bmb-bs-val{flex-grow:1;min-width:0;overflow-wrap:anywhere}
.bmb-bs-mono{font-family:Menlo,Consolas,monospace}
.bmb-bs-lines{width:100%;border-collapse:collapse}
.bmb-bs-lines th{text-align:left;font-weight:600;color:#5b566b;border-bottom:1px solid #dcdcde;padding:6px 8px}
.bmb-bs-lines td{border-bottom:1px solid #f0f0f1;padding:8px;vertical-align:middle}
.bmb-bs-lines .num{text-align:right;white-space:nowrap}
.bmb-bs-qty-many{font-weight:700;color:#8a1f1f}
.bmb-bs-barcode{display:block;max-width:none}
.bmb-bs-note{color:#7a4200}
.bmb-bs-total{display:flex;gap:16px;flex-wrap:wrap;align-items:center;margin-top:12px;font-size:14px}
</style>
<script>
(function () {
	if (window.bmbBsCopyBound) { return; }
	window.bmbBsCopyBound = true;
	document.addEventListener('click', function (e) {
		var btn = e.target.closest ? e.target.closest('.bmb-bs-copy') : null;
		if (!btn) { return; }
		e.preventDefault();
		var text = btn.getAttribute('data-copy') || '';
		var label = btn.getAttribute('data-label') || btn.textContent;
		btn.setAttribute('data-label', label);
		function done() {
			btn.textContent = 'Copied';
			setTimeout(function () { btn.textContent = label; }, 1200);
		}
		function fallback() {
			var area = document.createElement('textarea');
			area.value = text;
			area.setAttribute('readonly', '');
			area.style.position = 'fixed';
			area.style.opacity = '0';
			document.body.appendChild(area);
			area.select();
			try { if (document.execCommand('copy')) { done(); } } catch (err) {}
			document.body.removeChild(area);
		}
		if (navigator.clipboard && window.isSecureContext) {
			navigator.clipboard.writeText(text).then(done, fallback);
		} else {
			fallback();
		}
	});
})();
</script>
		<?php
	}
}

if ( ! function_exists( 'bmb_bs_render_box' ) ) {
	/**
	 * The box itself. Receives a WP_Post (classic) or WC_Order (HPOS).
	 */
	function bmb_bs_render_box( $post_or_order ) {
		if ( ! current_user_can( 'edit_shop_orders' ) ) {
			return;
		}
		$order = ( $post_or_order instanceof WC_Order ) ? $post_or_order : wc_get_order( $post_or_order );
		if ( ! $order ) {
			echo '<p>This order could not be loaded.</p>';
			return;
		}

		// Shipping first: "to be advised" orders change the banner.
		$shipping     = (float) $order->get_shipping_total() + (float) $order->get_shipping_tax();
		$method       = $order->get_shipping_method();
		$tba_shipping = ( $shipping <= 0 && preg_match( '/advis/i', $method ) ); // "Shipping costs/charges to be advised".

		bmb_bs_assets();
		bmb_bs_status_banner( $order, $tba_shipping );

		// 1 · Customer (Bookscan: search first; if new, add with these details).
		echo '<div class="bmb-bs-step">Customer</div>';
		bmb_bs_copy_row( 'First name', $order->get_billing_first_name() );
		bmb_bs_copy_row( 'Surname', $order->get_billing_last_name() );
		bmb_bs_copy_row( 'Company', $order->get_billing_company() );
		bmb_bs_copy_row( 'Email', $order->get_billing_email(), true );
		bmb_bs_copy_row( 'Phone', $order->get_billing_phone(), true );
		bmb_bs_copy_row( 'Address 1', $order->get_billing_address_1() );
		bmb_bs_copy_row( 'Address 2', $order->get_billing_address_2() );
		bmb_bs_copy_row( 'Town / city', $order->get_billing_city() );
		bmb_bs_copy_row( 'Postcode', $order->get_billing_postcode(), true );
		if ( 'NZ' !== $order->get_billing_country() ) {
			bmb_bs_copy_row( 'Country', $order->get_billing_country() );
		}

		// Delivery address, only when it differs from billing.
		$billing_addr  = array( $order->get_billing_first_name(), $order->get_billing_last_name(), $order->get_billing_address_1(), $order->get_billing_address_2(), $order->get_billing_city(), $order->get_billing_postcode(), $order->get_billing_country() );
		$shipping_addr = array( $order->get_shipping_first_name(), $order->get_shipping_last_name(), $order->get_shipping_address_1(), $order->get_shipping_address_2(), $order->get_shipping_city(), $order->get_shipping_postcode(), $order->get_shipping_country() );
		if ( $order->has_shipping_address() && array_map( 'strtolower', array_map( 'trim', $billing_addr ) ) !== array_map( 'strtolower', array_map( 'trim', $shipping_addr ) ) ) {
			echo '<div class="bmb-bs-step">Deliver to</div>';
			bmb_bs_copy_row( 'Deliver to', trim( $order->get_shipping_first_name() . ' ' . $order->get_shipping_last_name() ) );
			bmb_bs_copy_row( 'Address 1', $order->get_shipping_address_1() );
			bmb_bs_copy_row( 'Address 2', $order->get_shipping_address_2() );
			bmb_bs_copy_row( 'Town / city', $order->get_shipping_city() );
			bmb_bs_copy_row( 'Postcode', $order->get_shipping_postcode(), true );
		}

		// 2 · Lines.
		echo '<div class="bmb-bs-step">Lines</div>';
		echo '<table class="bmb-bs-lines"><thead><tr><th>Title</th><th>ISBN / code</th><th>Barcode</th><th class="num">Qty</th><th class="num">Unit price</th><th class="num">Line total</th></tr></thead><tbody>';
		foreach ( $order->get_items() as $item_id => $item ) {
			if ( ! ( $item instanceof WC_Order_Item_Product ) ) {
				continue;
			}
			$refunded_qty = (int) $order->get_qty_refunded_for_item( $item_id ); // Negative or 0.
			$qty          = (int) $item->get_quantity() + $refunded_qty;
			if ( $qty <= 0 ) {
				continue; // Fully refunded line: nothing to enter.
			}
			$product = $item->get_product();
			$sku     = $product ? trim( (string) $product->get_sku() ) : '';
			$barcode = bmb_bs_ean13_svg( preg_replace( '/\D/', '', $sku ) ); // Tolerate hyphens/spaces in stored SKUs.
			$unit    = $order->get_item_total( $item, true, true );
			$line    = $refunded_qty ? $unit * $qty : $order->get_line_total( $item, true, true );

			echo '<tr>';
			echo '<td>' . esc_html( $item->get_name() ) . '</td>';
			if ( '' === $sku ) {
				echo '<td class="bmb-bs-note">No ISBN</td><td></td>';
			} else {
				echo '<td><span class="bmb-bs-mono">' . esc_html( $sku ) . '</span> <button type="button" class="button button-small bmb-bs-copy" data-copy="' . esc_attr( $sku ) . '" aria-label="Copy code ' . esc_attr( $sku ) . '">Copy</button></td>';
				echo '<td>' . ( $barcode ? $barcode : '' ) . '</td>'; // SVG built from digits only.
			}
			echo '<td class="num' . ( $qty > 1 ? ' bmb-bs-qty-many' : '' ) . '">' . esc_html( (string) $qty ) . '</td>';
			echo '<td class="num">$' . esc_html( bmb_bs_money( $unit ) ) . '</td>';
			echo '<td class="num">$' . esc_html( bmb_bs_money( $line ) ) . '</td>';
			echo '</tr>';
		}

		// Freight line (Bookscan: department FRE).
		if ( $shipping <= 0 && '' !== $method ) {
			// $0 shipping: show the method only (to be advised / collect / free), never a $0 amount to copy.
			echo '<tr><td>Freight</td><td colspan="5"' . ( $tba_shipping ? ' class="bmb-bs-note"' : '' ) . '>' . esc_html( $method ) . '</td></tr>';
		} elseif ( $shipping > 0 ) {
			echo '<tr><td>Freight</td><td colspan="2">' . esc_html( $method ) . '</td><td class="num">1</td>';
			echo '<td class="num">$' . esc_html( bmb_bs_money( $shipping ) ) . ' <button type="button" class="button button-small bmb-bs-copy" data-copy="' . esc_attr( bmb_bs_money( $shipping ) ) . '" aria-label="Copy freight amount">Copy</button></td>';
			echo '<td class="num">$' . esc_html( bmb_bs_money( $shipping ) ) . '</td></tr>';
		}

		// Fees (rare), shown so the total adds up.
		foreach ( $order->get_fees() as $fee ) {
			$fee_total = (float) $fee->get_total() + (float) $fee->get_total_tax();
			echo '<tr><td>Fee: ' . esc_html( $fee->get_name() ) . '</td><td colspan="2"></td><td class="num">1</td>';
			echo '<td class="num">$' . esc_html( bmb_bs_money( $fee_total ) ) . '</td><td class="num">$' . esc_html( bmb_bs_money( $fee_total ) ) . '</td></tr>';
		}
		echo '</tbody></table>';

		// Warnings that change what gets entered.
		$discount = (float) $order->get_total_discount( false );
		if ( $discount > 0 ) {
			$codes = implode( ', ', $order->get_coupon_codes() );
			echo '<p class="bmb-bs-note">Discount $' . esc_html( bmb_bs_money( $discount ) ) . ( $codes ? ' (' . esc_html( $codes ) . ')' : '' ) . ', included in prices above</p>';
		}
		$refunded = (float) $order->get_total_refunded();
		if ( $refunded > 0 ) {
			echo '<p class="bmb-bs-note">Refunded $' . esc_html( bmb_bs_money( $refunded ) ) . '</p>';
		}
		$note = trim( (string) $order->get_customer_note() );
		if ( '' !== $note ) {
			echo '<p><strong>Customer note:</strong> ' . nl2br( esc_html( $note ) ) . '</p>';
		}

		// 3 · Pay.
		$net = (float) $order->get_total() - $refunded; // After any refunds.
		echo '<div class="bmb-bs-step">Total</div>';
		echo '<div class="bmb-bs-total"><span><strong>$' . esc_html( bmb_bs_money( $net ) ) . '</strong>' . ( $refunded > 0 ? ' (after refunds)' : '' ) . '</span>';
		echo '<button type="button" class="button button-small bmb-bs-copy" data-copy="' . esc_attr( bmb_bs_money( $net ) ) . '" aria-label="Copy order total">Copy</button>';
		echo '<span>Payment: ' . esc_html( $order->get_payment_method_title() ) . '</span></div>';
	}
}
