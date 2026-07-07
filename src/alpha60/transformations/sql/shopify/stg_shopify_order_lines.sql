CREATE OR REPLACE TABLE `{project_id}.{staging_dataset_id}.shopify_order_lines` AS
SELECT
  SAFE_CAST(raw_orders.record_id AS INT64) AS order_id,
  JSON_VALUE(TO_JSON(raw_orders.payload), '$.name') AS order_name,

  SAFE_CAST(JSON_VALUE(line_item, '$.id') AS INT64) AS order_line_id,
  SAFE_CAST(JSON_VALUE(line_item, '$.product_id') AS INT64) AS product_id,
  SAFE_CAST(JSON_VALUE(line_item, '$.variant_id') AS INT64) AS variant_id,

  JSON_VALUE(line_item, '$.sku') AS sku,
  JSON_VALUE(line_item, '$.name') AS product_name,
  JSON_VALUE(line_item, '$.variant_title') AS variant_title,
  JSON_VALUE(line_item, '$.vendor') AS vendor,

  CASE
    WHEN JSON_VALUE(line_item, '$.product_id') IS NOT NULL THEN 'product'
    WHEN JSON_VALUE(line_item, '$.sku') IS NOT NULL
      AND JSON_VALUE(line_item, '$.sku') != '' THEN 'sku_only'
    ELSE 'non_product_item'
  END AS product_reference_status,

  COALESCE(
    JSON_VALUE(line_item, '$.product_id'),
    JSON_VALUE(line_item, '$.sku')
  ) AS product_key,

  SAFE_CAST(JSON_VALUE(line_item, '$.quantity') AS INT64) AS quantity,
  SAFE_CAST(JSON_VALUE(line_item, '$.price') AS NUMERIC) AS unit_price,
  SAFE_CAST(JSON_VALUE(line_item, '$.total_discount') AS NUMERIC) AS total_discount,

  SAFE_CAST(
    JSON_VALUE(TO_JSON(raw_orders.payload), '$.created_at')
    AS TIMESTAMP
  ) AS order_created_at,

  SAFE_CAST(
    JSON_VALUE(TO_JSON(raw_orders.payload), '$.updated_at')
    AS TIMESTAMP
  ) AS order_updated_at,

  raw_orders.source,
  raw_orders.entity,
  raw_orders.extracted_at,
  line_item AS payload

FROM `{project_id}.{raw_dataset_id}.shopify_orders` AS raw_orders

CROSS JOIN UNNEST(
  JSON_QUERY_ARRAY(TO_JSON(raw_orders.payload), '$.line_items')
) AS line_item;
