SELECT
    p.product_id,
    p.product_key,
    p.product_title,
    p.handle,
    p.vendor,
    p.product_type,
    p.status,
    p.tags,
    p.product_created_at,
    p.product_updated_at,
    p.product_published_at,

    COUNT(DISTINCT fs.order_id) AS orders,
    COALESCE(SUM(fs.quantity), 0) AS units_sold,
    COALESCE(SUM(fs.net_sales), 0) AS lifetime_sales,

    MIN(fs.order_created_at) AS first_sale_at,
    MAX(fs.order_created_at) AS last_sale_at,

    COUNT(DISTINCT fs.customer_email) AS unique_customers,

    CURRENT_TIMESTAMP() AS modelled_at

FROM `alpha60-data-platform.stg.shopify_products` AS p

LEFT JOIN `alpha60-data-platform.warehouse.fact_sales` AS fs
    ON p.product_id = fs.product_id

GROUP BY
    p.product_id,
    p.product_key,
    p.product_title,
    p.handle,
    p.vendor,
    p.product_type,
    p.status,
    p.tags,
    p.product_created_at,
    p.product_updated_at,
    p.product_published_at
