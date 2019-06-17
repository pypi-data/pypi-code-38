import unittest

from migrationmaker import (TableMigrationMaker, MetaDataMigration,
                            ColumnTool, MetaDataTool, VersionControl)
from sqlalchemy import Column, create_engine, inspect
from sqlalchemy.types import (String, Integer, DateTime, Date, Time, Text,
                              Boolean)
from .model import user_t1, user_t2, meta1, meta2, meta3


TYPES = [String, Integer, DateTime, Date, Time, Text, Boolean]


class TestBasicMigration(unittest.TestCase):
    db_uri = "postgresql://testing:testing@localhost:13639/testing"

    def test_column_type(self):
        print("Test SQL type to string")
        c = Column(String)
        self.assertEqual(ColumnTool.get_sql_type_str(c.type),
                         "VARCHAR")
        c = Column(Integer)
        self.assertEqual(ColumnTool.get_sql_type_str(c.type),
                         "INTEGER")
        c = Column(DateTime)
        self.assertEqual(ColumnTool.get_sql_type_str(c.type),
                         "TIMESTAMP")
        c = Column(Date)
        self.assertEqual(ColumnTool.get_sql_type_str(c.type),
                         "DATE")
        c = Column(Time)
        self.assertEqual(ColumnTool.get_sql_type_str(c.type),
                         "TIME")
        c = Column(Text)
        self.assertEqual(ColumnTool.get_sql_type_str(c.type),
                         "TEXT")
        c = Column(Boolean)
        self.assertEqual(ColumnTool.get_sql_type_str(c.type),
                         "BOOLEAN")
        c = Column(String(20))
        self.assertEqual(ColumnTool.get_sql_type_str(c.type),
                         "VARCHAR(20)")

    def test_compare_table(self):
        print("Test two table different")
        self.compare = TableMigrationMaker.compare_table(user_t1, user_t2)
        new_column = self.compare.added[0]
        type_ = new_column.type

        self.assertEqual(new_column.name, "password")
        self.assertTrue(isinstance(type_, String))
        self.assertEqual(type_.length, 32)
        self.assertTrue(new_column.nullable)
        self.assertEqual(new_column.default.arg, "123")

    def test_meta(self):
        engine = create_engine(TestBasicMigration.db_uri)
        conn = engine.connect()

        print("Preparing ...")
        table_names = inspect(engine).get_table_names()
        for table in table_names:
            conn.execute(f"""DROP TABLE "{table}";""")

        meta1.create_all(engine)

        print("Migrate with new model")
        meta_migration = MetaDataMigration(meta1)
        meta_migration.scan_new_metadata(meta2)

        self.assertEqual(len(meta_migration.altered_tables), 1)
        self.assertEqual(len(meta_migration.dropped_table), 1)
        self.assertEqual(len(meta_migration.new_tables), 1)

        self.assertFalse(meta_migration.check_same())

        meta_migration.migrate(conn, engine)

    def test_single_meta_migrate(self):
        print("Turn metadata to string")
        string = MetaDataTool.to_string(meta1)
        meta = MetaDataTool.string_to_metadata(string)

        print("Turn string to metadata")
        meta_migration = MetaDataMigration(meta1)
        meta_migration.scan_new_metadata(meta)

        self.assertTrue(meta_migration.check_same())

    def test_version_ctl(self):
        version_ctl = VersionControl(TestBasicMigration.db_uri)
        print("Check version control")
        version_ctl.check_version_ctl_exist()

        meta1_str = MetaDataTool.to_string(meta1)
        meta2_str = MetaDataTool.to_string(meta2)

        version_ctl.db_insert_version(meta1_str)
        latest_version = version_ctl.get_latest_version()
        self.assertEqual(meta1_str, latest_version)

        version_ctl.db_insert_version(meta2_str)
        latest_version = version_ctl.get_latest_version(is_old_metadata=True)
        self.assertEqual(meta2_str, latest_version)

        version_ctl.new_version(meta3)

        version_ctl.report_status()

        print("Migrate")
        version_ctl.migrate()

        latest_version = version_ctl.get_latest_version()
        self.assertEqual(MetaDataTool.to_string(meta3),
                         latest_version)


if __name__ == "__main__":
    unittest.main()
