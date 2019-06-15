#!/usr/bin/env python3

# Extended from bwDB - CRUD library for sqlite 3 by Bill Weinman [http://bw.org/]

import sqlite3
import os

__version__ = '1.0.1'


class ArkDBSQLite:
    kQUERY_PARAM_PLACE_HOLDER = '?'

    def __init__(self, **kwargs):
        """
            db = ArkDBSQLite ( [ table = ''] [, filename = ''] )
            constructor method
        """
        db_config_file = kwargs.get('db_config_file', '')
        if db_config_file:
            with open(db_config_file) as config:
                config.readline().rstrip()  # skip host
                config.readline().rstrip()  # skip user
                config.readline().rstrip()  # skip password
                db_filename = config.readline().rstrip() # use schema name as filename
        else:
            db_filename = kwargs.get('filename')

        self.filepath_ = kwargs.get('db_filepath', '.')
        # see filename setter below
        self.filename_ = f'{self.filepath_}/{db_filename}'

        self.table_ = ''
        self.err_ = None

    # filename property
    @property
    def filename_(self):
        return self.dbfilename_

    @filename_.setter
    def filename_(self, fn):
        self.dbfilename_ = f'{fn}.sqlite3'
        self.con_ = sqlite3.connect(self.dbfilename_)
        self.con_.row_factory = sqlite3.Row

    @filename_.deleter
    def filename_(self):
        self.close()

    def remove_db_from_disk(self):
        os.remove(f'{self.dbfilename_}')

    def close(self):
        self.con_.close()
        del self.dbfilename_

    def set_table(self, table_name):
        self.table_ = table_name

    def get_table(self):
        if self.table_ == '' or self.table_ is None:
            raise ValueError('no table selected, set_table first')
        return self.table_

    def set_auto_inc(self, inc):
        """
        UPDATE
        SQLITE_SEQUENCE
        SET
        seq = < n > WHERE
        name = '<table>'
        """
        pass

    def get_auto_inc(self):
        pass

    def run_sql_nocommit(self, sql, params=()):
        """
            run_sql_nocommit( sql[, params] )
            method for non-select queries *without commit*
                sql is string containing SQL
                params is list containing parameters
            return the cursor of the query
        """
        # TODO: Add crash resilient code to recover from a failed query
        try:
            return self.con_.execute(sql, params)
        except sqlite3.Error as err:
            self.err_ = err
            print('### DB error ###')
            print(f'Error msg: {format(err)}')
            print('- - - - - - - -')
            print(f'SQL: {sql}')
            if params:
                print('- - - - with params - - - -')
                print(params)
            print('### END of DB error report ###')

    def commit(self):
        self.con_.commit()

    def get_error(self):
        return self.err_

    def run_sql(self, sql, params=()):
        """
            db.run_sql( sql[, params] )
            method for non-select queries
                sql is string containing SQL
                params is list containing parameters
            returns nothing
        """
        self.run_sql_nocommit(sql, params)
        self.commit()

    def run_query_get_all_row(self, query, params=()):
        cur = self.run_sql_nocommit(query, params)
        return cur.fetchall()

    def run_query(self, query, params=()):
        """
            db.run_query( query[, params] )
            generator method for queries
                query is string containing SQL
                params is list containing parameters
            returns a generator with one row per iteration
            each row is a Row factory
        """
        cur = self.run_sql_nocommit(query, params)
        for row in cur:
            yield row

    def get_query_row(self, query, params=()):
        """
            db.get_query_row( query[, params] )
            query for a single row
                query is string containing SQL
                params is list containing parameters
            returns a single row as a Row factory
        """
        cur = self.run_sql_nocommit(query, params)
        return cur.fetchone()

    def get_query_value(self, val_name, query, params=()):
        """
            db.get_query_value( query[, params] )
            query for a single value
                val_name is key to retrieve value
                query is string containing SQL
                params is list containing parameters
            returns a single value
        """
        row = self.get_query_row(query, params)
        if row is None or val_name not in row.keys():
            return None
        return row[val_name]

    def insert_nocommit(self, rec):
        """
            db.insert(rec)
            insert a single record into the table
                rec is a dict with key/value pairs corresponding to table schema
            omit id column to let SQLite generate it
        """
        klist = sorted(rec.keys())
        values = [rec[v] for v in klist]  # a list of values ordered by key
        query = 'INSERT INTO {} ({}) VALUES ({})'.format(
            self.get_table(),
            ', '.join(klist),
            ', '.join(self.kQUERY_PARAM_PLACE_HOLDER * len(values))
        )
        cur = self.run_sql_nocommit(query, values)
        return cur.lastrowid

    def insert(self, rec):
        lastrowid = self.insert_nocommit(rec)
        self.commit()
        return lastrowid

    def update_nocommit(self, recid, recid_label, rec):
        """
            db.update(recid, recid_label, rec)
            update a row in the table
                recid is the value of the id column for the row to be updated
                recid_label is the label of the id column for the row to be updated
                rec is a dict with key/value pairs corresponding to table schema
        """
        klist = sorted(rec.keys())
        values = [rec[v] for v in klist]  # a list of values ordered by key

        for i, k in enumerate(klist):  # don't udpate id
            if k == recid_label:
                del klist[i]
                del values[i]

        query = 'UPDATE {} SET {} WHERE {} = {}'.format(
            self.get_table(),
            ',  '.join(map(lambda s: '{} = ?'.format(s), klist)),
            recid_label,
            self.kQUERY_PARAM_PLACE_HOLDER
        )
        self.run_sql_nocommit(query, values + [recid])

    def update(self, recid, recid_label, rec):
        self.update_nocommit(recid, recid_label, rec)
        self.commit()

    def delete_nocommit(self, recid, recid_label):
        """
            db.delete(recid, recid_label)
            delete a row from the table, by a pair of recid and recid_label
        """
        query = f'DELETE FROM {self.get_table()} WHERE {recid_label} = {self.kQUERY_PARAM_PLACE_HOLDER}'
        self.run_sql_nocommit(query, [recid])

    def delete(self, recid, recid_label):
        self.delete_nocommit(recid, recid_label)
        self.commit()

    def is_table_exist(self, table):
        res = self.run_query_get_all_row(f"SELECT name FROM sqlite_master WHERE type = 'table' AND name = '{table}'")
        return len(res) != 0

    def countrecs(self):
        """
            db.countrecs()
            count the records in the table
            returns a single integer value
        """
        query = f'SELECT COUNT(*) AS CNT FROM {self.get_table()}'
        return self.get_query_value('CNT', query)

    def create_table(self, table_desc_dict, force=False):
        if self.is_table_exist(table_desc_dict['table_name']):
            if not force:
                return False
            self.run_sql(f"DROP TABLE {table_desc_dict['table_name']}")
        columns_desc_list = [f"`{item['name']}` {item['type']} {item['property']}"
                             for item in table_desc_dict['table_columns']]
        query = f"CREATE TABLE `{table_desc_dict['table_name']}` ("
        query += ', '.join(columns_desc_list)
        query += ', PRIMARY KEY ('
        query += ', '.join([f'`{col}`' for col in table_desc_dict['table_pks']])
        query += '))'
        self.run_sql(query)
        return True
