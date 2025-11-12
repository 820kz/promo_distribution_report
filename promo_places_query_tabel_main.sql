select distinct 
	pa.promo_id, 
	db.dmp_binding_name,
	ms.shop_code, 
	pads.shop_name,
	pawf.format_value,
	pads.dmp_id
from promo_tabel.promo_actions pa
    left join promo_tabel.promo_action_wars paw on pa.promo_id = paw.promo_id 
    left join promo_tabel.dmp_bindings db on db.dmp_binding_id = pa.dmp_binding_id
    left join promo_tabel.promo_action_war_regions pawr on paw.paw_id  = pawr.paw_id
    left join promo_tabel.promo_action_war_formats pawf on paw.paw_id = pawf.paw_id
    left join nsi.sprut_region_shops ms on pawr.region_code::varchar = ms.region_code::varchar and pawf.format_value::varchar = ms.shop_format::varchar
    left join promo_tabel.promo_action_dmp pad2 on pad2.barcode = paw.barcode and pad2.promo_id = pa.promo_id
    left join promo_tabel.promo_action_dmp_shops pads on pad2.dmp_list_id = pads.dmp_list_id and pads.shop_code::varchar = ms.shop_code::varchar 
where 1 = 1
    and pa.is_arc = 0
    and db.is_arc = 0
    and paw.source_product_id is not null
    and ms.shop_code is not null
    and pads.shop_code is not null
    and upper(trim('
' from dmp_id)) not in ('НЕ УЧАСТВУЕТ', 'КАССА', 'НЕУЧАСТВУЕТ', 'ОЗ', 'УЦЕНКА', 'ДИСПЛЕЙ', 'СЕЗОН', 'E-COM', '#N/A', '0')
    and pa.promo_id = %s
%s
