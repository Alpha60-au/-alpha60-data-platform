WITH recommendations AS (
    SELECT *
    FROM {{ ref('store_rotation_candidates') }}
    WHERE candidate_rank = 1 AND donor_rank = 1
),

location_stock AS (
    SELECT
        variant_id,

        MAX(IF(location_name = 'Oxford St', available_quantity, NULL)) AS oxford_st_stock,
        MAX(IF(location_name = 'Newtown', available_quantity, NULL)) AS newtown_stock,
        MAX(IF(location_name = 'Fitzroy', available_quantity, NULL)) AS fitzroy_stock,
        MAX(IF(location_name = 'Flinders Lane', available_quantity, NULL)) AS flinders_lane_stock,
        MAX(IF(location_name = 'James St', available_quantity, NULL)) AS james_st_stock,
        MAX(IF(location_name = 'Claremont', available_quantity, NULL)) AS claremont_stock,
        MAX(IF(location_name = 'Wellington', available_quantity, NULL)) AS wellington_stock,
        MAX(IF(location_name = 'Paddington', available_quantity, NULL)) AS paddington_stock,

        MAX(IF(location_name = 'Oxford St', style_units_sold_12_weeks, NULL)) AS oxford_st_style_sales_12_weeks,
        MAX(IF(location_name = 'Newtown', style_units_sold_12_weeks, NULL)) AS newtown_style_sales_12_weeks,
        MAX(IF(location_name = 'Fitzroy', style_units_sold_12_weeks, NULL)) AS fitzroy_style_sales_12_weeks,
        MAX(IF(location_name = 'Flinders Lane', style_units_sold_12_weeks, NULL)) AS flinders_lane_style_sales_12_weeks,
        MAX(IF(location_name = 'James St', style_units_sold_12_weeks, NULL)) AS james_st_style_sales_12_weeks,
        MAX(IF(location_name = 'Claremont', style_units_sold_12_weeks, NULL)) AS claremont_style_sales_12_weeks,
        MAX(IF(location_name = 'Wellington', style_units_sold_12_weeks, NULL)) AS wellington_style_sales_12_weeks,
        MAX(IF(location_name = 'Paddington', style_units_sold_12_weeks, NULL)) AS paddington_style_sales_12_weeks

    FROM {{ ref('variant_location_demand') }}
    GROUP BY variant_id
)

SELECT
    ROW_NUMBER() OVER (
        ORDER BY
            recommendations.send_from_location_name,
            recommendations.product_title,
            recommendations.variant_title
    ) AS sheet_row_number,

    recommendations.send_from_location_name,
    recommendations.product_title,
    recommendations.variant_title,
    recommendations.sku,
    recommendations.send_to_location_name,
    recommendations.recommended_transfer_quantity,

    CASE recommendations.send_from_location_name
        WHEN 'Oxford St' THEN location_stock.oxford_st_stock
        WHEN 'Newtown' THEN location_stock.newtown_stock
        WHEN 'Fitzroy' THEN location_stock.fitzroy_stock
        WHEN 'Flinders Lane' THEN location_stock.flinders_lane_stock
        WHEN 'James St' THEN location_stock.james_st_stock
        WHEN 'Claremont' THEN location_stock.claremont_stock
        WHEN 'Wellington' THEN location_stock.wellington_stock
        WHEN 'Paddington' THEN location_stock.paddington_stock
    END AS send_from_available_quantity,

    CASE recommendations.send_to_location_name
        WHEN 'Oxford St' THEN location_stock.oxford_st_stock
        WHEN 'Newtown' THEN location_stock.newtown_stock
        WHEN 'Fitzroy' THEN location_stock.fitzroy_stock
        WHEN 'Flinders Lane' THEN location_stock.flinders_lane_stock
        WHEN 'James St' THEN location_stock.james_st_stock
        WHEN 'Claremont' THEN location_stock.claremont_stock
        WHEN 'Wellington' THEN location_stock.wellington_stock
        WHEN 'Paddington' THEN location_stock.paddington_stock
    END AS send_to_available_quantity,

    CASE recommendations.send_from_location_name
        WHEN 'Oxford St' THEN location_stock.oxford_st_style_sales_12_weeks
        WHEN 'Newtown' THEN location_stock.newtown_style_sales_12_weeks
        WHEN 'Fitzroy' THEN location_stock.fitzroy_style_sales_12_weeks
        WHEN 'Flinders Lane' THEN location_stock.flinders_lane_style_sales_12_weeks
        WHEN 'James St' THEN location_stock.james_st_style_sales_12_weeks
        WHEN 'Claremont' THEN location_stock.claremont_style_sales_12_weeks
        WHEN 'Wellington' THEN location_stock.wellington_style_sales_12_weeks
        WHEN 'Paddington' THEN location_stock.paddington_style_sales_12_weeks
    END AS sender_style_sales_12_weeks,

    CASE recommendations.send_to_location_name
        WHEN 'Oxford St' THEN location_stock.oxford_st_style_sales_12_weeks
        WHEN 'Newtown' THEN location_stock.newtown_style_sales_12_weeks
        WHEN 'Fitzroy' THEN location_stock.fitzroy_style_sales_12_weeks
        WHEN 'Flinders Lane' THEN location_stock.flinders_lane_style_sales_12_weeks
        WHEN 'James St' THEN location_stock.james_st_style_sales_12_weeks
        WHEN 'Claremont' THEN location_stock.claremont_style_sales_12_weeks
        WHEN 'Wellington' THEN location_stock.wellington_style_sales_12_weeks
        WHEN 'Paddington' THEN location_stock.paddington_style_sales_12_weeks
    END AS receiver_style_sales_12_weeks,

    location_stock.oxford_st_stock,
    location_stock.newtown_stock,
    location_stock.fitzroy_stock,
    location_stock.flinders_lane_stock,
    location_stock.james_st_stock,
    location_stock.claremont_stock,
    location_stock.wellington_stock,
    location_stock.paddington_stock,
    recommendations.warehouse_available_quantity,

    location_stock.oxford_st_style_sales_12_weeks,
    location_stock.newtown_style_sales_12_weeks,
    location_stock.fitzroy_style_sales_12_weeks,
    location_stock.flinders_lane_style_sales_12_weeks,
    location_stock.james_st_style_sales_12_weeks,
    location_stock.claremont_style_sales_12_weeks,
    location_stock.wellington_style_sales_12_weeks,
    location_stock.paddington_style_sales_12_weeks,

    ROUND(recommendations.rotation_score, 1) AS rotation_score,
    recommendations.recommendation_type,
    recommendations.modelled_at

FROM recommendations

LEFT JOIN location_stock
    ON recommendations.variant_id = location_stock.variant_id

ORDER BY
    recommendations.send_from_location_name,
    recommendations.product_title,
    recommendations.variant_title
