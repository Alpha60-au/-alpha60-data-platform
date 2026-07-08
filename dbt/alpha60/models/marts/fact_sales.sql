SELECT
    ol.order_id,
    ol.order_line_id,

    o.order_name,
    ol.order_created_at,

    o.customer_email,

    ol.product_id,
    ol.variant_id,

    ol.product_key,
    ol.product_name,
    ol.variant_title,
    ol.sku,
    ol.vendor,

    ol.quantity,

    ol.unit_price,
    ol.total_discount,

    (ol.unit_price * ol.quantity) - ol.total_discount AS net_sales,

    o.financial_status,
    o.fulfillment_status,

    o.currency,

    CURRENT_TIMESTAMP() AS modelled_at

FROM `alpha60-data-platform.stg.shopify_order_lines` AS ol

JOIN `alpha60-data-platform.stg.shopify_orders` AS o
  ON ol.order_id = o.order_id
