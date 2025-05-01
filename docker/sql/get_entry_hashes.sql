select v.name, c.display_order, ca.name, y.hash, is_child
from vshow.current_year cy
join vshow.entrant e
  on e.year_id = cy.year_id
join vshow.villager v
  on v.id = e.villager_id
join vshow.entry y
  on y.entrant_id = e.id
join vshow.class c
  on c.id = y.class_id
join vshow.category ca
  on ca.id = c.category_id
order by 1, 2
