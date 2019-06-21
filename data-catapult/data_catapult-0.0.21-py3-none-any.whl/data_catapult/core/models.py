import os
import logging
import itertools
from data_catapult.database import postgres, monetdb
from sqlalchemy import create_engine
from monetdb.sql import connect as monet_connect


class InvalidSettingException(Exception):
    pass


class Pipeline(object):

    def __init__(self, tbl_name, config=None):
        self.tbl_name = tbl_name
        self.engines = {}
        self.config = config if config else {}
        dbs_config = Pipeline.get_setting(["global", "db_settings"],
                                          self.config)
        if dbs_config:
            for db, db_config in dbs_config.items():
                database_type = db
                user = db if "user" not in db_config else db_config["user"]
                host = "127.0.0.1" if "host" not in db_config else db_config["host"]
                db_name = "" if "db_name" not in db_config else db_config["db_name"]
                pw = "" if "password_env_var" not in db_config else os.environ.get(db_config["password_env_var"])
                port = 5432 if "port" not in db_config else db_config["port"]

                if db == "postgres":
                    params = {
                        "user": user,
                        "host": host,
                        "pw": pw,
                        "db_name": db_name,
                        "database_type": database_type,
                        "port": port
                    }
                    con_str = '{database_type}://{user}:{pw}@{host}:{port}/{db_name}'.format(**params)
                    self.engines['postgres'] = create_engine(con_str, echo=False)
                elif db == "monetdb":
                    self.engines['monetdb'] = monet_connect(
                        username=user,
                        password=pw,
                        hostname=host,
                        port=port,
                        database=db_name
                    )
            # TODO add verbose
            # print("Engines: {}".format(self.engines))

    @staticmethod
    def combos(**kwargs):
        vals = list(kwargs.values())
        combos = itertools.product(*vals)
        combos_lbls = [dict(zip(kwargs.keys(), combo)) for combo in combos]
        return combos_lbls

    @classmethod
    def get_setting(cls, names, my_data, optional=True, default=None):
        '''Accepts a single name or list of names which are then looked up in sequence
        in passed dictionary (my_data).'''
        if isinstance(names, str):
            names = [names]
        for name in names:
            if name not in my_data:
                if not optional:
                    msg = "{} not in configuration!".format(name)
                    raise InvalidSettingException(msg)
                else:
                    return default
            my_data = my_data[name]
        return my_data

    def load(self, df, schema='public', dtype=None, databases=[]):
        # databases default for cny is 'postgres', set in pipeline of cny.
        # create dict for dispatch
        # ---------------------------------------
        def do_postgres():
            db = postgres.PostgresDriver(self.engines['postgres'])
            db.to_sql(df, schema, self.tbl_name, dtype=dtype)

        def do_monetdb():
            db = monetdb.MonetDBDriver(self.engines['monetdb'])
            db.to_sql(df, schema, self.tbl_name, dtype=dtype)

        export_db = {
            "postgres": do_postgres,
            "monetdb": do_monetdb,
        }
        # ---------------------------------------

        # Start regular logic
        # check if drivers is an empty list or None
        if not databases:
            return

        # TODO verbose
        print(self.engines)
        for database in databases:
            export_db[database]()

        # End of regular logic. Below,


class DbWriter(object):

    def __init__(self, dbs_config=None):
        self.drivers = {}
        if not dbs_config:
            logging.warn("No database configuration found")
            return
        for db, db_config in dbs_config.items():
            database_type = db
            user = db if "user" not in db_config else db_config["user"]
            host = "127.0.0.1" if "host" not in db_config else db_config["host"]
            db_name = "" if "db_name" not in db_config else db_config["db_name"]
            pw = "" if "password" not in db_config else db_config["password"]

            if db == "postgres":
                port = 5432 if "port" not in db_config else db_config["port"]
                params = {
                    "user": user,
                    "host": host,
                    "pw": pw,
                    "db_name": db_name,
                    "database_type": database_type,
                    "port": port
                }
                con_str = '{database_type}://{user}:{pw}@{host}:{port}/{db_name}'.format(**params)
                postgres_engine = create_engine(con_str, echo=False)
                self.drivers['postgres'] = postgres.PostgresDriver(postgres_engine)

            elif db == "monetdb":
                port = 50000 if "port" not in db_config else db_config["port"]
                print(user, pw, host, port, db_name)
                monetdb_engine = monet_connect(
                    username=user,
                    password=pw,
                    hostname=host,
                    port=port,
                    database=db_name
                )
                self.drivers['monetdb'] = monetdb.MonetDBDriver(monetdb_engine)

    def write(self, df, table_name, schema='public', dtype=None, databases=None):
        for db in databases:
            try:
                self.drivers[db].to_sql(df, schema, table_name, dtype=dtype)
            except Exception as err:
                print("Database driver not found", type(err), err)
