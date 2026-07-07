CREATE OR REPLACE TABLE `{project_id}.{staging_dataset_id}.shopify_orders` AS
SELECT
  SAFE_CAST(record_id AS INT64) AS order_id,
  JSON_VALUE(TO_JSON(payload), '$.name') AS order_name,
  JSON_VALUE(TO_JSON(payload), '$.email') AS customer_email,
  JSON_VALUE(TO_JSON(payload), '$.financial_status') AS financial_status,
  JSON_VALUE(TO_JSON(payload), '$.fulfillment_status') AS fulfillment_status,
  SAFE_CAST(JSON_VALUE(TO_JSON(payload), '$.total_price') AS NUMERIC) AS total_price,
  SAFE_CAST(JSON_VALUE(TO_JSON(payload), '$.subtotal_price') AS NUMERIC) AS subtotal_price,
  SAFE_CAST(JSON_VALUE(TO_JSON(payload), '$.total_tax') AS NUMERIC) AS total_tax,
  SAFE_CAST(JSON_VALUE(TO_JSON(payload), '$.total_discounts') AS NUMERIC) AS total_discounts,
  SAFE_CAST(JSON_VALUE(TO_JSON(payload), '$.currency') AS STRING) AS currency,
  SAFE_CAST(JSON_VALUE(TO_JSON(payload), '$.created_at') AS TIMESTAMP) AS order_created_at,
  SAFE_CAST(JSON_VALUE(TO_JSON(payload), '$.updated_at') AS TIMESTAMP) AS order_updated_at,
  SAFE_CAST(JSON_VALUE(TO_JSON(payload), '$.cancelled_at') AS TIMESTAMP) AS order_cancelled_at,
  source,
  entity,
  extracted_at,
  payload
FROM `{project_id}.{raw_dataset_id}.shopify_orders`;
