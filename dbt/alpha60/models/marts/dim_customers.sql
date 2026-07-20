WITH latest_customers AS (

  SELECT *
  FROM `alpha60-data-platform.stg.shopify_customers`
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY customer_updated_at DESC
  ) = 1

)

SELECT
  c.customer_id,
  c.email,
  c.first_name,
  c.last_name,
  c.full_name,
  c.phone,

  c.customer_state,
  c.tags,
  c.currency,

  c.orders_count AS shopify_orders_count,
  c.total_spent AS shopify_total_spent,

  c.verified_email,
  c.email_marketing_state,
  c.sms_marketing_state,

  c.customer_created_at,
  c.customer_updated_at,

  c.default_country,
  c.default_country_code,
  c.default_province,
  c.default_province_code,
  c.default_city,
  c.default_postcode,

  COUNT(DISTINCT fs.order_id) AS warehouse_orders_count,
  COALESCE(SUM(fs.quantity), 0) AS lifetime_units_sold,
  COALESCE(SUM(fs.net_sales), 0) AS lifetime_net_sales,
  MIN(fs.order_created_at) AS first_order_at,
  MAX(fs.order_created_at) AS last_order_at,

  CURRENT_TIMESTAMP() AS modelled_at

FROM latest_customers AS c

LEFT JOIN `alpha60-data-platform.warehouse.fact_sales` AS fs
  ON LOWER(c.email) = LOWER(fs.customer_email)

GROUP BY
  c.customer_id,
  c.email,
  c.first_name,
  c.last_name,
  c.full_name,
  c.phone,
  c.customer_state,
  c.tags,
  c.currency,
  c.orders_count,
  c.total_spent,
  c.verified_email,
  c.email_marketing_state,
  c.sms_marketing_state,
  c.customer_created_at,
  c.customer_updated_at,
  c.default_country,
  c.default_country_code,
  c.default_province,
  c.default_province_code,
  c.default_city,
  c.default_postcode
