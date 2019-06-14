import re

from datetime import datetime
from sqlalchemy import MetaData, Table, Column, create_engine
from sqlalchemy.sql import select
from sqlalchemy.types import (String, Integer, DateTime, Date, Time, Text,
                              Boolean)

ADD_UNIQUE = """ALTER TABLE "{table}"
                ADD CONTRAINT {table}_{column}_key
                UNIQUE ({column});"""
DROP_UNIQUE = """ALTER TABLE "{table}"
                 DROP CONTRAINT {table}_{column}_key;"""

SET_NOT_NULL = """ALTER TABLE "{table}"
                  ALTER COLUMN {column}
                  SET NOT NULL;"""
DROP_NOT_NULL = """ALTER TABLE "{table}"
                   ALTER COLUMN {column}
                   DROP NOT NULL;"""

ADD_COLUMN = """ALTER TABLE "{table}"
                ADD COLUN {column} {type}{constraint}"""

DROP_COLUMN = """ALTER TABLE "{table}" DORP COLUMN {column};"""


class ColumnTool:
    @staticmethod
    def get_sql_type_str(type_):
        if isinstance(type_, type):
            if type_ == String:
                return "VARCHAR"
            elif type_ == Integer:
                return "INTEGER"
            elif type_ == DateTime:
                return "TIMESTAMP"
            elif type_ == Date:
                return "DATE"
            elif type_ == Time:
                return "TIME"
            elif type_ == Text:
                return "TEXT"
            elif type_ == Boolean:
                return "BOOLEAN"
            return None

        if isinstance(type_, Text):
            return "TEXT"
        elif isinstance(type_, Integer):
            return "INTEGER"
        elif isinstance(type_, DateTime):
            return "TIMESTAMP"
        elif isinstance(type_, Date):
            return "DATE"
        elif isinstance(type_, Time):
            return "TIME"
        elif isinstance(type_, String):
            if type_.length is None:
                return "VARCHAR"
            return f"VARCHAR({type_.length})"
        elif isinstance(type_, Boolean):
            return "BOOLEAN"

    @staticmethod
    def get_type(string):
        if string == "VARCHAR":
            return String
        elif string == "INTEGER":
            return Integer
        elif string == "TIMESTAMP":
            return DateTime
        elif string == "DATE":
            return Date
        elif string == "TIME":
            return Time
        elif string == "TEXT":
            return Text
        elif string == "BOOLEAN":
            return Boolean
        elif string.startswith("VARCHAR"):
            length = string.replace("VARCHAR(", "")[:-1]
            return String(length)

    @staticmethod
    def get_constraint(column):
        con = ""
        if column.nullable:
            con += " NOT NULL"
        if column.unique:
            con += " UNIQUE"
        return con


class TableMigrationMaker:
    def __init__(self, table, changed, added, dropped):
        self.table = table

        self.changed = changed
        self.added = added
        self.dropped = dropped

        self.sqls = []

    def check_same(self):
        return (len(self.changed) == 0 and len(self.added) == 0 and
                len(self.dropped) == 0)

    def make_migration(self):
        tb_name = self.table.name

        for c in self.dropped:
            self.sqls.append(DROP_COLUMN.format(table=tb_name, column=c))

        for name, changed in self.changed.items():
            if "unique" in changed:
                if changed["unique"]:
                    self.sqls.append(ADD_UNIQUE.format(table=tb_name,
                                                       column=name))
                else:
                    self.sqls.append(DROP_UNIQUE.format(table=tb_name,
                                                        column=name))

            if "nullable" in changed:
                if changed["nullable"]:
                    self.sqls.append(SET_NOT_NULL.format(table=tb_name,
                                                         column=name))
                else:
                    self.sqls.append(DROP_NOT_NULL.format(table=tb_name,
                                                          column=name))

        for column in self.added:
            self.sqls.append(ADD_COLUMN.format(
                table=tb_name, column=column.name,
                type=ColumnTool.get_sql_type_str(column.type),
                contraint=ColumnTool.get_constraint(column)))

    def migrate(self, conn):
        for sql in self.sqls:
            conn.execute(sql)

    @classmethod
    def compare_table(cls, original, new):
        changed_column = {}
        added_column = []
        dropped_column = []

        for c in original.columns.keys():
            column = original.columns.get(c)

            new_column = new.columns.get(c)
            if new_column is None:
                dropped_column.append(c)
                continue

            com = cls.compare_column(column, new_column)
            if len(com) > 0:
                changed_column[c] = com

        for c in new.columns.keys():
            new_column = new.columns.get(c)

            column = original.columns.get(c)
            if column is None:
                added_column.append(new_column)

        return cls(original, changed_column, added_column, dropped_column)

    @staticmethod
    def compare_column(original, new):
        changed = {}

        if original.nullable != new.nullable:
            changed["nullable"] = new.nullable
        if original.unique != new.unique:
            changed["unique"] = new.unique

        return changed


