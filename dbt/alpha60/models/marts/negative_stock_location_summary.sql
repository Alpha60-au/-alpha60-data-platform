{{ config(materialized='view') }}

SELECT
    location_id,
    location_name,
    city,

    COUNT(*) AS negative_variant_count,
    SUM(negative_units) AS total_negative_units,
    MIN(available_quantity) AS lowest_available_quantity,

    MAX(inventory_level_updated_at) AS latest_inventory_update,
    MAX(modelled_at) AS report_updated_at

FROM {{ ref('negative_stock_report') }}

GROUP BY
    location_id,
    location_name,
    city
