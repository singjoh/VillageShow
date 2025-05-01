with todel as (
  select ey.id
  from vshow.current_year cy
  join vshow.entrant e
    on e.year_id = cy.year_id
  join vshow.villager v
    on v.id = e.villager_id
  join vshow.entry ey
    on ey.entrant_id = e.id
  where v.name = 'Baby Test-Case'
)
update vshow.class c 
set 
  gold_entry_id = case when c.gold_entry_id in (select id from todel) then NULL else c.gold_entry_id end, 
  silver_entry_id = case when c.silver_entry_id in (select id from todel) then NULL else c.silver_entry_id end,
  bronze_entry_id = case when c.bronze_entry_id in (select id from todel) then NULL else c.bronze_entry_id end 
where c.gold_entry_id in (select id from todel)
or c.silver_entry_id in (select id from todel)
or c.bronze_entry_id in (select id from todel);

with todel as (
  select ey.id
  from vshow.current_year cy
  join vshow.entrant e
    on e.year_id = cy.year_id
  join vshow.villager v
    on v.id = e.villager_id
  join vshow.entry ey
    on ey.entrant_id = e.id
  where v.name = 'Baby Test-Case'
)
delete from vshow.cup_entry ce
where ce.entry_id in (select id from todel);

delete from vshow.entry
where id 
in (
  select ey.id
  from vshow.current_year cy
  join vshow.entrant e 
    on e.year_id = cy.year_id
  join vshow.villager v
    on v.id = e.villager_id
  join vshow.entry ey
    on ey.entrant_id = e.id
  where v.name = :name
);

delete from vshow.entrant
where id 
in (
  select e.id
  from vshow.current_year cy
  join vshow.entrant e 
    on e.year_id = cy.year_id
  join vshow.villager v
    on v.id = e.villager_id
  where v.name = :name
)
and :del_entrant


