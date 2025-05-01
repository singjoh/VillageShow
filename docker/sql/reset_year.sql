
delete from vshow.cup_class
where class_id 
in (select id from vshow.class where year_id = :year_id);

delete from vshow.cup_entry
where year_id = :year_id;

update vshow.class
set gold_entry_id = null,
    silver_entry_id = null,
    bronze_entry_id = null
where year_id = :year_id;

delete from vshow.entry
where entrant_id
in (select id from vshow.entrant where year_id = :year_id);

delete from vshow.class where year_id = :year_id;

delete from vshow.judge
where year_id = :year_id;

delete from vshow.entrant where year_id = :year_id;
