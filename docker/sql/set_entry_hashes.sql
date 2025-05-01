update vshow.entry e
set hash = unused.hash
from (
  select row_number() over (order by all_hashes.c) row_num, all_hashes.hash
  from (
    select c1.i * 10 + c2.i c, substring(y.c from c1.i for 1) || substring(y.c from c2.i for 1) as hash
    from ( select 'aAbBcdDeEfgGhHjklmnoPqQrRstTuvwxy2346789' as c ) as y
    cross join (select i from generate_series(1,40) as t(i)) as c1
    cross join (select i from generate_series(1,40) as t(i)) as c2
  ) as all_hashes
  left join vshow.entry e
    on e.hash = all_hashes.hash
  where e.hash is null
) as unused
join (
  select row_number() over (order by id) row_num, id
  from vshow.entry
  where hash is null
) as x
  on x.row_num = unused.row_num
where e.id = x.id
