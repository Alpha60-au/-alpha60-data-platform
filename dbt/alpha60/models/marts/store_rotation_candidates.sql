WITH base AS (
    SELECT
        demand.*,
        locations.can_send_rotations,
        locations.can_receive_rotations,
        locations.rotation_priority,
        products.is_classics
    FROM {{ ref('variant_location_demand') }} AS demand
    JOIN {{ ref('store_rotation_locations') }} AS locations
      ON demand.location_id = locations.location_id
    JOIN {{ ref('store_rotation_products') }} AS products
      ON demand.product_id = products.product_id
    WHERE products.is_season_aw26 = TRUE
      AND products.is_aw26_rotation_excluded = FALSE
      AND products.is_sock = FALSE
),

receivers AS (
    SELECT *
    FROM base
    WHERE can_receive_rotations = TRUE
      AND warehouse_available_quantity <= 0
      AND available_quantity < 2
),

senders AS (
    SELECT *
    FROM base
    WHERE can_send_rotations = TRUE
      AND available_quantity > 0
      AND warehouse_available_quantity <= 0
),

candidates AS (
    SELECT
        receiver.variant_id,
        receiver.product_id,
        receiver.product_title,
        receiver.variant_title,
        receiver.sku,

        sender.location_id AS send_from_location_id,
        sender.location_name AS send_from_location_name,
        sender.available_quantity AS send_from_available_quantity,
        sender.style_units_sold_12_weeks AS send_from_style_units_12_weeks,
        sender.style_demand_score AS send_from_style_demand_score,

        receiver.location_id AS send_to_location_id,
        receiver.location_name AS send_to_location_name,
        receiver.available_quantity AS send_to_available_quantity,
        receiver.style_units_sold_12_weeks AS send_to_style_units_12_weeks,
        receiver.style_demand_score AS send_to_style_demand_score,
        receiver.rotation_priority AS send_to_rotation_priority,

        receiver.warehouse_available_quantity,

        CASE
            WHEN receiver.location_name IN ('Oxford St', 'Newtown') THEN 1
            WHEN receiver.available_quantity <= 0 THEN LEAST(
                sender.available_quantity,
                2
            )
            WHEN receiver.available_quantity = 1 THEN 1
            ELSE 0
        END AS recommended_transfer_quantity,

        CASE
            WHEN sender.location_name = 'Newtown' THEN 1
            WHEN sender.location_name = 'Oxford St' THEN 2
            WHEN sender.location_name IN ('Wellington', 'Claremont', 'James St') THEN 3
            WHEN sender.location_name IN ('Flinders Lane', 'Fitzroy') THEN 4
            ELSE 99
        END AS donor_tier,

        receiver.style_demand_score - sender.style_demand_score AS style_demand_gap,

        (
            receiver.style_demand_score * 20
            - sender.style_demand_score * 5
            + receiver.rotation_priority
            + 75
        ) AS rotation_score,

        'rotation_recommendation_warehouse_empty' AS recommendation_type,

        CURRENT_TIMESTAMP() AS modelled_at

    FROM receivers AS receiver

    JOIN senders AS sender
      ON receiver.variant_id = sender.variant_id
     AND receiver.location_id != sender.location_id

    WHERE (
        receiver.location_name != 'Oxford St'
        OR (
            sender.location_name = 'Newtown'
            AND sender.available_quantity >= 2
            AND receiver.style_demand_score > sender.style_demand_score
        )
    )

    -- Oxford St and Newtown operate as a closed transfer pair.
    AND NOT (
        sender.location_name = 'Oxford St'
        AND receiver.location_name != 'Newtown'
    )
    AND NOT (
        receiver.location_name = 'Oxford St'
        AND sender.location_name != 'Newtown'
    )
    AND NOT (
        sender.location_name = 'Newtown'
        AND receiver.location_name != 'Oxford St'
    )
    AND NOT (
        receiver.location_name = 'Newtown'
        AND sender.location_name != 'Oxford St'
    )
    AND (
        receiver.location_name NOT IN ('Oxford St', 'Newtown')
        OR receiver.available_quantity = 0
    )

    -- Smith St may receive only Denim or CLASSICS, and never from Newtown.
    AND (
        receiver.location_name != 'Smith St'
        OR (
            sender.location_name != 'Newtown'
            AND (
                UPPER(COALESCE(receiver.product_type, '')) LIKE '%DENIM%'
                OR receiver.is_classics
            )
        )
    )

    -- Flinders Lane and Fitzroy are restricted sending stores.
    AND (
        sender.location_name NOT IN ('Flinders Lane', 'Fitzroy')
        OR (
            (
                (
                    sender.location_name = 'Flinders Lane'
                    AND receiver.location_name IN ('Fitzroy', 'Smith St')
                )
                OR (
                    sender.location_name = 'Fitzroy'
                    AND receiver.location_name IN ('Flinders Lane', 'Smith St')
                )
            )
            AND sender.available_quantity > 2
            AND receiver.available_quantity = 0
            AND receiver.style_demand_score > sender.style_demand_score
        )
    )
),

ranked_candidates AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY variant_id, send_to_location_id
            ORDER BY
                donor_tier ASC,
                rotation_score DESC,
                send_from_style_demand_score ASC,
                send_from_location_name ASC
        ) AS candidate_rank,

        ROW_NUMBER() OVER (
            PARTITION BY variant_id, send_from_location_id
            ORDER BY
                rotation_score DESC,
                send_to_style_units_12_weeks DESC,
                send_to_available_quantity ASC,
                send_to_rotation_priority DESC,
                send_to_location_name ASC
        ) AS donor_rank
    FROM candidates
)

SELECT *
FROM ranked_candidates
ORDER BY rotation_score DESC
