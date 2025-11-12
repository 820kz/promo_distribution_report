select distinct 
	pa.date_start,
	pa.date_end,
	paw.source_product_id,
	ms.shop_code, 
	promo_bonus, 
	trim('
' from dmp_id) as dmp_id,
	purchaise_price_wvat,
	promo_discount,
	paw.promo_price_wvat,
	paw.barcode, 
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
	) as RN,
	paw.brand,
	supllier_name, 
	pads.shop_name,
	pzpt
from promo_tabel.promo_actions pa
    left join promo_tabel.promo_action_wars paw on pa.promo_id = paw.promo_id 
    left join promo_tabel.promo_action_war_regions pawr on paw.paw_id  = pawr.paw_id
    left join promo_tabel.promo_action_war_formats pawf on paw.paw_id = pawf.paw_id
    left join nsi.sprut_region_shops ms on pawr.region_code::varchar = ms.region_code::varchar and pawf.format_value::varchar = ms.shop_format::varchar
    left join promo_tabel.promo_action_dmp pad2 on pad2.barcode = paw.barcode and pad2.promo_id = pa.promo_id
    left join promo_tabel.promo_action_dmp_shops pads on pad2.dmp_list_id = pads.dmp_list_id and pads.shop_code::varchar = ms.shop_code::varchar 
    left join promo_tabel.dmp_types dt on dt.dmp_type_id = paw.dmp_type_id
where 1 = 1
    and pa.is_arc = 0
    and paw.source_product_id is not null
    and ms.shop_code is not null
    and pads.shop_code is not null
    and trim('
' from dmp_id) not in ('НЕ УЧАСТВУЕТ', 'не участвует', 'Не участвует', 'НЕУЧАСТВУЕТ')
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