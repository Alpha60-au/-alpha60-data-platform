CREATE OR REPLACE TABLE `{project_id}.{staging_dataset_id}.shopify_product_variants` AS
SELECT
  SAFE_CAST(raw_products.record_id AS INT64) AS product_id,
  CAST(raw_products.record_id AS STRING) AS product_key,

  SAFE_CAST(JSON_VALUE(variant, '$.id') AS INT64) AS variant_id,
  CAST(JSON_VALUE(variant, '$.id') AS STRING) AS variant_key,

  JSON_VALUE(variant, '$.sku') AS sku,
  JSON_VALUE(variant, '$.title') AS variant_title,
  JSON_VALUE(variant, '$.barcode') AS barcode,

  SAFE_CAST(JSON_VALUE(variant, '$.price') AS NUMERIC) AS price,
  SAFE_CAST(JSON_VALUE(variant, '$.compare_at_price') AS NUMERIC) AS compare_at_price,
  SAFE_CAST(JSON_VALUE(variant, '$.inventory_quantity') AS INT64) AS inventory_quantity,
  JSON_VALUE(variant, '$.inventory_policy') AS inventory_policy,
  JSON_VALUE(variant, '$.inventory_management') AS inventory_management,

  SAFE_CAST(JSON_VALUE(variant, '$.created_at') AS TIMESTAMP) AS variant_created_at,
  SAFE_CAST(JSON_VALUE(variant, '$.updated_at') AS TIMESTAMP) AS variant_updated_at,

  JSON_VALUE(TO_JSON(raw_products.payload), '$.title') AS product_title,
  JSON_VALUE(TO_JSON(raw_products.payload), '$.vendor') AS vendor,
  JSON_VALUE(TO_JSON(raw_products.payload), '$.product_type') AS product_type,
  JSON_VALUE(TO_JSON(raw_products.payload), '$.status') AS product_status,

  raw_products.source,
  raw_products.entity,
  raw_products.extracted_at,
  variant AS payload

FROM `{project_id}.{raw_dataset_id}.shopify_products` AS raw_products

CROSS JOIN UNNEST(
  JSON_QUERY_ARRAY(TO_JSON(raw_products.payload), '$.variants')
) AS variant;
