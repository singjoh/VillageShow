update vshow.entry e
set class_id = x.class_id
from (
	select y.id entry_id, c.id class_id
	from vshow.current_year cy
	join vshow.entrant e
	  on e.year_id = cy.year_id
	join vshow.entry y
	  on y.entrant_id = e.id
	join vshow.class c
	  on c.year_id = cy.year_id
	where y.hash = :hash
	 and c.display_order = :display_order
) x
where e.id = x.entry_id
