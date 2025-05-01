select name,
 case when ym.year is not null then y.year + 18 - ym.year else NULL end age
from vshow.villager v
left join vshow.year ym
 on ym.id = v.year_id_of_majority
cross join vshow.current_year cy
join vshow.year y
 on y.id = cy.year_id