class MetaDataTool:
    @staticmethod
    def to_string(metadata):
        string = ""

        for tb_name, table in dict(metadata.tables).items():
            string += tb_name.capitalize()

            for column in table.columns:
                string += ","
                string += column.name.capitalize()
                string += ColumnTool.get_sql_type_str(column.type).capitalize()

                if column.nullable:
                    string += "Nullable"
                if column.unique:
                    string += "Unique"

            string += ";"
        return string

    @staticmethod
    def string_to_metadata(string):
        temp_metadata = MetaData()
        tb_datas = string.split(";")
        tb_datas.remove("")

        for data in tb_datas:
            tb_name = data.split(",")[0].lower()
            columns_data = data.split(",")[1:]

            table = Table(tb_name, temp_metadata)
            for column_data in columns_data:
                args = re.findall(r"[A-Z][^A-Z]+", column_data)
                c = Column(args[0].lower(),
                           ColumnTool.get_type(args[1].upper()))

                if "Nullable" in args:
                    c.nullable = True
                if "Unique" in args:
                    c.unique = True

                table.append_column(c)

        return temp_metadata


class MetaDataMigration:
    def __init__(self, metadata):
        self.tables = dict(metadata.tables)

        self.altered_tables = []
        self.new_tables = []
        self.dropped_table = []

    def check_same(self):
        return (len(self.altered_tables) == 0 and len(self.new_tables) == 0 and
                len(self.dropped_table) == 0)

    def scan_new_metadata(self, metadata):
        for tb_name, table in self.tables.items():
            if tb_name not in metadata.tables:
                self.dropped_table.append(tb_name)
                continue

            compare = TableMigrationMaker.compare_table(
                table, metadata.tables[tb_name])

            if compare.check_same():
                self.altered_tables.append(compare)

        for tb_name, table in dict(metadata.tables).items():
            if tb_name not in self.tables:
                self.new_tables.append(table)

    def migrate(self, conn, engine):
        for table in self.new_tables:
            table.create(engine)

        for compare in self.altered_tables:
            compare.make_migration()
            compare.migrate(conn)

        for table in self.dropped_table:
            conn.execute(f"""DROP TABLE "{table}";""")


class VersionControl:
    def __init__(self, db_uri):
        self.engine = create_engine(db_uri)
        self.verison_ctl_t = None
        self.conn = None

    def check_version_ctl_exist(self):
        self.verison_ctl_t = Table(
            "version_ctl", MetaData(),
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("version", String),
            Column("create_at", DateTime, default=datetime.utcnow))

        self.verison_ctl_t.create(self.engine)

    def connect(self):
        self.conn = self.engine.connect()

    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def insert_version(self, version_str):
        rst = self.conn.execute(self.verison_ctl_t.insert(), {
            "version": version_str})

        if rst.is_insert:
            return True
        return False

    def get_latest_version(self):
        select_sql = select([self.verison_ctl_t.c.version]).order_by(
            self.verison_ctl_t.c.create_at.desc())

        row = self.conn.execute(select_sql).fetchone()

        if row is not None:
            return row["version"]
        return None
