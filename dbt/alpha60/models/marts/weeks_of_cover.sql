WITH sales_30_days AS (
    SELECT
        variant_id,
        SUM(quantity) AS units_sold_30_days
    FROM `alpha60-data-platform.warehouse.fact_sales`
    WHERE order_created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
    GROUP BY variant_id
),

inventory AS (
    SELECT
        location_id,
        location_name,
        product_id,
        variant_id,
        product_title,
        variant_title,
        sku,
        vendor,
        product_type,
        product_status,
        available_quantity
    FROM `alpha60-data-platform.warehouse.fact_inventory_snapshot`
),

base AS (
    SELECT
        inventory.*,
        COALESCE(sales_30_days.units_sold_30_days, 0) AS units_sold_30_days,
        SAFE_DIVIDE(
            inventory.available_quantity,
            SAFE_DIVIDE(COALESCE(sales_30_days.units_sold_30_days, 0), 4.2857)
        ) AS raw_weeks_of_cover
    FROM inventory
    LEFT JOIN sales_30_days
        ON inventory.variant_id = sales_30_days.variant_id
)

SELECT
    *,
    ROUND(raw_weeks_of_cover, 1) AS weeks_of_cover,

    CASE
        WHEN available_quantity < 0 THEN 'negative_stock'
        WHEN available_quantity = 0 THEN 'out_of_stock'
        WHEN units_sold_30_days = 0 THEN 'no_recent_sales'
        WHEN raw_weeks_of_cover < 2 THEN 'low_cover'
        WHEN raw_weeks_of_cover > 12 THEN 'overstocked'
        ELSE 'healthy'
    END AS stock_status,

    CURRENT_TIMESTAMP() AS modelled_at

FROM base
