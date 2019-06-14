#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sqlite3
import traceback

from Homevee.DBMigration import DBMigration
from Homevee.Helper import Logger
from Homevee.Utils import Constants


# use encrypted databases
# http://charlesleifer.com/blog/encrypted-sqlite-databases-with-python-and-sqlcipher/

class Database():
    def __init__(self):
        self.db_con = self.get_database_con()

    @staticmethod
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def get_database_con(self):
        db_path = os.path.join(Constants.DATA_DIR, "data.db")

        # init db if not yet existing
        if not os.path.isfile(db_path):
            open(db_path, "w+")
            self.upgrade()
        con = sqlite3.connect(db_path)
        con.text_factory = str
        con.row_factory = Database.dict_factory

        return con

    def get_server_data(self, key):
        item = self.select_one("SELECT VALUE FROM SERVER_DATA WHERE KEY = :key",
                    {'key': key})

        try:
            return item['VALUE']
        except Exception as e:
            return None

    def set_server_data(self, key, value):
        self.insert("INSERT OR IGNORE INTO SERVER_DATA (VALUE, KEY) VALUES(:value, :key)",
                    {'value': value, 'key': key})

        self.update("UPDATE OR IGNORE SERVER_DATA SET VALUE = :value WHERE KEY = :key",
                    {'value': value, 'key': key})

    def do_query(self, query, params=None):
        #Logger.log(("DATABASE_QUERY", query, params))

        if params is None:
            params = {}

        with self.db_con:
            cur = self.db_con.cursor()
            cur.execute(query, params)
            return cur

    def select_one(self, query, params=None):
        try:
            cur = self.do_query(query, params)
            output = cur.fetchone()
            cur.close()
            return output
        except:
            return None

    def select_all(self, query, params=None):
        try:
            cur = self.do_query(query, params)
            output = cur.fetchall()
            cur.close()
            return output
        except:
            return []

    def insert(self, query, params=None):
        try:
            cur = self.do_query(query, params)
            last_id = cur.lastrowid
            cur.close()
            return last_id
        except:
            if Logger.IS_DEBUG:
                traceback.print_exc()
        return False

    def update(self, query, params=None):
        try:
            cur = self.do_query(query, params)
            cur.close()
            return True
        except:
            if Logger.IS_DEBUG:
                traceback.print_exc()
        return False

    def delete(self, query, params=None):
        try:
            cur = self.do_query(query, params)
            cur.close()
            return True
        except:
            if Logger.IS_DEBUG:
                traceback.print_exc()
        return False

    @staticmethod
    def upgrade():
        """
        Upgrades the database to the current scheme
        :return:
        """
        Logger.log("Upgrading Database...")
        db = Database()
        with db.db_con:
            cur = db.db_con.cursor()
            migration = DBMigration()
            try:
                db_version = int(db.get_server_data("DB_VERSION"))
            except:
                db_version = 0
            db_script_map = migration.get_filecontent_version_map()
            db_script_versions = db_script_map.keys()
            last_version = 0
            for version in db_script_versions:
                if (version <= db_version):
                    continue
                try:
                    Logger.log("Executing DB-Upgrade-Script V" + str(version) + "...")
                    cur.executescript(db_script_map[version])
                except:
                    db.set_server_data("DB_VERSION", version)
            cur.close()