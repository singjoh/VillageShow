select j.judge_code, v.name, cup.name, c.display_order, ca.name
from vshow.current_year cy
join vshow.judge j
  on j.year_id = cy.year_id
left join vshow.villager v
  on v.id = j.villager_id
join vshow.class c
  on c.judge_id = j.id
join vshow.category ca
  on ca.id = c.category_id
join vshow.cup_class cc
  on cc.class_id = c.id
join vshow.cup cup
  on cup.id = cc.cup_id
 and cup.points_type = false
