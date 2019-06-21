__version__ = 1.22

import os
import sys
import sqlalchemy
from random import randrange
import pandas as pd
import core.settings as settings
from time import sleep
from sqlalchemy import *
from datetime import datetime
from sqlalchemy.orm import mapper
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

db_type_allias = {'ms': 'MsSql', 'ora': 'Oracle', 'pst': 'Postgre'}


class Database:
    db = None
    server = None
    db_type = None
    database = None
    engine = None
    nls_lang = 'CROATIAN_CROATIA.UTF8'
    primary_key = 'id'  # default primary key is id
    archive_date = "dat_pro"  # default archive column name is dat_pro

    def __init__(self, config_file, conn_type=1):
        """connection type: 1 for trusted, 2 for untrusted and requires username and password in settings"""
        # import setings from config file
        db_default = settings.DbConfig(config_file)

        self.conn_type = conn_type
        # cache if changes have been made to connection variables
        variables = [i for i in dir(self) if not i.__contains__('__') and type(self.__getattribute__(i)) is str]

        check_db_allias = db_type_allias.get(self.db_type.lower())
        if check_db_allias is not None:
            self.db_type = check_db_allias

        if self.db_type == 'Oracle' and getattr(self, 'nls_lang') is not None:
            os.environ['NLS_LANG'] = getattr(self, 'nls_lang')

        # construct final database settings and update attribute values
        # db_module = getattr(sys.modules[__name__], self.db_type)
        db_module = getattr(settings, self.db_type)
        [setattr(db_module, variable, self.__getattribute__(variable)) for variable in variables]
        self.db = db_module(db_default)
        self.primary_key = self.primary_key
        self.connect()

    def connect(self):
        while True:
            try:
                conn_types = {1: self.db.conn_trusted, 2: self.db.conn_untrusted}
                self.engine = create_engine(conn_types.get(self.conn_type), echo=False)
                break
            except:
                sleep(60)

    def raw_connect(self):
        x = 0
        while True:
            x += 1
            try:
                return self.engine.raw_connection()
            except Exception as e:
                print(str(e))
                if x > 2:
                    break
                self.connect()
                sleep(x * 2)

    @staticmethod
    def lower(table):
        for child in table.get_children():
            child.name = child.name.lower()
            child.key = child.key.lower()

    def insert(self, tablename, data, schema=None, freeze=False):
        """freeze: When True it will leave Column names as they are if False they will be all lower"""
        for tires in range(5):
            try:
                def convert_nan(v):
                    if pd.isnull(v) or pd.isna(v):
                        v = None
                    return v

                engine = self.engine
                if self.db_type == 'Oracle':
                    tablename = tablename.upper()

                metadata = MetaData(bind=engine)
                table = Table(tablename, metadata, autoload=True, quote=True, schema=schema)
                if freeze is True:
                    insert_rows = [{k: convert_nan(v) for k, v in check_ir.items()} for check_ir in data]
                else:
                    insert_rows = [{k.lower(): convert_nan(v) for k, v in check_ir.items()} for check_ir in data]
                with engine.begin() as connection:
                    for insert_row in insert_rows:
                        connection.execute(table.insert().values(**insert_row))
                break
            # exception handles errors like connecting to database or if connection is closed
            except (sqlalchemy.exc.OperationalError, sqlalchemy.exc.ResourceClosedError) as e:
                print("error insert", e)
                print("+ reconecting: sqlalchemy connection Error")
                self.connect()

    def callproc(self, procs, response=False, one=False, keyval=False):
        """
        :param list procs:
        :param bool response:
        Description:
            proc: list of procedure we want to execute must.
                if list item is string then call's procedure without args
                if list itrm is tuple then 1 is the name and second list of args
            response: True if we expect from database procedure to return some results
            else it will happen error Exception
        """
        results = []
        for proc in procs:
            # print(proc)

            proc_name, args = None, []

            if type(proc) is str:
                proc_name = proc

            if type(proc) in (list, tuple):
                proc_name, args = proc

            connection = self.raw_connect()
            result = 0
            try:
                cursor = connection.cursor()
                # print("args", args)
                if keyval is False:
                    cursor.callproc(proc_name, args)
                else:
                    cursor.callproc(proc_name, keywordParameters=args)
                if response is True:
                    cursor.nextset()
                    if one is True:
                        result = cursor.fetchone()
                    else:
                        result = cursor.fetchall()
                cursor.close()
                connection.commit()
            finally:
                connection.close()
            results.append(result)
        return results

    def delete(self, tablename, filters=None, schema=None):
        """Deletes records that are not needed anymore.
        Warning: filter value must be same datatype as in table or
         it will delete entire content of table"""

        class DbTable(object):
            pass

        engine = self.engine
        metadata = MetaData(engine)
        table = Table(tablename, metadata, autoload=True, schema=schema)
        mapper(DbTable, table)

        session = sessionmaker(bind=engine)()

        if filters is None:
            session.query(DbTable).filter(getattr(DbTable, self.archive_date).isnot(None)).delete()
            session.commit()
        else:
            filter_combine = []
            for k, v in filters.items():
                if type(v) is bool:
                    if v is True:
                        filter_combine.append(getattr(DbTable, k).isnot(None))
                if type(v) is str:
                    filter_combine.append(getattr(DbTable, k) == v)
            session.query(DbTable).filter(*filter_combine).delete()
            session.commit()

    def select(self, tablename, columns=None, filters=None, sql=None, schema=None, index=False, view=True):
        """
        :param str tablename:
        :param list columns:
        :param dict filters:
        :param str sql:
        :param str schema:
        :param bool index:
        :param bool view:
        Description:
            usage: selects data from specified table in database
            filter: is where clause with and's
            columns: final columns to pick
            sql: return results from str query
            schema: if schema is needed to be specified
            index: if index True select will return index data and records
            view: if view is True then mapper needs column name 'id' so it can
                declare it as prmary key - this is only applicable for mssql since
                you cant add primary key in mssql views
        """

        class DbTable(object):
            pass

        for tries in range(5):
            try:
                engine = self.engine
                if sql is None:
                    metadata = MetaData(engine)

                    # if pk is True:
                    table = Table(tablename, metadata, autoload=True, schema=schema)

                    self.lower(table)
                    if view is True:
                        try:
                            mapper(DbTable, table, primary_key=[table.c.ID])
                        except:
                            mapper(DbTable, table, primary_key=[table.c.id])

                    else:
                        mapper(DbTable, table)

                    session = sessionmaker(bind=engine)()

                    if filters is not None:
                        filters = {k.lower(): v for k, v in filters.items()}
                        results = session.query(DbTable).filter_by(**filters).statement
                    else:
                        results = session.query(DbTable).statement
                    db_df = pd.read_sql(results, engine, index_col=self.primary_key)
                else:
                    results = sql
                    db_df = pd.read_sql(results, engine)

                db_df.columns = map(str.lower, db_df.columns)

                if columns is not None:
                    columns = [k.lower() for k in columns]
                    db_df = db_df[columns]

                db_df.drop_duplicates(inplace=True)
                if index is False:
                    final_select = db_df.to_dict('records')
                else:
                    final_select = db_df.to_dict()
                return final_select

            # except sqlalchemy.exc.OperationalError as e:
            #     print("+ reconecting: sqlalchemy connection Error", str(e))
            #     self.connect()
            #     sleep(randrange(5,20))
            # except sqlalchemy.exc.ResourceClosedError as e:
            #     print("+ reconecting: sqlalchemy connection Error", str(e))
            #     self.connect()
            #     sleep(randrange(5, 20))
            # exception handles errors like connecting to database or if connection is closed
            except (sqlalchemy.exc.OperationalError, sqlalchemy.exc.ResourceClosedError):
                print("+ reconecting: sqlalchemy connection Error")
                self.connect()
                sleep(randrange(5, 20))

    def merge(self, tablename, data, filters, popkeys=None, schema=None, insert=True, update=True, on=False):
        """
        :param str tablename:
        :param dict data:
        :param dict filters:
        :param str schema:
        :param bool insert:
        :param bool update:
        :param list on:
        Description:
            usage: Compartment of web data with current database data.. insert of new and archive of old data
            data: dictionary where keys are int and values are dictionary that represents single row of data
            filter: dictionary that contains data that will filter database table data that is needed to compare
            schema: if schema is needed to be specified
            insert: if insert is False no data will be inserted
            update: if update is False no data will be updated/closed
            on: what columns it will compare default is all cols
            """

        class DbTable(object):
            pass

        for tries in range(5):
            try:
                filters = {k.lower(): v for k, v in filters.items()}
                engine = self.engine
                metadata = MetaData(bind=engine)
                table = Table(tablename, metadata, autoload=True, quote=True, schema=schema)
                self.lower(table)

                mapper(DbTable, table)

                DbTable.__getattribute__(DbTable, self.primary_key)
                session = sessionmaker(bind=engine)()
                results = session.query(DbTable).filter_by(**filters).statement

                # convert data to pandas tables
                db_df = pd.read_sql(results, engine)
                db_df.columns = map(str.lower, db_df.columns)
                web_df = pd.DataFrame.from_dict(data, orient='index')
                web_df = web_df.where((pd.notnull(web_df)), None)
                web_df.columns = map(str.lower, web_df.columns)  # change column names to lower_letters
                # gather datypes form MsSql InfoSchma
                # todo: add gather datatypes for Oracle and Postgre
                column_datatypes = {}
                convert_types = {'date': 'datetime64', 'datetime': 'datetime64', 'smalldatetime': 'datetime64',
                                 'int': 'int64', 'numeric': 'float64', 'bigint': 'int64'}

                if self.db_type == "MsSql":
                    column_datatypes = self.select("INFORMATION_SCHEMA.COLUMNS",
                                                   sql="select * from INFORMATION_SCHEMA.COLUMNS where table_name = '{}' ".format(tablename),
                                                   columns=['column_name', 'data_type'])
                    column_datatypes = [tuple(x.values()) for x in column_datatypes]
                    column_datatypes = {k.lower(): v for k, v in column_datatypes}

                # converting web_df columns to match db_df column datatype
                for col, type0 in db_df.dtypes.items():
                    if web_df.get(col) is not None:
                        if web_df[col].dtype != type0:
                            web_df[col] = web_df[col].astype(type0)
                            continue
                        datatype = column_datatypes.get(col)
                        if web_df[col].dtype == type0 and type0 == 'object' and datatype is not None:
                            conversion = convert_types.get(datatype)

                            if conversion is not None:
                                try:
                                    web_df[col] = web_df[col].astype(conversion)
                                    db_df[col] = db_df[col].astype(conversion)
                                except:
                                    pass
                                web_df[col] = web_df[col].where((pd.notnull(web_df[col])), None)
                                db_df[col] = db_df[col].where((pd.notnull(db_df[col])), None)

                # if on is not False then on is list of lower named columns
                if on is not False:
                    on = [str(o).lower() for o in on]
                else:
                    on = [key.lower() for key in list(data.get(0).keys())]

                # print("web_df", web_df.to_dict('records'))
                # print("db_df", db_df.to_dict('records'))
                # print("====="*30)

                # compare differences between web data and database data for specified filtered data
                if popkeys is None:
                    process_data = self.compare(web_df, db_df, on)
                else:
                    process_data = self.compare(web_df, db_df, on, popkeys=popkeys)

                # print(web_df.to_dict('records'))
                # print(db_df.to_dict('records'))
                # print("===="*30)
                # exit()
                # print(process_data)

                # insert new data and close old data if their is differance
                if process_data is not None:
                    # print(process_data)
                    close, inserting = tuple(process_data.get('close')), process_data.get('insert')
                    # closing records
                    # print("close", len(close))
                    if close != [] and update is True:
                        session.query(DbTable).filter(DbTable.__getattribute__(DbTable, self.primary_key).in_(close)) \
                            .update({self.archive_date: datetime.now()}, synchronize_session='fetch')

                    # inserting new records
                    # print("inserting", len(inserting))
                    if inserting != [] and insert is True:
                        try:
                            session.bulk_insert_mappings(DbTable, inserting)
                        except Exception as e:
                            print(str(e))

                session.commit()
                session.flush()
                break

            # exception handles errors like connecting to database or if connection is closed
            except (sqlalchemy.exc.OperationalError, sqlalchemy.exc.ResourceClosedError):
                print("+ reconecting: sqlalchemy connection Error")
                self.connect()

            # except Exception as e:
            #     exc_type, exc_obj, exc_tb = sys.exc_info()
            #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #     error =  '======================================\n database Err: \n +error type: %s \n +py location: %s \n +error line: %s \n +error description: %s \n======================================' % (str(exc_type), os.path.abspath(fname), exc_tb.tb_lineno, str(e))
            #     print(error)
            #     print(data)
            #     raise Exception(str(error))
            #

    def compare(self, web_df, db_df, on, popkeys=None):

        def convert_nan(v):
            if pd.isnull(v) or pd.isna(v):
                v = None
            return v

        # find all that does not exist in web frame
        # + ============= CLOSE ============= + "

        df_all = db_df.merge(web_df.drop_duplicates(), on=on,
                             how='left', indicator=True)

        close_rows = df_all[df_all['_merge'].isin(['left_only'])]
        close_ids = []
        if not close_rows.empty:
            close_persons = close_rows.to_dict('records')
            for close_person in close_persons:
                rowid = close_person.get(self.primary_key)
                close_ids.append(rowid)

        # find all that does not exist in database frame
        # + ============= INSERT ============= + "
        df_all = web_df.merge(db_df.drop_duplicates(), on=on,
                              how='left', indicator=True)
        for column in df_all.columns:
            if column.endswith('_y'):
                df_all.drop(column, axis=1, inplace=True)
            if column.endswith('_x'):
                df_all.rename(columns={column: column.replace("_x", "")}, inplace=True)

        insert_rows = []
        insert_row = df_all[df_all['_merge'].isin(['left_only'])]
        if not insert_row.empty:
            insert_rows = insert_row.to_dict('records')
            poper = [self.primary_key, '_merge', self.archive_date]
            if popkeys is not None:
                poper.extend(popkeys)

            # left_columns_remove that is y
            insert_rows = [{k: convert_nan(v) for k, v in check_ir.items()
                            if k not in poper} for check_ir in insert_rows]

        if close_ids or insert_rows:
            return {'close': close_ids, 'insert': insert_rows}

        return None

    def execute(self, packs):
        """
        :param list packs:
        Description:
            usage: splits list that contains data for merge method.
            Required keys of every dict is tablename, filters and data
            More about filters and data look in merge docstring
        """
        for pack in packs:
            tablename = pack.get('tablename')
            filters = pack.get('filters')
            data = pack.get('data')
            self.merge(tablename, data, filters)

    def create_table(self, table_name, args=None):
        """
        :param str table_name:
        :param list construct:
            Description:
                table_name - name how table will be called
                construct - list with dictionary that contains
                arguments such as name, type_, primary_key, nullable
        """
        # TODO: implement create table for oracle also
        engine = self.engine
        metadata = MetaData(engine)
        table = Table(table_name, metadata,
                      Column('id', Integer, primary_key=True),
                      Column('date_created', DateTime, server_default=text('Getdate()')),
                      Column('dat_pro', DateTime))
        for arg in args:
            table.append_column(Column(**arg))
        metadata.create_all()
