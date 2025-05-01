select ym.id
from vshow.year ym
cross join vshow.current_year cy
join vshow.year y
 on y.id = cy.year_id
where y.year + 18 - ym.year = :age
