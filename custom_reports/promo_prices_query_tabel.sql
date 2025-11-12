select distinct 
	db.dmp_binding_name as scenario_name,
	pads.shop_code::varchar,
    pads.shop_name as "Торговый зал",
    ms.shop_format as "Формат",
    pads.dmp_id as "Промо-место",
    dmp_type_value as "Тип ДМП",
    count(distinct paw.promo_price_wvat) as "Факт цен"
from promo_tabel.promo_actions pa
    left join promo_tabel.promo_action_wars paw on pa.promo_id = paw.promo_id 
    left join promo_tabel.promo_action_war_regions pawr on paw.paw_id  = pawr.paw_id
    left join promo_tabel.promo_action_war_formats pawf on paw.paw_id = pawf.paw_id
    left join nsi.sprut_region_shops ms on pawr.region_code::varchar = ms.region_code::varchar and pawf.format_value::varchar = ms.shop_format::varchar
    left join promo_tabel.promo_action_dmp pad2 on pad2.barcode = paw.barcode and pad2.promo_id = pa.promo_id
    left join promo_tabel.promo_action_dmp_shops pads on pad2.dmp_list_id = pads.dmp_list_id and pads.shop_code::varchar = ms.shop_code::varchar 
    left join promo_tabel.dmp_types dt on dt.dmp_type_id = paw.dmp_type_id
	left join promo_tabel.dmp_bindings db on db.dmp_binding_id = pa.dmp_binding_id
where 1 = 1
    and pa.is_arc = 0
    and ms.shop_code is not null
    and pads.shop_code is not NULL
    AND pa.promo_id = %s
	group by 1,2,3,4,5,6
%s