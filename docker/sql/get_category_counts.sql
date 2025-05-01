select display_order, name, sum(case when e.id is null then 0 else 1 end)
from vshow.class c
join vshow.current_year cy
 on cy.year_id = c.year_id
join vshow.category ca
 on ca.id = c.category_id
left join vshow.entry e
 on e.class_id = c.id
group by display_order, name
order by display_order, name
