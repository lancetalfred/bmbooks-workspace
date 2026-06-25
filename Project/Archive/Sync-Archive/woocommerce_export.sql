-- ─────────────────────────────────────────────────────────────────────────────
-- BMBooks — WooCommerce Product Export Query
-- Run in phpMyAdmin → Export result as CSV
-- Used for Shopify POC before DBF files are available
--
-- Instructions:
-- 1. Log into cPanel > phpMyAdmin
-- 2. Select the BMBooks database
-- 3. Click SQL tab
-- 4. Paste this query and click Go
-- 5. Click Export > Format: CSV > Go
-- ─────────────────────────────────────────────────────────────────────────────

SELECT
    p.ID                                                            AS product_id,
    p.post_title                                                    AS title,
    p.post_content                                                  AS description,

    MAX(CASE WHEN pm.meta_key = '_sku'            THEN pm.meta_value END) AS isbn,
    MAX(CASE WHEN pm.meta_key = '_regular_price'  THEN pm.meta_value END) AS price,
    MAX(CASE WHEN pm.meta_key = '_stock'          THEN pm.meta_value END) AS stock,
    MAX(CASE WHEN pm.meta_key = '_stock_status'   THEN pm.meta_value END) AS stock_status,
    MAX(CASE WHEN pm.meta_key = '_weight'         THEN pm.meta_value END) AS weight,
    MAX(CASE WHEN pm.meta_key = '_manage_stock'   THEN pm.meta_value END) AS manage_stock,

    -- Bookscan custom fields (may vary — check results)
    MAX(CASE WHEN pm.meta_key = '_author'         THEN pm.meta_value END) AS author,
    MAX(CASE WHEN pm.meta_key = '_publisher'      THEN pm.meta_value END) AS publisher,
    MAX(CASE WHEN pm.meta_key = '_binding'        THEN pm.meta_value END) AS binding,
    MAX(CASE WHEN pm.meta_key = '_pages'          THEN pm.meta_value END) AS pages,
    MAX(CASE WHEN pm.meta_key = '_pub_date'       THEN pm.meta_value END) AS pub_date

FROM wp4n_posts p
JOIN wp4n_postmeta pm ON p.ID = pm.post_id

WHERE p.post_type   = 'product'
AND   p.post_status = 'publish'

GROUP BY p.ID, p.post_title, p.post_content

-- Only include products with a valid ISBN
HAVING isbn IS NOT NULL AND isbn != ''

ORDER BY p.post_title

-- Remove LIMIT to export all products. Use LIMIT 50 for initial testing.
LIMIT 50;
