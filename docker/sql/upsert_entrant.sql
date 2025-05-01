insert into vshow.entrant
  (villager_id, year_id)
select v.id, cy.year_id
from vshow.villager v
cross join vshow.current_year cy
where v.name = :name
and not exists (
  select 1 
  from vshow.entrant e
  join vshow.current_year cy
    on cy.year_id = e.year_id
  join vshow.villager v
    on v.id = e.villager_id
  where name = :name)



