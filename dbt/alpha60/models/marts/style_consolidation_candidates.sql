WITH base AS (
    SELECT
        demand.*,
        locations.can_send_rotations,
        locations.can_receive_rotations,
        products.is_classics
    FROM `alpha60-data-platform.warehouse.variant_location_demand` AS demand

    JOIN `alpha60-data-platform.warehouse.dim_locations` AS locations
      ON demand.location_id = locations.location_id

    JOIN `alpha60-data-platform.warehouse.dim_products` AS products
      ON demand.product_id = products.product_id

    WHERE products.is_season_aw26 = TRUE
      AND products.is_aw26_rotation_excluded = FALSE
      AND products.is_sock = FALSE
),

style_inventory AS (
    SELECT
        product_id,
        location_id,
        location_name,
        SUM(available_quantity) AS style_available_quantity
    FROM base
    GROUP BY
        product_id,
        location_id,
        location_name
),

warehouse_style_inventory AS (
    SELECT
        product_id,
        SUM(available_quantity) AS warehouse_style_available_quantity
    FROM base
    WHERE location_name = 'Online / Warehouse'
    GROUP BY product_id
),

donors AS (
    SELECT
        base.*,
        style_inventory.style_available_quantity,
        warehouse_style_inventory.warehouse_style_available_quantity
    FROM base

    JOIN style_inventory
      ON base.product_id = style_inventory.product_id
     AND base.location_id = style_inventory.location_id

    JOIN warehouse_style_inventory
      ON base.product_id = warehouse_style_inventory.product_id

    WHERE base.can_send_rotations = TRUE
      AND base.location_name NOT IN ('Fitzroy', 'Flinders Lane')
      AND base.available_quantity > 0
      AND style_inventory.style_available_quantity = 1
      AND warehouse_style_inventory.warehouse_style_available_quantity <= 0
),

destinations AS (
    SELECT
        style_inventory.product_id,
        style_inventory.location_id,
        style_inventory.location_name,
        style_inventory.style_available_quantity
    FROM style_inventory

    JOIN `alpha60-data-platform.warehouse.dim_locations` AS locations
      ON style_inventory.location_id = locations.location_id

    WHERE locations.can_receive_rotations = TRUE
      AND style_inventory.style_available_quantity > 1
),

valid_candidates AS (
    SELECT
        donor.product_id,
        donor.variant_id,
        donor.product_title,
        donor.variant_title,
        donor.sku,
        donor.product_type,
        donor.is_classics,

        donor.location_id AS send_from_location_id,
        donor.location_name AS send_from_location_name,
        donor.available_quantity AS send_from_available_quantity,
        donor.style_available_quantity AS send_from_style_available_quantity,

        destination.location_id AS send_to_location_id,
        destination.location_name AS send_to_location_name,
        destination.style_available_quantity AS send_to_style_available_quantity,

        donor.warehouse_style_available_quantity,

        1 AS recommended_transfer_quantity,
        'style_consolidation' AS recommendation_type,

        CURRENT_TIMESTAMP() AS modelled_at

    FROM donors AS donor

    JOIN destinations AS destination
      ON donor.product_id = destination.product_id
     AND donor.location_id != destination.location_id

    WHERE
        -- Oxford St and Newtown remain a closed pair.
        NOT (
            donor.location_name = 'Oxford St'
            AND destination.location_name != 'Newtown'
        )
        AND NOT (
            destination.location_name = 'Oxford St'
            AND donor.location_name != 'Newtown'
        )
        AND NOT (
            donor.location_name = 'Newtown'
            AND destination.location_name != 'Oxford St'
        )
        AND NOT (
            destination.location_name = 'Newtown'
            AND donor.location_name != 'Oxford St'
        )

        -- Smith St may receive only Denim or CLASSICS.
        AND (
            destination.location_name != 'Smith St'
            OR (
                donor.location_name != 'Newtown'
                AND (
                    UPPER(COALESCE(donor.product_type, '')) LIKE '%DENIM%'
                    OR donor.is_classics
                )
            )
        )
),

ranked_candidates AS (
    SELECT
        *,
        MAX(send_to_style_available_quantity) OVER (
            PARTITION BY product_id, send_from_location_id
        ) AS highest_destination_style_quantity
    FROM valid_candidates
),

unique_highest_destination AS (
    SELECT
        *,
        COUNTIF(
            send_to_style_available_quantity = highest_destination_style_quantity
        ) OVER (
            PARTITION BY product_id, send_from_location_id
        ) AS highest_destination_count
    FROM ranked_candidates
)

SELECT *
FROM unique_highest_destination
WHERE send_to_style_available_quantity = highest_destination_style_quantity
  AND highest_destination_count = 1
ORDER BY
    send_from_location_name,
    product_title,
    variant_title
