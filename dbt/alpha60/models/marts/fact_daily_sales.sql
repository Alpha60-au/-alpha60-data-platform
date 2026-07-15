WITH locations AS (
    SELECT
        location_id,
        location_name,
        sales_location_name
    FROM {{ ref('dim_locations') }}
),

order_shipping AS (
    SELECT
        orders.order_id,
        SUM(
            COALESCE(
                SAFE_CAST(
                    JSON_VALUE(shipping_line, '$.discounted_price')
                    AS NUMERIC
                ),
                SAFE_CAST(
                    JSON_VALUE(shipping_line, '$.price')
                    AS NUMERIC
                ),
                0
            )
        ) AS shipping_sales
    FROM `alpha60-data-platform.stg.shopify_orders` AS orders

    LEFT JOIN UNNEST(
        JSON_QUERY_ARRAY(orders.payload, '$.shipping_lines')
    ) AS shipping_line

    GROUP BY orders.order_id
),

order_events AS (
    SELECT
        DATE(
            orders.order_created_at,
            'Australia/Melbourne'
        ) AS trading_date,

        locations.location_id,
        COALESCE(
            locations.location_name,
            orders.sales_location_name,
            'Unknown'
        ) AS location_name,

        orders.sales_location_name,

        orders.subtotal_price
            + orders.total_discounts AS gross_sales,

        orders.total_discounts AS discounts,
        CAST(0 AS NUMERIC) AS returns,
        COALESCE(order_shipping.shipping_sales, 0) AS shipping_sales,
        orders.total_tax AS taxes,

        orders.subtotal_price
            + COALESCE(order_shipping.shipping_sales, 0)
            + orders.total_tax AS total_sales,

        1 AS order_count,
        CAST(0 AS INT64) AS returned_units

    FROM `alpha60-data-platform.stg.shopify_orders` AS orders

    LEFT JOIN order_shipping
        ON orders.order_id = order_shipping.order_id

    LEFT JOIN locations
        ON orders.sales_location_name = locations.sales_location_name

    WHERE orders.order_cancelled_at IS NULL
),

refund_events AS (
    SELECT
        DATE(
            SAFE_CAST(
                JSON_VALUE(refund, '$.processed_at')
                AS TIMESTAMP
            ),
            'Australia/Melbourne'
        ) AS trading_date,

        COALESCE(
            SAFE_CAST(
                JSON_VALUE(refund_line, '$.location_id')
                AS INT64
            ),
            SAFE_CAST(
                JSON_VALUE(
                    JSON_QUERY_ARRAY(
                        refund,
                        '$.transactions'
                    )[SAFE_OFFSET(0)],
                    '$.location_id'
                )
                AS INT64
            )
        ) AS location_id,

        SUM(
            COALESCE(
                SAFE_CAST(
                    JSON_VALUE(refund_line, '$.subtotal')
                    AS NUMERIC
                ),
                0
            )
        ) AS returns,

        SUM(
            COALESCE(
                SAFE_CAST(
                    JSON_VALUE(refund_line, '$.total_tax')
                    AS NUMERIC
                ),
                0
            )
        ) AS returned_tax,

        SUM(
            COALESCE(
                SAFE_CAST(
                    JSON_VALUE(refund_line, '$.quantity')
                    AS INT64
                ),
                0
            )
        ) AS returned_units

    FROM `alpha60-data-platform.stg.shopify_orders` AS orders

    CROSS JOIN UNNEST(
        JSON_QUERY_ARRAY(orders.payload, '$.refunds')
    ) AS refund

    LEFT JOIN UNNEST(
        JSON_QUERY_ARRAY(refund, '$.refund_line_items')
    ) AS refund_line

    WHERE orders.order_cancelled_at IS NULL

    GROUP BY
        trading_date,
        location_id
),

normalised_refund_events AS (
    SELECT
        refund_events.trading_date,
        refund_events.location_id,
        COALESCE(
            locations.location_name,
            'Unknown'
        ) AS location_name,
        locations.sales_location_name,

        CAST(0 AS NUMERIC) AS gross_sales,
        CAST(0 AS NUMERIC) AS discounts,
        refund_events.returns,
        CAST(0 AS NUMERIC) AS shipping_sales,
        -refund_events.returned_tax AS taxes,

        -refund_events.returns
            - refund_events.returned_tax AS total_sales,

        0 AS order_count,
        refund_events.returned_units

    FROM refund_events

    LEFT JOIN locations
        ON refund_events.location_id = locations.location_id
),

all_sales_events AS (
    SELECT * FROM order_events

    UNION ALL

    SELECT * FROM normalised_refund_events
)

SELECT
    trading_date,
    location_id,
    location_name,
    sales_location_name,

    SUM(gross_sales) AS gross_sales,
    SUM(discounts) AS discounts,
    SUM(returns) AS returns,
    SUM(shipping_sales) AS shipping_sales,
    SUM(taxes) AS taxes,
    SUM(total_sales) AS total_sales,

    SUM(order_count) AS order_count,
    SUM(returned_units) AS returned_units,

    CURRENT_TIMESTAMP() AS modelled_at

FROM all_sales_events

WHERE trading_date IS NOT NULL

GROUP BY
    trading_date,
    location_id,
    location_name,
    sales_location_name
