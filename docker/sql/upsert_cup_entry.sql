with this_row as (
select 
	(select distinct cup.id
	from vshow.current_year cy
	join vshow.judge j
      on j.year_id = cy.year_id
    join vshow.class c
      on c.judge_id = j.id
    join vshow.cup_class cc
      on cc.class_id = c.id
	join vshow.cup cup
      on cup.id = cc.cup_id
     and cup.points_type = false
	where j.judge_code = :code
	  and cup.name = :cup ) as cup_id,
	(select  ey.id
	from vshow.current_year cy
    join vshow.entrant e
      on e.year_id = cy.year_id
    join vshow.entry ey
      on ey.entrant_id = e.id
	where ey.hash = :key ) as entry_id,
	(select year_id from vshow.current_year) as year_id
)  
delete from vshow.cup_entry 
where id in (
   select ce.id
   from this_row x
   join vshow.cup_entry ce
     on ce.cup_id = x.cup_id
     and ce.year_id = x.year_id
   where x.entry_id is null );

with this_row as (
select 
	(select distinct cup.id
	from vshow.current_year cy
	join vshow.judge j
      on j.year_id = cy.year_id
    join vshow.class c
      on c.judge_id = j.id
    join vshow.cup_class cc
      on cc.class_id = c.id
	join vshow.cup cup
      on cup.id = cc.cup_id
     and cup.points_type = false
	where j.judge_code = :code
	  and cup.name = :cup ) as cup_id,
	(select  ey.id
	from vshow.current_year cy
    join vshow.entrant e
      on e.year_id = cy.year_id
    join vshow.entry ey
      on ey.entrant_id = e.id
	where ey.hash = :key ) as entry_id,
	(select year_id from vshow.current_year) as year_id
)  
update vshow.cup_entry ce
set entry_id = x.entry_id, entry_description = :entry_description
from this_row x
where ce.cup_id = x.cup_id
  and ce.year_id = x.year_id
  and x.entry_id is not null;
  
with this_row as (
select 
	(select distinct cup.id
	from vshow.current_year cy
	join vshow.judge j
      on j.year_id = cy.year_id
    join vshow.class c
      on c.judge_id = j.id
    join vshow.cup_class cc
      on cc.class_id = c.id
	join vshow.cup cup
      on cup.id = cc.cup_id
     and cup.points_type = false
	where j.judge_code = :code
	  and cup.name = :cup ) as cup_id,
	(select  ey.id
	from vshow.current_year cy
    join vshow.entrant e
      on e.year_id = cy.year_id
    join vshow.entry ey
      on ey.entrant_id = e.id
	where ey.hash = :key ) as entry_id,
	(select year_id from vshow.current_year) as year_id
)  
insert into vshow.cup_entry (cup_id, year_id, entry_id, entry_description)
select x.cup_id, x.year_id, x.entry_id, :entry_description
from this_row as x
where not exists (
	select 1 from vshow.cup_entry ce
	join this_row y 
	  on y.year_id = ce.year_id
	  and y.cup_id = ce.cup_id
  )
  and x.entry_id is not null;
