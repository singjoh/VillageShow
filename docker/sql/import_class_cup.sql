insert into  vshow.cup_class (cup_id, class_id)
select (select id from vshow.cup where sname = :cup),
       (select id from vshow.class where display_order = :class and year_id = :year_id)
where not exists (
	select 1 
	from vshow.cup_class cc
	join vshow.cup 
	  on cup.id = cc.cup_id
	  and cup.sname = :cup
	join vshow.class c
	  on c.id = cc.class_id
	  and c.year_id = :year_id
	  and c.display_order = :class
)
