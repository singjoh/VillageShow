select display_order, ca.name, ca.is_child
from vshow.cup
join vshow.cup_class cc
	on cc.cup_id = cup.id
join vshow.class c
	on c.id = cc.class_id
join vshow.current_year cy
    on cy.year_id = c.year_id
join vshow.category ca
	on ca.id = c.category_id
where cup.sname = :cup
