insert into vshow.entry (entrant_id, class_id)
select e.id, cl.id
from vshow.current_year cy
join vshow.entrant e
  on e.year_id = cy.year_id
join vshow.villager v
  on v.id = e.villager_id
join vshow.class cl
  on cl.year_id = cy.year_id
join vshow.category ca
  on ca.id = cl.category_id
where v.name = :name
  and ca.name = :catname
  and ca.is_child = :is_child
