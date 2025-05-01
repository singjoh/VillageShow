select display_order, name, is_child
from vshow.class c
join vshow.current_year cy
 on cy.year_id = c.year_id
join vshow.category ca
 on ca.id = c.category_id
