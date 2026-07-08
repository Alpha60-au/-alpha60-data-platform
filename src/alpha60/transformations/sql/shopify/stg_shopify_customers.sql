CREATE OR REPLACE TABLE `{project_id}.{staging_dataset_id}.shopify_customers` AS
SELECT
  SAFE_CAST(record_id AS INT64) AS customer_id,

  LOWER(JSON_VALUE(payload, '$.email')) AS email,
  JSON_VALUE(payload, '$.first_name') AS first_name,
  JSON_VALUE(payload, '$.last_name') AS last_name,
  TRIM(CONCAT(
    COALESCE(JSON_VALUE(payload, '$.first_name'), ''),
    ' ',
    COALESCE(JSON_VALUE(payload, '$.last_name'), '')
  )) AS full_name,

  JSON_VALUE(payload, '$.phone') AS phone,
  JSON_VALUE(payload, '$.state') AS customer_state,
  JSON_VALUE(payload, '$.tags') AS tags,
  JSON_VALUE(payload, '$.currency') AS currency,

  SAFE_CAST(JSON_VALUE(payload, '$.orders_count') AS INT64) AS orders_count,
  SAFE_CAST(JSON_VALUE(payload, '$.total_spent') AS NUMERIC) AS total_spent,

  SAFE_CAST(JSON_VALUE(payload, '$.verified_email') AS BOOL) AS verified_email,
  SAFE_CAST(JSON_VALUE(payload, '$.tax_exempt') AS BOOL) AS tax_exempt,

  JSON_VALUE(payload, '$.email_marketing_consent.state') AS email_marketing_state,
  JSON_VALUE(payload, '$.email_marketing_consent.opt_in_level') AS email_marketing_opt_in_level,
  SAFE_CAST(
    JSON_VALUE(payload, '$.email_marketing_consent.consent_updated_at')
    AS TIMESTAMP
  ) AS email_marketing_consent_updated_at,

  JSON_VALUE(payload, '$.sms_marketing_consent.state') AS sms_marketing_state,
  JSON_VALUE(payload, '$.sms_marketing_consent.opt_in_level') AS sms_marketing_opt_in_level,
  SAFE_CAST(
    JSON_VALUE(payload, '$.sms_marketing_consent.consent_updated_at')
    AS TIMESTAMP
  ) AS sms_marketing_consent_updated_at,

  SAFE_CAST(JSON_VALUE(payload, '$.created_at') AS TIMESTAMP) AS customer_created_at,
  SAFE_CAST(JSON_VALUE(payload, '$.updated_at') AS TIMESTAMP) AS customer_updated_at,

  SAFE_CAST(JSON_VALUE(payload, '$.last_order_id') AS INT64) AS last_order_id,
  JSON_VALUE(payload, '$.last_order_name') AS last_order_name,

  JSON_VALUE(payload, '$.default_address.country') AS default_country,
  JSON_VALUE(payload, '$.default_address.country_code') AS default_country_code,
  JSON_VALUE(payload, '$.default_address.province') AS default_province,
  JSON_VALUE(payload, '$.default_address.province_code') AS default_province_code,
  JSON_VALUE(payload, '$.default_address.city') AS default_city,
  JSON_VALUE(payload, '$.default_address.zip') AS default_postcode,
  JSON_VALUE(payload, '$.default_address.phone') AS default_phone,

  source,
  entity,
  extracted_at,
  payload

FROM `{project_id}.{raw_dataset_id}.shopify_customers`;
