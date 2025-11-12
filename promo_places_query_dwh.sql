with main as (
	with base_places as
		    (select * from dwh_com.eb_promoplaces)
		    ,
		    temp_places as
		    (
		        select source_store_id,place_id,place_type,category_restriction,brand_restriction, allow_multibrand, is_stm, prices_limit
		        from dwh_com.eb_promoplaces_override 
		        where scenario_name = '%s'
		    )
		    (
		    select distinct base_places.source_store_id store_id
		        ,base_places.place_id
		        ,base_places.place_type
		        ,base_places.category_restriction place_group
		        ,base_places.brand_restriction brand
		        ,base_places.allow_multibrand
		        ,base_places.is_stm
		        ,base_places.prices_limit
		    from base_places
		        left join temp_places on base_places.source_store_id=temp_places.source_store_id 
		            and base_places.place_id=temp_places.place_id
		    where temp_places.place_id is null
		    )
		    union all
		    (select distinct source_store_id store_id
		        ,place_id,place_type
		        ,category_restriction place_group
		        ,brand_restriction brand
		        ,allow_multibrand
		        ,is_stm
		        ,prices_limit
		    from temp_places))
	select store_id,short_name, place_id, place_group,city,store_format
	from main m
	left join dwh_com.dict_store ds on m.store_id = ds.source_store_id
	where upper(place_id) not in ('НЕ УЧАСТВУЕТ', 'КАССА', 'НЕУЧАСТВУЕТ', 'ОЗ', 'УЦЕНКА', 'ДИСПЛЕЙ', 'СЕЗОН', 'E-COM', '#N/A', '0')
	%s