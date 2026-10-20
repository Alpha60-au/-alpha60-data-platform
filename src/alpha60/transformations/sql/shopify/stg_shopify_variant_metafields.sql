CREATE OR REPLACE TABLE `{project_id}.{staging_dataset_id}.shopify_variant_metafields` AS
WITH latest_variants AS (
  SELECT * EXCEPT(row_num)
  FROM (
    SELECT
      *,
      ROW_NUMBER() OVER (
        PARTITION BY record_id
        ORDER BY extracted_at DESC
      ) AS row_num
    FROM `{project_id}.{raw_dataset_id}.shopify_variant_metafields`
  )
  WHERE row_num = 1
)

SELECT
  SAFE_CAST(record_id AS INT64) AS variant_id,

  CAST(SAFE_CAST(MAX(IF(
    JSON_VALUE(metafield, '$.key') = 'desired_stock_level_claremont',
    JSON_VALUE(metafield, '$.value'),
    NULL
  )) AS NUMERIC) AS INT64) AS desired_stock_level_claremont,

  CAST(SAFE_CAST(MAX(IF(
    JSON_VALUE(metafield, '$.key') = 'desired_stock_level_james_st',
    JSON_VALUE(metafield, '$.value'),
    NULL
  )) AS NUMERIC) AS INT64) AS desired_stock_level_james_st,

  CAST(SAFE_CAST(MAX(IF(
    JSON_VALUE(metafield, '$.key') = 'desired_stock_level_oxford_st',
    JSON_VALUE(metafield, '$.value'),
    NULL
  )) AS NUMERIC) AS INT64) AS desired_stock_level_oxford_st,

  CAST(SAFE_CAST(MAX(IF(
    JSON_VALUE(metafield, '$.key') = 'desired_stock_level_newtown',
    JSON_VALUE(metafield, '$.value'),
    NULL
  )) AS NUMERIC) AS INT64) AS desired_stock_level_newtown,

  CAST(SAFE_CAST(MAX(IF(
    JSON_VALUE(metafield, '$.key') = 'desired_stock_level_smith_st',
    JSON_VALUE(metafield, '$.value'),
    NULL
  )) AS NUMERIC) AS INT64) AS desired_stock_level_smith_st,

  CAST(SAFE_CAST(MAX(IF(
    JSON_VALUE(metafield, '$.key') = 'desired_stock_level_fitzroy',
    JSON_VALUE(metafield, '$.value'),
    NULL
  )) AS NUMERIC) AS INT64) AS desired_stock_level_fitzroy,

  CAST(SAFE_CAST(MAX(IF(
    JSON_VALUE(metafield, '$.key') = 'desired_stock_level_melbourne',
    JSON_VALUE(metafield, '$.value'),
    NULL
  )) AS NUMERIC) AS INT64) AS desired_stock_level_flinders_lane,

  MAX(extracted_at) AS metafields_extracted_at

FROM latest_variants
LEFT JOIN UNNEST(
  JSON_QUERY_ARRAY(payload, '$.metafields')
) AS metafield
  ON TRUE
GROUP BY record_id;
