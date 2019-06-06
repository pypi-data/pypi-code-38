from thompcoutils.log_utils import get_logger
from thompcoutils.config_utils import ConfigManager
import logging
import sqlobject
import os


class DBConfig:
    def __init__(self, cfg_mgr=None, db_type=None, sqlite_file=None, host=None, username=None, password=None,
                 schema=None, port=None, rebuild=None, section="db connection"):
        if cfg_mgr is None:
            self.type = db_type
            self.sqlite_file = sqlite_file
            self.host = host
            self.username = username
            self.password = password
            self.schema = schema
            self.port = port
            self.rebuild = rebuild
        else:
            self.type = cfg_mgr.read_entry(section, "type", default_value="mysql")
            self.sqlite_file = cfg_mgr.read_entry(section, "sqlite file", default_value="licenseserver.sqlite")
            self.host = cfg_mgr.read_entry(section, "host", default_value="localhost")
            self.username = cfg_mgr.read_entry(section, "username", default_value="my db user name")
            self.password = cfg_mgr.read_entry(section, "password", default_value="my db user password")
            self.schema = cfg_mgr.read_entry(section, "schema", default_value="my db schema")
            self.port = cfg_mgr.read_entry(section, "port", default_value=3306)
            self.rebuild = cfg_mgr.read_entry(section, "rebuild", default_value=False)


class DbUtils:
    def __init__(self, db_cfg=None, db_type=None, host=None, username=None, password=None, schema=None, port=None,
                 sqlite_file=None):
        self.connection = None
        if db_cfg is not None:
            db_type = db_cfg.type
            host = db_cfg.host
            username = db_cfg.username
            password = db_cfg.password
            schema = db_cfg.schema
            port = db_cfg.port
        if db_type == "sqlite":
            if sqlite_file is None:
                raise RuntimeError("--sqlite requires --sqlite-dir")
            else:
                print("Using Sqlite database")
                self._connect_sqlite(sqlite_file)
        elif db_type == "postgres":
            self._connect_postgres(username, password, schema, host, port)
        elif "mysql" in db_type:
            self._connect_mysql(username, password, schema, host, port)
        elif db_type == "odbc":
            raise RuntimeError("ODBC not implemented yet")
        else:
            raise RuntimeError("No database type selected")

    def _connect_uri(self, uri):
        self.connection = sqlobject.sqlhub.processConnection = sqlobject.connectionForURI(uri)

    def _connect_sqlite(self, file_path):
        uri = "sqlite:" + file_path
        self._connect_uri(uri)

    def _connect_postgres(self, username, password, database, host, port):
        port_str = ""
        if port is not None:
            port_str = ":" + str(port)
        uri = "postgres://" + username + ":" + password + "@" + host + port_str + "/" + database
        self._connect_uri(uri)

    def _connect_mysql(self, username, password, database, host, port):
        port_str = ""
        if port is not None:
            port_str = ":" + str(port)
        uri = "mysql://" + username + ":" + password + "@" + host + port_str + "/" + database
        self._connect_uri(uri)

    def create_table(self, table):
        logger = get_logger()
        if not self.connection.tableExists(table.q.tableName):
            logger.debug("creating table {}".format(str(table)))
            table.createTable()

    def create_tables(self, tables):
        logger = get_logger()
        logger.debug("Creating tables...")
        for table in tables:
            self.create_table(table)

    @staticmethod
    def drop_tables(tables):
        logger = get_logger()
        logger.debug("Dropping tables...")
        for table in tables:
            logger.debug("dropping table {}".format(str(table)))
            table.dropTable(cascade=True, ifExists=True)


def main():
    create_file = False
    logging.config.fileConfig('logging.conf')
    temp_filename = "testing DbConfig only.cfg"
    if create_file:
        if os.path.isfile(temp_filename):
            os.remove(temp_filename)
    cfg_mgr = ConfigManager(temp_filename, create=create_file)
    db_cfg = DBConfig(cfg_mgr=cfg_mgr)
    if create_file:
        cfg_mgr.write(temp_filename)
    db = DbUtils(db_cfg)


if __name__ == "__main__":
    main()
