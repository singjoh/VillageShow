select judge_code, display_order, ca.name, ca.is_child, e.hash
from vshow.current_year y
join vshow.judge j
  on j.year_id = y.year_id
join vshow.class c
  on c.judge_id = j.id
join vshow.category ca
  on ca.id = c.category_id
join vshow.entry e
  on e.class_id = c.id
