#!/usr/bin/env python3

# Developed based on bwDB - CRUD library for sqlite 3 by Bill Weinman [http://bw.org/]

import mysql.connector

__version__ = '1.0.0'


class ArkDBMySQL:
    kQUERY_PARAM_PLACE_HOLDER = '%s'

    def __init__(self, **kwargs):
        """
            db = ArkDBMySQL( [ table = ''] [, db_config_file = ''] )
            constructor method
        """
        db_config_file = kwargs.get('db_config_file', '')
        if db_config_file:
            with open(db_config_file) as config:
                self.host_ = config.readline().rstrip()
                self.user_ = config.readline().rstrip()
                self.password_ = config.readline().rstrip()
                self.schema_ = config.readline().rstrip()
                self.port_ = int(config.readline().rstrip())
        else:
            self.host_ = kwargs.get('host')
            self.user_ = kwargs.get('user')
            self.password_ = kwargs.get('password')
            self.schema_ = kwargs.get('schema')
            self.port_ = kwargs.get('port', 3306)   # default MySQL port is 3306

        self.table_ = ''
        self.con_ = mysql.connector.connect(
            user=self.user_,
            password=self.password_,
            host=self.host_,
            database=self.schema_,
        )
        self.cur_ = self.con_.cursor(dictionary=True, buffered=True)
        self.err_ = None

    def __del__(self):
        self.con_.close()

    def dup_self(self):
        duplicated_db = ArkDBMySQL(
            host=self.host_,
            user=self.user_,
            password=self.password_,
            schema=self.schema_,
            port=self.port_,
        )
        duplicated_db.set_table(self.get_table())
        return duplicated_db

    def set_table(self, table_name):
        self.table_ = table_name

    def get_table(self):
        if self.table_ == '' or self.table_ is None:
            raise ValueError('no table selected, set_table first')
        return self.table_

    def set_auto_inc(self, inc):
        cur_inc = self.get_auto_inc()
        if cur_inc >= inc:
            print(f'Error: Current value {cur_inc} is larger than {inc}')
            return False
        self.run_sql(f'ALTER TABLE {self.get_table()} AUTO_INCREMENT={self.kQUERY_PARAM_PLACE_HOLDER}', [inc])
        return True

    def get_auto_inc(self):
        return self.get_query_value('AUTO_INCREMENT',
                                    f"SELECT AUTO_INCREMENT FROM INFORMATION_SCHEMA.TABLES "
                                    f"WHERE TABLE_SCHEMA='{self.schema_}' AND TABLE_NAME='{self.get_table()}'")

    def run_sql_nocommit(self, sql, params=()):
        """
            run_sql_nocommit( sql[, params] )
            method for non-select queries *without commit*
                sql is string containing SQL
                params is list containing parameters
            returns nothing
        """
        # TODO: Add crash resilient code to recover from a failed query
        self.err_ = None
        try:
            self.cur_.execute(sql, params)
        except mysql.connector.Error as err:
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
        self.run_sql_nocommit(query, params)
        return self.cur_.fetchall()

    def run_query(self, query, params=()):
        """
            db.run_query( query[, params] )
            generator method for queries
                query is string containing SQL
                params is list containing parameters
            returns a generator with one row per iteration
            each row is a Row factory
        """
        self.run_sql_nocommit(query, params)
        row = self.cur_.fetchone()
        while row is not None:
            yield row
            row = self.cur_.fetchone()

    def get_query_row(self, query, params=()):
        """
            db.get_query_row( query[, params] )
            query for a single row
                query is string containing SQL
                params is list containing parameters
            returns a single row as a Row factory
        """
        self.run_sql_nocommit(query, params)
        return self.cur_.fetchone()

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
        if row is None or val_name not in row:
            return None
        return row[val_name]

    def insert_nocommit(self, rec):
        """
            db.insert(rec)
            insert a single record into the table
                rec is a dict with key/value pairs corresponding to table schema
        """
        klist = sorted(rec.keys())
        values = [rec[v] for v in klist]
        query = 'INSERT INTO {} ({}) VALUES ({})'.format(
            self.get_table(),
            ', '.join(klist),
            ', '.join([self.kQUERY_PARAM_PLACE_HOLDER] * len(values))
        )
        self.run_sql_nocommit(query, values)
        return self.cur_.lastrowid

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
        values = [rec[v] for v in klist]

        # do not update id
        for i, k in enumerate(klist):
            if k == recid_label:
                del klist[i]
                del values[i]

        query = 'UPDATE {} SET {} WHERE {} = {}'.format(
            self.get_table(),
            ', '.join(map(lambda s: '{} = %s'.format(s), klist)),
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

    def optimize(self, table=None):
        if not table:
            table = self.get_table()
        self.run_sql(f'optimize table {table}')

    def is_table_exist(self, table):
        res = self.run_query_get_all_row(f"SHOW TABLES LIKE '{table}'")
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
        query += 'ENGINE = InnoDB'
        self.run_sql(query)
        return True

    def add_index(self, item, table=None):
        if not table:
            table = self.get_table()
        indexes = self.run_query_get_all_row(f'SHOW INDEX FROM {table}')
        for row in indexes:
            if row['Column_name'] == item:
                print(f'Index {item} already exists in table {table}')
                return False
        self.run_sql(f'ALTER TABLE {table} ADD INDEX ({item})')
        print(f'Added index {item} for table {table}')
        return True

    def remove_index(self, item, table=None):
        if not table:
            table = self.get_table()
        indexes = self.run_query_get_all_row(f'SHOW INDEX FROM {table}')
        for row in indexes:
            if row['Column_name'] == item:
                break
        else:
            print(f'Index {item} does not exist in table {table}')
            return False
        self.run_sql(f'DROP INDEX `{item}` ON {table}')
        print(f'Removed index {item} for table {table}')
        return True

    def get_table_disk_size(self, table=None):
        if not table:
            table = self.get_table()
        data_size = self.get_query_value('size_in_mb', f'SELECT table_name AS `Table`, round(((data_length) / 1024 / 1024), 2) AS `size_in_mb` FROM information_schema.TABLES WHERE table_schema = "{self.schema_}" AND table_name = "{table}"')
        index_size = self.get_query_value('size_in_mb', f'SELECT table_name AS `Table`, round(((index_length) / 1024 / 1024), 2) AS `size_in_mb` FROM information_schema.TABLES WHERE table_schema = "{self.schema_}" AND table_name = "{table}"')
        return data_size, index_size
