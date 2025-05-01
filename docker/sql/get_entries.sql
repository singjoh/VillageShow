select v.name, c.display_order, ca.name, ca.is_child
from vshow.villager v
cross join vshow.current_year cy
join vshow.entrant e
  on e.villager_id = v.id
  and e.year_id = cy.year_id
join vshow.entry ey
  on ey.entrant_id = e.id
join vshow.class c
  on c.id = ey.class_id
join vshow.category ca
  on ca.id = c.category_id
order by 1, 2
