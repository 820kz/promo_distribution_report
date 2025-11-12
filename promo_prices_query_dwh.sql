WITH 
    base_places AS (
        SELECT * FROM dwh_com.eb_promoplaces
    ),
    temp_places AS (
        SELECT source_store_id, place_id, place_type, category_restriction, brand_restriction, allow_multibrand, is_stm, prices_limit
        FROM dwh_com.eb_promoplaces_override 
        WHERE scenario_name LIKE '%s'
    ),
    main AS (
        (
            SELECT DISTINCT base_places.source_store_id store_id
                ,base_places.place_id
                ,base_places.place_type
                ,base_places.category_restriction place_group
                ,base_places.brand_restriction brand
                ,base_places.allow_multibrand
                ,base_places.is_stm
                ,base_places.prices_limit
            FROM base_places
            LEFT JOIN temp_places ON base_places.source_store_id=temp_places.source_store_id 
                AND base_places.place_id=temp_places.place_id
            WHERE temp_places.place_id IS NULL
        )
        UNION ALL
        (
            SELECT DISTINCT source_store_id store_id
                ,place_id,place_type
                ,category_restriction place_group
                ,brand_restriction brand
                ,allow_multibrand
                ,is_stm
                ,prices_limit
            FROM temp_places
        )
    )
select distinct
	m.store_id::varchar,
	ds.store_format,
    ds.city,
	m.place_id,
	m.place_type,
	m.place_group,
	--m.brand,
	--m.allow_multibrand,
	--m.is_stm,
	m.prices_limit
FROM main m
left join dwh_com.dict_store ds on m.store_id = ds.source_store_id
where 1 = 1
    --and upper(m.place_id) not in ('НЕ УЧАСТВУЕТ', 'КАССА', 'НЕУЧАСТВУЕТ', 'ОЗ', 'УЦЕНКА', 'ДИСПЛЕЙ', 'СЕЗОН', 'E-COM', '#N/A', '0')
    --and m.place_type in ('Т', 'П', 'СТ', 'КК', 'СП', 'TXO', 'TB')
;