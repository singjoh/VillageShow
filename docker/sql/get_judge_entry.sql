select judge_code, cup_name, e.hash, ce.entry_description
from ( 
	select distinct j.judge_code, cy.year_id, cup.id cup_id, cup.name cup_name
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
) as d
left join vshow.cup_entry ce
  on ce.year_id = d.year_id
  and ce.cup_id = d.cup_id 
left join vshow.entry e
  on e.id = ce.entry_id

