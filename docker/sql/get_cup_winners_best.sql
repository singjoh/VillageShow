select x.cup_number, x.name, x.description, ca.name, v.name, ce.entry_description
from (
    select distinct cup.id cup_id, cup.cup_number, cup.name, cup.description, cy.year_id
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
     ) as x
join vshow.cup_entry ce
  on ce.cup_id = x.cup_id
  and ce.year_id = x.year_id
join vshow.entry e
  on e.id = ce.entry_id
join vshow.entrant ea
  on ea.id = e.entrant_id
join vshow.villager v
  on v.id = ea.villager_id
join vshow.class c
  on c.id = e.class_id
join vshow.category ca
  on ca.id = c.category_id
order by 1, 2
