CREATE SCHEMA IF NOT EXISTS vshow;

CREATE TABLE IF NOT EXISTS vshow.year (
	id SERIAL PRIMARY KEY,
	year INT NOT NULL,
	show_date DATE NULL,
	CONSTRAINT uk_year UNIQUE(year)
	);

CREATE TABLE IF NOT EXISTS vshow.current_year (
	year_id INT NOT NULL REFERENCES vshow.year
	);

CREATE TABLE IF NOT EXISTS vshow.villager (
	id SERIAL PRIMARY KEY,
	name VARCHAR(128),
	year_id_of_majority INT NULL REFERENCES vshow.year,
	CONSTRAINT uk_name UNIQUE(name)
	);

CREATE TABLE IF NOT EXISTS vshow.judge (
	id SERIAL PRIMARY KEY,
	year_id INT NOT NULL REFERENCES vshow.year,
	judge_code VARCHAR(16) NOT NULL,
	villager_id INT NULL REFERENCES vshow.villager,
	CONSTRAINT uk_judge UNIQUE(year_id, judge_code)
	);

CREATE TABLE IF NOT EXISTS vshow.entrant (
	id SERIAL PRIMARY KEY,
	villager_id INT NOT NULL REFERENCES vshow.villager,
	year_id INT NOT NULL REFERENCES vshow.year,
	hash char(2),
	CONSTRAINT uk_entrant UNIQUE(villager_id, year_id)
	);

CREATE TABLE IF NOT EXISTS vshow.category (
	id SERIAL PRIMARY KEY,
	name VARCHAR(128) NOT NULL,
	is_child bool NOT NULL,
	description VARCHAR(512) NULL,
	CONSTRAINT uk_name_child UNIQUE(name, is_child)
	);

CREATE TABLE IF NOT EXISTS vshow.class (
	id SERIAL PRIMARY KEY,
	display_order INT NOT NULL,
	year_id INT NOT NULL REFERENCES vshow.year,
	category_id INT NOT NULL REFERENCES vshow.category,
	judge_id INT NOT NULL REFERENCES vshow.judge,
	gold_entry_id INT NULL,
	silver_entry_id INT NULL,
	bronze_entry_id INT NULL,
	CONSTRAINT uk_class UNIQUE(category_id, year_id),
	CONSTRAINT uk_display_order_year_id UNIQUE(display_order, year_id)
	);

CREATE TABLE IF NOT EXISTS vshow.entry (
	id SERIAL PRIMARY KEY,
	entrant_id INT NOT NULL REFERENCES vshow.entrant,
	class_id INT NOT NULL REFERENCES vshow.class,
	hash char(2)
	);
	
ALTER TABLE vshow.class DROP CONSTRAINT IF EXISTS fk_gold_entry_id; 
ALTER TABLE vshow.class DROP CONSTRAINT IF EXISTS fk_silver_entry_id; 
ALTER TABLE vshow.class DROP CONSTRAINT IF EXISTS fk_bronze_entry_id; 

ALTER TABLE vshow.class
    ADD CONSTRAINT fk_gold_entry_id
    FOREIGN KEY (gold_entry_id) REFERENCES vshow.entry(id),	
    ADD CONSTRAINT fk_silver_entry_id
    FOREIGN KEY (silver_entry_id) REFERENCES vshow.entry(id),	
    ADD CONSTRAINT fk_bronze_entry_id
    FOREIGN KEY (bronze_entry_id) REFERENCES vshow.entry(id);
	
CREATE TABLE IF NOT EXISTS vshow.cup (
	id SERIAL PRIMARY KEY,
	name VARCHAR(128) NOT NULL,
	sname varchar(16) NOT NULL,
	description VARCHAR(512) NULL,
	points_type bool default true,
	CONSTRAINT uk_sname UNIQUE(sname)
	);

CREATE TABLE IF NOT EXISTS vshow.cup_entry (
	id SERIAL PRIMARY KEY,
	cup_id INT NOT NULL REFERENCES vshow.cup,
	year_id INT NOT NULL REFERENCES vshow.year,
	entry_id INT NOT NULL REFERENCES vshow.entry,
	CONSTRAINT uk_cup_entry UNIQUE(cup_id, year_id)
	);
	
CREATE TABLE IF NOT EXISTS vshow.cup_class (
	id SERIAL PRIMARY KEY,
	cup_id INT NOT NULL REFERENCES vshow.cup,
	class_id INT NOT NULL REFERENCES vshow.class,
	CONSTRAINT uk_cup_class UNIQUE(cup_id, class_id)
	);
	
