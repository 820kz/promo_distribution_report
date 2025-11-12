select distinct 
	paw.l3 as "Отдел",
    paw.l4 as "Группа",
    paw.l5 as "Подгруппа",
    paw.barcode as "Штрих-код",
	--db.dmp_binding_name,
    concat(pads.shop_name, ' ', pawf.format_value) as shop_name,
    paw.source_product_id as "Код товара в Спрут",
    paw.name_ware as "Наименование товара",
    paw.brand as "Торговая марка",
    pads.supllier_name as "Наименование поставщика",
	paw.regular_price_wvat as "Регулярная розничная цена с НДС,тг",
	paw.promo_price_wvat as "Акционная цена с НДС, тг",
	paw.promo_discount / 100 as "Скидка для покупателя, %%",
	dt.dmp_type_value as "Тип ДМП",
    case when ms.shop_name = 'ТЗ ТФ №3 EXPRESS' then 'Шымкент' else  ms.region_name end as "Регион проведения акции",
	pads.dmp_id
from promo_tabel.promo_actions pa
    left join promo_tabel.promo_action_wars paw on pa.promo_id = paw.promo_id 
    left join promo_tabel.dmp_types dt on dt.dmp_type_id = paw.dmp_type_id
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
--     and upper(trim('
-- ' from dmp_id)) not in ('НЕ УЧАСТВУЕТ', 'КАССА', 'НЕУЧАСТВУЕТ', 'ОЗ', 'УЦЕНКА', 'ДИСПЛЕЙ', 'СЕЗОН', 'E-COM', '#N/A', '0')
    and pa.promo_id = %s
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