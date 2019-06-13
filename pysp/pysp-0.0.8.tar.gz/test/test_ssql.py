
import datetime
import os
import shutil
import sqlalchemy as sa
import unittest

from pysp.sbasic import SFile
from pysp.serror import SDebug
from pysp.sconf import SConfig
from pysp.ssql import SSimpleDB


class SsqlTest(unittest.TestCase, SDebug, SFile):
    # DEBUG = True
    test_folder = '/tmp/sql/'
    config_file = test_folder+'db.cfg'
    db_file = test_folder+'test.sqlite3'

    def test_db(self):
        if os.path.exists(self.test_folder):
            shutil.rmtree(self.test_folder)
        try:
            self.check_create()
            self.check_alter()
            self.check_upsert()
            self.check_query()
            self.check_count()
            self.check_drop_columns()
            self.check_rename_columns()
        except Exception:
            self.assertTrue(False)

    def check_create(self):
        DBCONFIG = '''
tables:
    - name: inspection
      columns:
        - [SNumber, String10, NotNull, CollateNocase, Unique, PrimaryKey]
        - [Integer, Integer, NotNull]
        - [Float, Float]
        - [Bool, Boolean]
        - [DateTime, DateTime]
'''
        self.to_file(self.config_file, DBCONFIG)
        dbconfig = SConfig(self.config_file)
        db = SSimpleDB(self.db_file, dbconfig)
        del db

    def check_alter(self):
        DBCONFIG = '''
tables:
    - name: inspection
      columns:
        - [SNumber, String10, NotNull, CollateNocase, Unique, PrimaryKey]
        - [Integer, Integer, NotNull]
        - [Float, Float]
        - [Bool, Boolean]
        - [DateTime, DateTime]
        - [Date, Date]
        - [Alter1, String15, Unique]
        - [Alter2, String5]
'''
        self.to_file(self.config_file, DBCONFIG)
        db = SSimpleDB(self.db_file, SConfig(self.config_file))
        del db

    def check_upsert(self):
        db = SSimpleDB(self.db_file, SConfig(self.config_file))
        data = {
            'SNumber':  '0000000000',
            'Integer':  1234,
            'Date':     datetime.datetime.now().date(),
        }
        items = {
            'data': data
        }
        db.upsert('inspection', **items)
        data = {
            'SNumber':  '0000000000',
            'Alter2':   'Five5',
            'DateTime': sa.sql.func.now(),
        }
        items = {
            'data': data
        }
        db.upsert('inspection', **items)
        for i in range(10):
            data = {
                'SNumber':  '%010d' % i,
                'Integer':  9 - i,
                'Alter1':   '%05d' % i,
            }
            items = {
                'data': data
            }
            db.upsert('inspection', **items)
        del db

    def check_query(self):
        db = SSimpleDB(self.db_file, SConfig(self.config_file))
        columns = ['SNumber', 'Integer', 'Float', 'Alter1', 'Alter2']
        options = {
            'wheres': {
                'Alter1': ['00000', '00005'],
                'Alter2': 'Five5',
            },
            'operate': SSimpleDB.OP_AND,
            'page': 0,
            'size': 4,
        }
        data = db.query('inspection', *columns, **options)
        self.assertTrue(len(data) == 1)
        data = data[0]
        self.assertTrue(data[0] == '0000000000')
        self.assertTrue(data[1] == 9)
        self.assertTrue(data[2] is None)
        self.assertTrue(data[3] == '00000')
        self.assertTrue(data[4] == 'Five5')

        columns = []
        options = {
            'wheres': {
                'Alter1': ['00000', '00005'],
                'Alter2': 'Five5',
            },
            'operate': SSimpleDB.OP_OR,
            'page': 0,
            'size': 4,
        }
        data = db.query('inspection', *columns, **options)
        self.assertTrue(len(data) == 2)
        for item in data:
            self.assertTrue(item[0] in ['0000000000', '0000000005'])

    def check_count(self):
        db = SSimpleDB(self.db_file, SConfig(self.config_file))
        self.assertTrue(db.count('inspection') == 10)
        columns = []
        options = {
            'wheres': {
                'Alter1': ['00000', '005'],
                'Alter2': 'Five5',
            },
            'operate': SSimpleDB.OP_OR,
            'page': 0,
            'size': 4,
        }
        self.assertTrue(db.count('inspection', *columns, **options) == 2)
        columns = ['SNumber', 'Integer', 'Float', 'Alter1', 'Alter2']
        options = {
            'wheres': {
                'Alter1': ['00000', '00005'],
                'Alter2': 'Five5',
            },
            'operate': SSimpleDB.OP_AND,
            'page': 0,
            'size': 4,
        }
        self.assertTrue(db.count('inspection', *columns, **options) == 1)

    def check_drop_columns(self):
        DBCONFIG = '''
tables:
    - name: inspection
      columns:
        - [SNumber, String10, NotNull, CollateNocase, Unique, PrimaryKey]
        - [Integer, Integer, NotNull]
        - [Float, Float]
        - [DateTime, DateTime]
        - [Date, Date]
        - [Alter2, String5]
      migrate:
        operation: drop
'''
        self.to_file(self.config_file, DBCONFIG)
        db = SSimpleDB(self.db_file, SConfig(self.config_file))
        columns = ['SNumber', 'Integer', 'Alter2']
        options = {
            'wheres': {
                'Alter2': 'Five5',
            },
            'operate': SSimpleDB.OP_AND,
            'page': 0,
            'size': 4,
        }
        self.assertTrue(db.count('inspection', *columns, **options) == 1)
        del db

    def check_rename_columns(self):
        DBCONFIG = '''
tables:
    - name: inspection
      columns:
        - [SNumber, String10, NotNull, CollateNocase, Unique, PrimaryKey]
        - [Pass, String5]
        - [AString, String20]
        - [Integer, Integer, NotNull]
        - [DateTime, DateTime]
        - [Date, Date]
      migrate:
        operation: rename
        columns:
            Pass: Alter2
'''
        self.to_file(self.config_file, DBCONFIG)
        db = SSimpleDB(self.db_file, SConfig(self.config_file))
        columns = ['SNumber', 'Integer', 'Pass']
        options = {
            'wheres': {
                'Pass': 'Five5',
            },
            'operate': SSimpleDB.OP_AND,
            'page': 0,
            'size': 4,
        }
        self.assertTrue(db.count('inspection', *columns, **options) == 1)
        db.vacuum()
        del db
