import re

from sqlalchemy import MetaData, Table, Column
from sqlalchemy.types import (String, Integer, DateTime, Date, Time, Text,
                              Boolean)

ADD_UNIQUE1 = """ALTER TABLE "{table}"
                ADD CONTRAINT "{table}_{column}_key"
                UNIQUE ({column});"""
ADD_UNIQUE2 = """CREATE UNIQUE INDEX "{table}_{column}_key"
                 ON "{table}" ({column});"""

DROP_UNIQUE1 = """ALTER TABLE "{table}"
                 DROP CONTRAINT "{table}_{column}_key";"""
DROP_UNIQUE2 = """DROP INDEX "{table}_{column}_key";"""

SET_NOT_NULL = """ALTER TABLE "{table}"
                  ALTER COLUMN {column}
                  SET NOT NULL;"""
DROP_NOT_NULL = """ALTER TABLE "{table}"
                   ALTER COLUMN {column}
                   DROP NOT NULL;"""

ADD_COLUMN = """ALTER TABLE "{table}"
                ADD COLUMN {column} {type}{constraint}"""

DROP_COLUMN = """ALTER TABLE "{table}" DROP COLUMN {column};"""


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
        self.name = table.name
        self.table = table

        self.changed = changed
        self.added = added
        self.dropped = dropped

        self.sqls = []

    def report_status(self, prefix=""):
        for col in self.dropped:
            print(prefix, "-", col, "dropped")

        for col in self.added:
            print(prefix, "-", col.name, "added")

        for col, changes in self.changed.items():
            description = ""

            if "unique" in changes:
                if changes["unique"]:
                    description += "add UNIQUE "
                else:
                    description += "drop UNIQUE "
            if "nullable" in changes:
                if changes["nullable"]:
                    description += "drop NOT NULL"
                else:
                    description += "add NOT NULL"

            print(prefix, "-", col, description)

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
                    self.sqls.append((
                        ADD_UNIQUE1.format(table=tb_name, column=name),
                        ADD_UNIQUE2.format(table=tb_name, column=name),))
                else:
                    self.sqls.append((
                        DROP_UNIQUE1.format(table=tb_name, column=name),
                        DROP_UNIQUE2.format(table=tb_name, column=name)))

            if "nullable" in changed:
                if changed["nullable"]:
                    self.sqls.append(DROP_NOT_NULL.format(table=tb_name,
                                                          column=name))
                else:
                    self.sqls.append(SET_NOT_NULL.format(table=tb_name,
                                                         column=name))

        for column in self.added:
            self.sqls.append(ADD_COLUMN.format(
                table=tb_name, column=column.name,
                type=ColumnTool.get_sql_type_str(column.type),
                constraint=ColumnTool.get_constraint(column)))

    def migrate(self, conn):
        for sql in self.sqls:
            if isinstance(sql, tuple):
                for s in sql:
                    try:
                        conn.execute(s)
                        break
                    except Exception:
                        pass

                continue
            else:
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
            if original.nullable is True or new.nullable is True:
                changed["nullable"] = new.nullable
        if original.unique != new.unique:
            if original.unique is True or new.unique is True:
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
                else:
                    c.nullable = False
                if "Unique" in args:
                    c.unique = True
                else:
                    c.unique = False

                table.append_column(c)

        return temp_metadata


class MetaDataMigration:
    def __init__(self, metadata):
        self._old_metadata = metadata
        self._tables = dict(metadata.tables)

        self.altered_tables = []
        self.new_tables = []
        self.dropped_table = []

    def check_same(self):
        return (len(self.altered_tables) == 0 and len(self.new_tables) == 0 and
                len(self.dropped_table) == 0)

    def scan_new_metadata(self, metadata):
        for tb_name, table in self._tables.items():
            if tb_name not in metadata.tables:
                self.dropped_table.append(tb_name)
                continue

            compare = TableMigrationMaker.compare_table(
                table, metadata.tables[tb_name])

            if not compare.check_same():
                self.altered_tables.append(compare)

        for tb_name, table in dict(metadata.tables).items():
            if tb_name not in self._tables:
                self.new_tables.append(table)

    def migrate(self, conn, engine):
        for table in self.new_tables:
            table.create(engine)

        for compare in self.altered_tables:
            compare.make_migration()
            compare.migrate(conn)

        for table in self.dropped_table:
            conn.execute(f"""DROP TABLE "{table}";""")
