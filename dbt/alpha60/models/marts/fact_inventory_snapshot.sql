SELECT
    il.inventory_level_key,

    il.location_id,
    l.location_name,
    l.city,

    pv.inventory_item_id,

    pv.product_id,
    pv.variant_id,

    pv.product_title,
    pv.variant_title,

    pv.sku,
    pv.vendor,
    pv.product_type,

    COALESCE(il.available_quantity, 0) AS available_quantity,

    p.status AS product_status,

    il.inventory_level_updated_at,
    CURRENT_TIMESTAMP() AS modelled_at

FROM `alpha60-data-platform.stg.shopify_inventory_levels` il

JOIN `alpha60-data-platform.stg.shopify_product_variants` pv
  ON il.inventory_item_id = pv.inventory_item_id

JOIN `alpha60-data-platform.stg.shopify_products` p
  ON pv.product_id = p.product_id

JOIN `alpha60-data-platform.stg.shopify_locations` l
  ON il.location_id = l.location_id
