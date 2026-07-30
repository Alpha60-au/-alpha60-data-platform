{{ config(materialized='view') }}

SELECT
    fis.location_name,
    fis.product_title,
    fis.variant_title,
    fis.sku,
    fis.product_type,
    fis.product_status,
    fis.available_quantity,
    ABS(fis.available_quantity) AS negative_units,
    fis.inventory_level_updated_at,
    fis.modelled_at

FROM {{ ref('fact_inventory_snapshot') }} fis

JOIN `alpha60-data-platform.stg.shopify_products` p
  ON fis.product_id = p.product_id

WHERE fis.available_quantity < 0

  AND fis.location_name IN (
      'Claremont',
      'Fitzroy',
      'Flinders Lane',
      'James St',
      'Newtown',
      'Oxford St',
      'Online / Warehouse',
      'Smith St'
  )

  AND EXISTS (
      SELECT 1
      FROM UNNEST(SPLIT(COALESCE(p.tags, ''), ',')) AS tag
      WHERE UPPER(TRIM(tag)) = 'SEASON_AW26'
  )

ORDER BY
    fis.location_name,
    fis.available_quantity ASC,
    fis.product_title,
    fis.variant_title
