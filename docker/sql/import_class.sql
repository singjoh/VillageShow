
update vshow.category
  set description = :description
where name = :name
  and is_child = :is_child;

insert into vshow.category
  (name, is_child, description)
select :name, :is_child, :description
where not exists (select 1 from vshow.category where name = :name and is_child = :is_child);

insert into vshow.judge
  (year_id, judge_code)
select :year_id, :judge
where not exists (select 1 from vshow.judge where year_id = :year_id and judge_code = :judge);

update vshow.class
set category_id = ca.id,
    judge_id = (select id from vshow.judge where year_id = :year_id and judge_code = :judge)
from vshow.category as ca
where ca.name = :name
  and ca.is_child = :is_child
  and display_order = :class
  and year_id = :year_id;

insert into vshow.class
  (year_id, display_order, category_id, judge_id)
select :year_id, :class, ca.id, 
       (select id from vshow.judge where year_id = :year_id and judge_code = :judge)
from vshow.category as ca
where ca.name = :name
  and ca.is_child = :is_child
  and not exists (select 1 from vshow.class where display_order = :class and year_id = :year_id);


