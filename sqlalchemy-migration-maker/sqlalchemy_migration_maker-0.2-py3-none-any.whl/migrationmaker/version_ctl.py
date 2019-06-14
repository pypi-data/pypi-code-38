from .migration import MetaDataMigration, MetaDataTool

from datetime import datetime
from sqlalchemy import create_engine, Table, Column, MetaData
from sqlalchemy.types import Integer, String, DateTime
from sqlalchemy.sql import select


class VersionControl(MetaDataMigration):
    def __init__(self, db_uri):
        self.engine = create_engine(db_uri)
        self.verison_ctl_t = None
        self.conn = None

        self.metadata = None
        self.tables = {}

        self.altered_tables = []
        self.new_tables = []
        self.dropped_table = []

    def report_status(self):
        print("-" * 10, "Status", "-" * 10)
        if len(self.dropped_table) > 0:
            print("Table dropped:")
            for tb in self.dropped_table:
                print(" -", tb)
            print()

        if len(self.new_tables) > 0:
            print("Table added:")
            for tb in self.new_tables:
                print(" -", tb)
            print()

        if len(self.altered_tables) > 0:
            print("Table altered:")
            for tb in self.altered_tables:
                print(" -", tb.name)
                tb.report_status(prefix="  ")
            print()

        print("-" * 28)

    def assign_metadata(self, metadata):
        self.metadata = metadata
        self.tables = dict(metadata.tables)

    def migrate(self):
        self.connect()

        super().migrate(self.conn, self.engine)

        self.insert_version(MetaDataTool.to_string(self.metadata))

        self.close()

    def check_version_ctl_exist(self):
        self.verison_ctl_t = Table(
            "version_ctl", MetaData(),
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("version", String),
            Column("create_at", DateTime, default=datetime.utcnow))

        self.verison_ctl_t.create(self.engine)

    def connect(self):
        if self.conn is None:
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

    def get_latest_version(self, is_old_metadata=False):
        select_sql = select([self.verison_ctl_t.c.version]).order_by(
            self.verison_ctl_t.c.create_at.desc())

        row = self.conn.execute(select_sql).fetchone()

        if row is not None:
            data = row["version"]
            if is_old_metadata:
                self.assign_metadata(MetaDataTool.string_to_metadata(data))

            return data
        return None
