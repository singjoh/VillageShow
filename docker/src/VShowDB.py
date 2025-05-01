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

        # delete entries
        params["del_entrant"] = (len(items) == 0)
        with open(f'{self._scriptdir}/delete_entries.sql') as fh:
            sql = fh.read()
        self.execute_sql((sql,params))

        if len(items) == 0:
            return

        # create entrant
        with open(f'{self._scriptdir}/upsert_entrant.sql') as fh:
            sql = fh.read()
        self.execute_sql((sql,params))

        with open(f'{self._scriptdir}/insert_entry.sql') as fh:
            sql = fh.read()
        for item in items:
            catname = item.name.split(': ')[1]
            is_child = False
            if catname[-8:] == ' (child)':
                is_child = True
                catname = catname[:-8]
            params = {"name": name, "catname": catname, "is_child": is_child}
            self.execute_sql((sql,params))

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

    def set_entry_hashes(self):
        with open(f'{self._scriptdir}/set_entry_hashes.sql') as fh:
            sql = fh.read()
        self.execute_sql(sql)

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

