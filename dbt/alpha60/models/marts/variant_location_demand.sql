WITH sales AS (
    SELECT
        variant_id,
        sales_location_name,
        order_created_at,
        quantity
    FROM `alpha60-data-platform.warehouse.fact_sales`
    WHERE sales_location_name IS NOT NULL
),

sales_by_variant_location AS (
    SELECT
        variant_id,
        sales_location_name,

        SUM(
            CASE
                WHEN order_created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 28 DAY)
                THEN quantity
                ELSE 0
            END
        ) AS units_sold_4_weeks,

        SUM(
            CASE
                WHEN order_created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 84 DAY)
                THEN quantity
                ELSE 0
            END
        ) AS units_sold_12_weeks,

        MIN(order_created_at) AS first_sale_at,
        MAX(order_created_at) AS last_sale_at

    FROM sales
    GROUP BY
        variant_id,
        sales_location_name
),

warehouse_stock AS (
    SELECT
        variant_id,
        SUM(available_quantity) AS warehouse_available_quantity
    FROM `alpha60-data-platform.warehouse.fact_inventory_snapshot`
    WHERE location_name = 'Online / Warehouse'
    GROUP BY variant_id
)

SELECT
    inventory.location_id,
    inventory.location_name,

    inventory.product_id,
    inventory.variant_id,
    inventory.inventory_item_id,

    inventory.product_title,
    inventory.variant_title,
    inventory.sku,
    inventory.vendor,
    inventory.product_type,
    inventory.product_status,

    inventory.available_quantity,

    CASE inventory.location_name
        WHEN 'Claremont'
            THEN desired_stock.desired_stock_level_claremont
        WHEN 'James St'
            THEN desired_stock.desired_stock_level_james_st
        WHEN 'Oxford St'
            THEN desired_stock.desired_stock_level_oxford_st
        WHEN 'Newtown'
            THEN desired_stock.desired_stock_level_newtown
        WHEN 'Smith St'
            THEN desired_stock.desired_stock_level_smith_st
        WHEN 'Fitzroy'
            THEN desired_stock.desired_stock_level_fitzroy
        WHEN 'Flinders Lane'
            THEN desired_stock.desired_stock_level_flinders_lane
    END AS desired_stock_level,

    COALESCE(sales.units_sold_4_weeks, 0) AS units_sold_4_weeks,
    COALESCE(sales.units_sold_12_weeks, 0) AS units_sold_12_weeks,

    COALESCE(style_demand.style_units_4_weeks, 0) AS style_units_sold_4_weeks,
    COALESCE(style_demand.style_units_12_weeks, 0) AS style_units_sold_12_weeks,
    COALESCE(style_demand.demand_score, 0) AS style_demand_score,

    sales.first_sale_at,
    sales.last_sale_at,

    DATE_DIFF(
        CURRENT_DATE(),
        DATE(sales.last_sale_at),
        DAY
    ) AS days_since_last_sale,

    COALESCE(sales.units_sold_12_weeks, 0) > 0 AS has_recent_demand,

    inventory.available_quantity <= 0 AS currently_out_of_stock,

    COALESCE(warehouse_stock.warehouse_available_quantity, 0) AS warehouse_available_quantity,

    COALESCE(warehouse_stock.warehouse_available_quantity, 0) <= 0 AS warehouse_out_of_stock,

    CURRENT_TIMESTAMP() AS modelled_at

FROM `alpha60-data-platform.warehouse.fact_inventory_snapshot` AS inventory

LEFT JOIN `alpha60-data-platform.warehouse.dim_locations` AS locations
    ON inventory.location_id = locations.location_id

LEFT JOIN sales_by_variant_location AS sales
    ON inventory.variant_id = sales.variant_id
   AND locations.sales_location_name = sales.sales_location_name

LEFT JOIN warehouse_stock
    ON inventory.variant_id = warehouse_stock.variant_id

LEFT JOIN `alpha60-data-platform.stg.shopify_variant_metafields` AS desired_stock
    ON inventory.variant_id = desired_stock.variant_id

LEFT JOIN `alpha60-data-platform.warehouse.style_location_demand` AS style_demand
    ON inventory.product_id = style_demand.product_id
   AND inventory.location_name = style_demand.location_name
