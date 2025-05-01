update vshow.class c
set gold_entry_id = g_id,
    silver_entry_id = s_id,
    bronze_entry_id = b_id
from (
  select c.id, g.id g_id, s.id s_id, b.id b_id
  from vshow.current_year cy
  join vshow.class c
    on c.year_id = cy.year_id
  join vshow.judge j
    on j.id = c.judge_id
  left join vshow.entry g
    on g.class_id = c.id
    and g.hash = :gold
  left join vshow.entry s
    on s.class_id = c.id
    and s.hash = :silver
  left join vshow.entry b
    on b.class_id = c.id
    and b.hash = :bronze
  where j.judge_code = :code
    and c.display_order = :display_order ) as x
where x.id = c.id
