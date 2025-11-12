with agg_formats as (
    -- Форматы через запятую
	select pawr.region_code, paw.paw_id,
		paw.source_product_id, 
		string_agg(distinct pawf.format_value, ', ') as format_values 
	from promo_tabel.promo_actions pa
	    left join promo_tabel.promo_action_wars paw on pa.promo_id = paw.promo_id 
	    left join promo_tabel.promo_action_war_regions pawr on paw.paw_id  = pawr.paw_id
	    left join promo_tabel.promo_action_war_formats pawf on paw.paw_id = pawf.paw_id
	where 1 = 1
	    and pa.is_arc = 0
	    and paw.source_product_id is not null
	    AND pa.promo_id = %s
	GROUP BY pawr.region_code, paw.paw_id, paw.source_product_id)
select distinct 
	(
	SELECT
	    e.full_name
	FROM
	    adm.roles r
	JOIN adm.system_roles sr ON sr.role_id = r.role_id
	JOIN adm.employee_system_roles esr ON esr.system_role_id = sr.system_role_id
	JOIN nsi.employees e ON e.emp_id = esr.emp_id AND e.is_arc = 0
	JOIN (
	    SELECT esr3.emp_id, parg1.group_code
	    FROM 						
	        adm.employee_system_roles esr3
	    JOIN promo_tabel.promo_action_roles par1 ON esr3.system_role_id = par1.system_role_id
	    JOIN promo_tabel.promo_action_role_regions parr1 ON par1.par_id = parr1.par_id 
	    JOIN promo_tabel.promo_action_role_groups parg1 ON par1.par_id = parg1.par_id 
	    WHERE parr1.region_code = '1' AND parg1.group_code = paw.l5_code
	) subq ON e.emp_id = subq.emp_id
	WHERE r.role_code = 'promoTabelRN'
	LIMIT 1
	) as "РН",
	paw.user_full_name as "КМ",
	paw.l3 as "Отдел",
    paw.l4 as "Группа",
    paw.l5 as "Подгруппа",
    null as "АФ",
    null as "АСТ",
    null as "КФ",
    null as "ШФ",
    null as "ТКФ",
    null as "ППФ",
    null as "КЗФ",
    null as "ТЗФ",
    null as "ТФ",
    null as "УКФ",
    ms.region_name as "Регион проведения акции",
    --paw.action_type_id as "Тип акции",  
    af.format_values as "Форматы",
	paw.top_wars as "Топ товаров",   
    paw.module as "Модуль",
    paw.barcode as "Штрих-код",
    paw.source_product_id as "Код товара в Спрут",
    paw.name_ware as "Наименование товара",
    paw.supplier_name as "Наименование поставщика",
    paw.brand as "Торговая марка",
    paw.regular_price_wvat as "Регулярная розничная цена с НДС,тг",
    paw.promo_price_wvat as "Акционная цена с НДС, тг",
    paw.promo_discount as "Скидка для покупателя, %%",	
	null as "Исключить ТК Алматы",
	null as "Исключить ТК Астаны",
	null as "Исключить ТК Караганды",
	null as "Исключить ТК Шымкент",
	null as "Исключить ТК Талдыкорган",
	null as "Исключить ТК Петропавловск",
	null as "Исключить ТК Кызылорда",
	null as "Исключить ТК Тараз",
	null as "Исключить ТК Туркестан",
	null as "Исключить ТК Усть-Каменогорск",
    concat(pads.shop_name, ' ', pawf.format_value) as shop_name,
    case when upper(pads.dmp_id) = 'НЕУЧАСТВУЕТ' then 'НЕ УЧАСТВУЕТ' else pads.dmp_id end as dmp_id
from promo_tabel.promo_actions pa
    left join promo_tabel.promo_action_wars paw on pa.promo_id = paw.promo_id 
    left join promo_tabel.promo_action_war_regions pawr on paw.paw_id  = pawr.paw_id
    left join promo_tabel.promo_action_war_formats pawf on paw.paw_id = pawf.paw_id
    left join nsi.sprut_region_shops ms on pawr.region_code::varchar = ms.region_code::varchar and pawf.format_value::varchar = ms.shop_format::varchar
    left join promo_tabel.promo_action_dmp pad2 on pad2.barcode = paw.barcode and pad2.promo_id = pa.promo_id
    left join promo_tabel.promo_action_dmp_shops pads on pad2.dmp_list_id = pads.dmp_list_id and pads.shop_code::varchar = ms.shop_code::varchar 
    left join promo_tabel.dmp_types dt on dt.dmp_type_id = paw.dmp_type_id
    left join agg_formats af on af.region_code = pawr.region_code and af.source_product_id = paw.source_product_id and paw.paw_id = af.paw_id
    left join promo_tabel.share_mechanics smm on paw.sm_id = smm.sm_id
where 1 = 1
    and pa.is_arc = 0
    and paw.source_product_id is not null
    and ms.shop_code is not null
    and pads.shop_code is not NULL
    AND pa.promo_id = %s
    and paw.module in ('1', '0')
	and pawr.region_code::int4 in (select distinct 
										cast(parr.region_code as int4) 
									from
										promo_tabel.promo_action_roles par,
										promo_tabel.promo_action_role_regions parr 
									where
										par.par_id  = parr.par_id 
										and par.system_role_id in (
											select
												sr.system_role_id
											from
												adm.system_roles sr,
												adm.employee_system_roles esr,
												nsi.employees e2 
											where sr.system_role_id = esr.system_role_id 	
											and esr.emp_id = e2.emp_id 
											and upper(e2.account_name) = upper('%s')))
		and ms.shop_format in (select distinct 
										parf.format_code 	
									from
										promo_tabel.promo_action_roles par,
										promo_tabel.promo_action_role_formats parf 
									where
										par.par_id  = parf.par_id 
										and par.system_role_id in (
											select
												sr.system_role_id
											from
												adm.system_roles sr,
												adm.employee_system_roles esr,
												nsi.employees e2 
											where sr.system_role_id = esr.system_role_id 	
											and esr.emp_id = e2.emp_id 
											and upper(e2.account_name) = upper('%s')
										))
		and SPLIT_PART(paw.l5, ' ', 1) in (select distinct 
											parg.group_code 	
											from
												promo_tabel.promo_action_roles par,
												promo_tabel.promo_action_role_groups parg 
											where
												par.par_id  = parg.par_id 
												and par.system_role_id in (
													select
														sr.system_role_id
													from
														adm.system_roles sr,
														adm.employee_system_roles esr,
														nsi.employees e2 
													where sr.system_role_id = esr.system_role_id 	
													and esr.emp_id = e2.emp_id 
													and upper(e2.account_name) = upper('%s')
													))
%s
    