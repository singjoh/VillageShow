with entry_lookup as (
  select e.id, v.name
  from vshow.entry e
  join vshow.entrant ea
  	on ea.id = e.entrant_id
  join vshow.current_year cy
    on cy.year_id = ea.year_id
  join vshow.villager v
    on v.id = ea.villager_id
)
select cu.cup_number, cu.name, cu.description, c.display_order, ca.name, ca.is_child, g.name, s.name, b.name
from vshow.current_year cy
join vshow.class c
  on c.year_id = cy.year_id
join vshow.category ca
  on ca.id = c.category_id
join vshow.cup_class cc
  on cc.class_id = c.id
join vshow.cup cu
  on cu.id = cc.cup_id
  and cu.points_type = true
left join entry_lookup g
  on g.id = c.gold_entry_id
left join entry_lookup s
  on s.id = c.silver_entry_id
left join entry_lookup b
  on b.id = c.bronze_entry_id
order by 1, 2
