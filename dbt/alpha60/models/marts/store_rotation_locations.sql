SELECT
    location_id,
    location_name,

    CASE
        WHEN location_name IN (
            'Online / Warehouse',
            'Faulty Land',
            'Sparehouse',
            'Melbourne Outlet',
            'Spring1883',
            'Smith St',
            'Paddington'
        ) THEN FALSE
        ELSE TRUE
    END AS can_send_rotations,

    CASE
        WHEN location_name IN (
            'Claremont',
            'Wellington',
            'James St',
            'Paddington',
            'Online / Warehouse',
            'Faulty Land',
            'Sparehouse',
            'Melbourne Outlet',
            'Spring1883'
        ) THEN FALSE
        ELSE TRUE
    END AS can_receive_rotations,

    CASE
        WHEN location_name = 'Flinders Lane' THEN 100
        WHEN location_name = 'Fitzroy' THEN 95
        WHEN location_name = 'Smith St' THEN 90
        WHEN location_name = 'Newtown' THEN 85
        WHEN location_name = 'Oxford St' THEN 80
        ELSE 0
    END AS rotation_priority,

    CURRENT_TIMESTAMP() AS modelled_at

FROM `alpha60-data-platform.warehouse.dim_locations`
