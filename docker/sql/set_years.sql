insert into vshow.year(year)
select ny.year
from ( 
  select 1950 + i as year
  from generate_series(0,150) as t(i)
	) as ny
left join vshow.year y
  on y.year = ny.year
where y.year is null;

update vshow.current_year 
set year_id = y.id
from vshow.year y
where y.year = date_part('year', now());

insert into vshow.current_year (year_id)
select y.id
from vshow.year y
where y.year = date_part('year', now())
and not exists (select 1 from vshow.current_year);

