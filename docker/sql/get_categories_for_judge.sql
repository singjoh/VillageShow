select display_order, ca.name, ca.is_child, g.hash gold, s.hash silver, b.hash bronze
from vshow.judge j
join vshow.current_year cy
  on cy.year_id = j.year_id
join vshow.class c
  on c.judge_id = j.id
join vshow.category ca
  on ca.id = c.category_id
left join vshow.entry g
  on g.id = c.gold_entry_id
left join vshow.entry s
  on s.id = c.silver_entry_id
left join vshow.entry b
  on b.id = c.bronze_entry_id
where judge_code = :judge
