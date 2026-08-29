import time
import random
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists, create_database

LOGGER = logging.getLogger(__name__)

class vShowDB():

    def __init__(self, scriptdir='~/', run_setup=False):
        server = os.getenv('DB_SERVER')
        port = os.getenv('DB_PORT')
        user = os.getenv('DB_USER')
        pwd = os.getenv('POSTGRES_PWD')
        db = os.getenv('DB_NAME')
        self._conn_str = f'postgresql://{user}:{pwd}@{server}:{port}/{db}'
        self._engine = create_engine(self._conn_str)
        self._scriptdir = scriptdir

        if not database_exists(self._conn_str):    
            create_database(self._conn_str)

        if run_setup:
            if not self.is_db_init():
                self.db_init()
            self.default_year()
    
    ### COMMON UTILS
    # Execute multiple calls, return data from the last call only
    def execute_sql(self, sqls, verbose=False):
        with self._engine.connect() as conn:
            results = []
            if not isinstance(sqls, list):
                sqls = (sqls,)
            for sqlt in sqls:
                if isinstance(sqlt, tuple):
                    if verbose:
                        LOGGER.info(f'Running sql: {sqlt[0]}')
                        LOGGER.info(f'Running params: {sqlt[1]}')
                    results.append(conn.execute(text(sqlt[0]),sqlt[1]))
                else:
                    if verbose:
                        LOGGER.info(f'Running sql: {sqlt}')
                    results.append(conn.execute(text(sqlt)))
            conn.commit()
            if len(sqls) == 1:  
                return results[0]
            return results

    ### TESTING UTILS (numbers table insert/pull)
    def add_new_row(self, n):
        # Insert a new number into the 'numbers' table.
        ts = int(round(time.time() * 1000))
        sql = ( "INSERT INTO numbers (number,timestamp) "
               f"VALUES ({n},{ts}) "
              )
        self.execute_sql(sql)

    def get_last_row(self):
        # Retrieve the last number inserted inside the 'numbers'
        sql = ( "SELECT number "
                "FROM numbers "
                "WHERE timestamp >= (SELECT max(timestamp) FROM numbers)"
                "LIMIT 1"
              )
        result = self.execute_sql(sql)
        for (row) in result:
            return row[0]

    # SET-UP THE DATABASE
    def is_db_init(self):
        sql = ( "SELECT EXISTS ( "
                "  SELECT FROM pg_tables "
                "  WHERE  schemaname = 'vshow' "
                "  AND    tablename  = 'current_year' "
                "); "
               )
        result = self.execute_sql(sql)
        db_exists = result.first()[0]
        LOGGER.info(f'DB Exists: {db_exists}')
        return db_exists

    def db_init(self):
        LOGGER.info('Running initdb script')
        with open(f'{self._scriptdir}/initdb.sql') as fh:
            sql = fh.read()
        self.execute_sql(sql)

    def default_year(self):
        LOGGER.info('Running default_year')
        with open(f'{self._scriptdir}/set_years.sql') as fh:
            sql = fh.read()
        self.execute_sql(sql)

    def get_year(self):
        sql = "select year from vshow.current_year cy join vshow.year y on cy.year_id = y.id"
        return list(self.execute_sql(sql))[0][0]

    def get_year_id(self):
        sql = "select year_id from vshow.current_year"
        year_id = list(self.execute_sql(sql))[0][0]
        return list(self.execute_sql(sql))[0][0]

    def set_year(self, year):
        LOGGER.info(f'Running set_year for {year}')
        sql = "update vshow.current_year cy set year_id = y.id from vshow.year y where year = :year"
        self.execute_sql((sql,{'year': year}))

    def get_years(self):
        sql = "select year from vshow.year"
        return list(x[0] for x in self.execute_sql(sql))

    def reset_year(self):
        LOGGER.info('Running clear year script')
        year_id = self.get_year_id()

        with open(f'{self._scriptdir}/reset_year.sql') as fh:
            sql = fh.read()
        self.execute_sql((sql,{"year_id": year_id}))

    # Bulk insert
    def import_classes(self, classes):
        LOGGER.info('Running class import')
        year_id = self.get_year_id()
        with open(f'{self._scriptdir}/import_class.sql') as fh:
            sql = fh.read()
        with open(f'{self._scriptdir}/import_class_cup.sql') as fh:
            sql_cup = fh.read()
        sqls = []
        for _class in classes:
            args = {
                    "year_id": year_id,
                    "class": _class['class'],
                    "name": _class['name'],
                    "is_child": (_class["kids"] in ('yY') ),
                    "description": _class['description'],
                    "judge": _class['judge']
                    }
            sqls.append((sql, args))
            for cup in _class['cups']:
                sqls.append((sql_cup, {"year_id": year_id, "class": _class['class'], "cup": cup} ))
        self.execute_sql(sqls)


    # Get / Upsert sections
    # CUPS
    def get_cups(self):
        sql = "select sname, name, description, points_type, cup_number from vshow.cup"
        return list(self.execute_sql(sql))

    def get_categories_for_cup(self, sname):
        with open(f'{self._scriptdir}/get_categories_for_cup.sql') as fh:
            sql = fh.read()
        results = list(self.execute_sql((sql,{"cup": sname})))
        return results

    def upsert_cup(self, sname, name, description, points_type, cup_number):
        params = {"sname": sname, "cup_number": cup_number, "name": name, "description": description, "points_type": points_type}
        sql = "select 1 from vshow.cup where sname = :sname"
        # cast cursor to list, then row 1, columne 1
        exists = list(self.execute_sql((sql, params)))
        if len(exists):
            sql = "update vshow.cup set name = :name, cup_number = :cup_number, description = :description, points_type = :points_type where sname = :sname"
        else:
            sql = "insert into vshow.cup(sname, name, cup_number, description, points_type) values (:sname, :name, :cup_number, :description, :points_type)"
        self.execute_sql((sql,params))

    # Note tht deletes will fail and raise exceptions to be caught in UI code
    def delete_cup(self, sname, ):
        params = {"sname": sname}
        sql = "delete from vshow.cup where sname = :sname"
        self.execute_sql((sql,params))

    # Judges
    def get_judges(self):
        sql = ( "select judge_code, name "
                "from vshow.judge j "
                "join vshow.current_year cy "
                " on cy.year_id = j.year_id "
                "left join vshow.villager v "
                " on v.id = j.villager_id " 
               )
        return list(self.execute_sql(sql))

    def get_categories_for_judge(self, code):
        with open(f'{self._scriptdir}/get_categories_for_judge.sql') as fh:
            sql = fh.read()
        results = list(self.execute_sql((sql,{"judge": code})))
        return results

    def get_entries_for_judges(self):
        with open(f'{self._scriptdir}/get_entries_for_judges.sql') as fh:
            sql = fh.read()
        results = list(self.execute_sql(sql))
        return results

    def get_judge_entry(self):
        with open(f'{self._scriptdir}/get_judge_entry.sql') as fh:
            sql = fh.read()
        results = list(self.execute_sql(sql))
        return results

    def update_judge(self, code, villager, items, cups):
        LOGGER.info(f'Saving {code}/{villager} - {items}')
        params = {"code": code, "villager": villager}

        sql = ( "update vshow.judge j "
               "set villager_id = (select id from vshow.villager where name = :villager) "
                "where j.year_id = (select year_id from vshow.current_year) "
               "and j.judge_code = :code "
               )
        self.execute_sql((sql,params))

        params = {"code": code}
        with open(f'{self._scriptdir}/update_class_medal.sql') as fh:
            sql = fh.read()
        for item in items:
            params['display_order'] = item[0]
            params['gold'] = item[1]
            params['silver'] = item[2]
            params['bronze'] = item[3]
            self.execute_sql((sql,params))

        params = {"code": code}
        with open(f'{self._scriptdir}/upsert_cup_entry.sql') as fh:
            sql = fh.read()
        for cup in cups:
            params['cup'] = cup[0]
            params['key'] = cup[1]
            params['entry_description'] = cup[2]
            self.execute_sql((sql,params))

    def clear_medal_codes(self):
        sql = ( "update vshow.class c "
                "set gold_entry_id = null, "
                "    silver_entry_id = null, "
                "    bronze_entry_id = null "
                "from vshow.current_year cy "
                "where c.year_id = cy.year_id "
               )
        self.execute_sql(sql)

    # Villagers
    def get_villagers(self):
        with open(f'{self._scriptdir}/get_villagers.sql') as fh:
            sql = fh.read()
        return list(self.execute_sql(sql))

    def delete_villager(self,name):
        params = {"name": name}
        sql = "delete from vshow.villager where name = :name"
        self.execute_sql((sql,params))

    def __get_existing_entries(self, name):
        """Get existing entries for a villager in current year, grouped by category."""
        sql = """
        select ca.name, ca.is_child
        from vshow.current_year cy
        join vshow.entrant e on e.year_id = cy.year_id
        join vshow.villager v on v.id = e.villager_id
        join vshow.entry ey on ey.entrant_id = e.id
        join vshow.class cl on cl.id = ey.class_id
        join vshow.category ca on ca.id = cl.category_id
        where v.name = :name
        order by ca.name, ca.is_child
        """
        params = {"name": name}
        results = list(self.execute_sql((sql, params)))
        return results

    def __parse_entry_name(self, entry_name):
        """Parse entry name into category name and is_child flag."""
        parts = entry_name.split(': ')
        if len(parts) < 2:
            return None, False
        catname = parts[1]
        is_child = False
        if catname.endswith(' (child)'):
            is_child = True
            catname = catname[:-8]
        return catname, is_child

    def __delete_entry_by_category(self, name, catname, is_child):
        """Delete one entry for a villager in a specific category."""
        sql = """
        delete from vshow.entry
        where id = (
            select ey.id
            from vshow.current_year cy
            join vshow.entrant e on e.year_id = cy.year_id
            join vshow.villager v on v.id = e.villager_id
            join vshow.entry ey on ey.entrant_id = e.id
            join vshow.class cl on cl.id = ey.class_id
            join vshow.category ca on ca.id = cl.category_id
            where v.name = :name
            and ca.name = :catname
            and ca.is_child = :is_child
            limit 1
        )
        """
        params = {"name": name, "catname": catname, "is_child": is_child}
        self.execute_sql((sql, params))

    def __assign_hash_to_unhashed_entries(self, name):
        """Assign hashes to any unhashed entries for this villager in current year."""
        sql = """
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
          left join (select e2.hash
            from vshow.entry e2
            join vshow.entrant et
              on et.id = e2.entrant_id
            join vshow.current_year cy
              on cy.year_id = et.year_id
          ) as e2
            on e2.hash = all_hashes.hash
          where e2.hash is null
        ) as unused
        join (
          select row_number() over (order by e3.id) row_num, e3.id
          from vshow.entry e3
          join vshow.entrant et
            on et.id = e3.entrant_id
          join vshow.villager v
            on v.id = et.villager_id
          join vshow.current_year cy
            on cy.year_id = et.year_id
          where v.name = :name and e3.hash is null
        ) as x
          on x.row_num = unused.row_num
        where e.id = x.id
        """
        params = {"name": name}
        self.execute_sql((sql, params))

    def upsert_entries(self, name, items):
        """Upsert entries: add new ones, delete removed ones, keep existing.
        Automatically assigns hashes to newly created entries."""
        LOGGER.info(f'Upserting entries for {name}: {items}')

        # Get existing entries from database
        existing = self.__get_existing_entries(name)

        # Parse on-page entries
        page_entries = []
        for item in items:
            catname, is_child = self.__parse_entry_name(item.name)
            if catname:
                page_entries.append((catname, is_child))

        # Count occurrences in page and database
        from collections import Counter
        page_counts = Counter(page_entries)
        existing_counts = Counter(existing)

        # Delete entries that are no longer on page
        for (catname, is_child), existing_count in existing_counts.items():
            page_count = page_counts.get((catname, is_child), 0)
            if existing_count > page_count:
                for _ in range(existing_count - page_count):
                    self.__delete_entry_by_category(name, catname, is_child)

        # Insert new entries that are on page but not in database
        with open(f'{self._scriptdir}/insert_entry.sql') as fh:
            insert_sql = fh.read()
        for (catname, is_child), page_count in page_counts.items():
            existing_count = existing_counts.get((catname, is_child), 0)
            if page_count > existing_count:
                for _ in range(page_count - existing_count):
                    params = {"name": name, "catname": catname, "is_child": is_child}
                    self.execute_sql((insert_sql, params))

        # Automatically assign hashes to any newly created unhashed entries
        self.__assign_hash_to_unhashed_entries(name)

    def upsert_villager(self, name, age, items):
        LOGGER.info(f'Saving {name}/{age} - {items}')
        params = {"name": name, "age": age, "year_id": None}
        if age:
            with open(f'{self._scriptdir}/get_year_id_for_age.sql') as fh:
                sql = fh.read()
            params["year_id"] = list(self.execute_sql((sql, params)))[0][0]

        sql = "select 1 from vshow.villager where name = :name"
        exists = list(self.execute_sql((sql, params)))
        if len(exists):
            sql = "update vshow.villager set name = :name, year_id_of_majority = :year_id where name = :name"
        else:
            sql = "insert into vshow.villager(name, year_id_of_majority) values (:name, :year_id)"
        self.execute_sql((sql,params))

        # Handle entries with upsert logic instead of delete-and-recreate
        if len(items) == 0:
            # Delete all entries for this villager in current year
            params["del_entrant"] = True
            with open(f'{self._scriptdir}/delete_entries.sql') as fh:
                sql = fh.read()
            self.execute_sql((sql, params))
            return

        # Create entrant if needed
        with open(f'{self._scriptdir}/upsert_entrant.sql') as fh:
            sql = fh.read()
        self.execute_sql((sql, params))

        # Upsert entries (add/delete as needed, keep existing)
        self.upsert_entries(name, items)

    # Categories
    def get_categories(self):
        with open(f'{self._scriptdir}/get_categories.sql') as fh:
            sql = fh.read()
        return list(self.execute_sql(sql))

    # Entries
    def get_entries(self):
        with open(f'{self._scriptdir}/get_entries.sql') as fh:
            sql = fh.read()
        return list(self.execute_sql(sql))

    def adjust_entry(self, ref, num):
        with open(f'{self._scriptdir}/adjust_entry.sql') as fh:
            sql = fh.read()
        self.execute_sql((sql, {'hash': ref, 'display_order': num}))

    # Bulk Export Data
    def get_cup_winners_pts(self):
        with open(f'{self._scriptdir}/get_cup_winners_pts.sql') as fh:
            sql = fh.read()
        return list(self.execute_sql(sql))

    def get_cup_winners_best(self):
        with open(f'{self._scriptdir}/get_cup_winners_best.sql') as fh:
            sql = fh.read()
        return list(self.execute_sql(sql))

    def get_class_winners(self):
        with open(f'{self._scriptdir}/get_class_winners.sql') as fh:
            sql = fh.read()
        return list(self.execute_sql(sql))

    def get_judge_pages_points(self):
        with open(f'{self._scriptdir}/get_judge_pages_points.sql') as fh:
            sql = fh.read()
        return list(self.execute_sql(sql))

    def get_judge_pages_entry(self):
        with open(f'{self._scriptdir}/get_judge_pages_entry.sql') as fh:
            sql = fh.read()
        return list(self.execute_sql(sql))

    def get_entry_hashes(self):
        with open(f'{self._scriptdir}/get_entry_hashes.sql') as fh:
            sql = fh.read()
        return list(self.execute_sql(sql))

    def get_category_counts(self):
        with open(f'{self._scriptdir}/get_category_counts.sql') as fh:
            sql = fh.read()
        return list(self.execute_sql(sql))

    def get_villagers_with_entries(self):
        sql = """
        select distinct v.name
        from vshow.current_year cy
        join vshow.entrant e on e.year_id = cy.year_id
        join vshow.villager v on v.id = e.villager_id
        join vshow.entry ey on ey.entrant_id = e.id
        order by v.name
        """
        return [row[0] for row in self.execute_sql(sql)]

