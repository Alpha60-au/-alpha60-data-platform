SELECT
    product_id,

    REGEXP_CONTAINS(
        LOWER(COALESCE(tags, '')),
        r'(^|,\s*)season_aw26(\s*,|$)'
    ) AS is_season_aw26,

    REGEXP_CONTAINS(
        LOWER(COALESCE(tags, '')),
        r'(^|,\s*)aw26 rotations'
    ) AS is_aw26_rotation_excluded,

    REGEXP_CONTAINS(
        LOWER(COALESCE(product_title, '')),
        r'\bsocks?\b'
    ) AS is_sock,

    REGEXP_CONTAINS(
        LOWER(COALESCE(tags, '')),
        r'(^|,\s*)classics(\s*,|$)'
    ) AS is_classics,

    CURRENT_TIMESTAMP() AS modelled_at

FROM `alpha60-data-platform.warehouse.dim_products`
