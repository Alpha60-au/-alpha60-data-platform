WITH shopify_locations AS (
    SELECT
        location_id,
        location_name AS inventory_location_name,
        city,
        province,
        country,
        is_active
    FROM `alpha60-data-platform.stg.shopify_locations`
),

location_mapping AS (
    SELECT 'Warehouse' AS sales_location_name, 'Online / Warehouse' AS inventory_location_name UNION ALL
    SELECT 'Melbourne', 'Flinders Lane' UNION ALL
    SELECT 'Fitzroy', 'Fitzroy' UNION ALL
    SELECT 'Newtown', 'Newtown' UNION ALL
    SELECT 'Smith St', 'Smith St' UNION ALL
    SELECT 'Melbourne Outlet', 'Melbourne Outlet' UNION ALL
    SELECT 'Claremont', 'Claremont' UNION ALL
    SELECT 'Paddington', 'Paddington' UNION ALL
    SELECT 'Oxford St', 'Oxford St' UNION ALL
    SELECT 'Wellington', 'Wellington' UNION ALL
    SELECT 'James St', 'James St' UNION ALL
    SELECT 'Spring1883', 'Spring1883'
)

SELECT
    shopify_locations.location_id,
    shopify_locations.inventory_location_name AS location_name,
    location_mapping.sales_location_name,
    shopify_locations.city,
    shopify_locations.province,
    shopify_locations.country,
    shopify_locations.is_active,

    CASE
        WHEN shopify_locations.inventory_location_name = 'Online / Warehouse' THEN 'warehouse'
        WHEN shopify_locations.inventory_location_name IN ('Faulty Land', 'Sparehouse') THEN 'internal'
        WHEN shopify_locations.is_active THEN 'store'
        ELSE 'inactive'
    END AS location_type,

    CASE
        WHEN shopify_locations.inventory_location_name IN (
            'Online / Warehouse',
            'Faulty Land',
            'Sparehouse',
            'Melbourne Outlet',
            'Spring1883',
            'Smith St',
            'Paddington'
        ) THEN FALSE
        ELSE TRUE
    END AS can_send_rotations,

    CASE
        WHEN shopify_locations.inventory_location_name IN (
            'Claremont',
            'Wellington',
            'James St',
            'Paddington',
            'Online / Warehouse',
            'Faulty Land',
            'Sparehouse',
            'Melbourne Outlet',
            'Spring1883'
        ) THEN FALSE
        ELSE TRUE
    END AS can_receive_rotations,

    CASE
        WHEN shopify_locations.inventory_location_name = 'Flinders Lane' THEN 100
        WHEN shopify_locations.inventory_location_name = 'Fitzroy' THEN 95
        WHEN shopify_locations.inventory_location_name = 'Smith St' THEN 90
        WHEN shopify_locations.inventory_location_name = 'Newtown' THEN 85
        WHEN shopify_locations.inventory_location_name = 'Oxford St' THEN 80
        ELSE 0
    END AS rotation_priority,

    CURRENT_TIMESTAMP() AS modelled_at

FROM shopify_locations

LEFT JOIN location_mapping
    ON shopify_locations.inventory_location_name = location_mapping.inventory_location_name
