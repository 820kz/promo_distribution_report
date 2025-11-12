select distinct 
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
				)
