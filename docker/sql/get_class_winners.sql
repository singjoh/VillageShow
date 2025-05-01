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
select c.display_order, ca.name, g.name, s.name, b.name
from vshow.current_year cy
join vshow.class c
  on c.year_id = cy.year_id
join vshow.category ca
  on ca.id = c.category_id
left join entry_lookup g
  on g.id = c.gold_entry_id
left join entry_lookup s
  on s.id = c.silver_entry_id
left join entry_lookup b
  on b.id = c.bronze_entry_id
order by 1, 2
