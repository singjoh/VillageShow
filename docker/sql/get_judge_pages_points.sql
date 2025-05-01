select j.judge_code, v.name, c.display_order, ca.name,
  (select count(*) from vshow.entry e where e.class_id = c.id) c
from vshow.current_year cy
join vshow.judge j
  on j.year_id = cy.year_id
left join vshow.villager v
  on v.id = j.villager_id
join vshow.class c
  on c.judge_id = j.id
join vshow.category ca
  on ca.id = c.category_id
 order by 1, 3
