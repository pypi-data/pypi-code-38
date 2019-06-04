# Copied from ThreeDiToolbox
from builtins import object
import copy

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.event import listen
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


def load_spatialite(con, connection_record):
    """Load spatialite extension as described in
    https://geoalchemy-2.readthedocs.io/en/latest/spatialite_tutorial.html"""
    import sqlite3

    con.enable_load_extension(True)
    cur = con.cursor()
    libs = [
        # SpatiaLite >= 4.2 and Sqlite >= 3.7.17, should work on all platforms
        ("mod_spatialite", "sqlite3_modspatialite_init"),
        # SpatiaLite >= 4.2 and Sqlite < 3.7.17 (Travis)
        ("mod_spatialite.so", "sqlite3_modspatialite_init"),
        # SpatiaLite < 4.2 (linux)
        ("libspatialite.so", "sqlite3_extension_init"),
    ]
    found = False
    for lib, entry_point in libs:
        try:
            cur.execute("select load_extension('{}', '{}')".format(lib, entry_point))
        except sqlite3.OperationalError:
            continue
        else:
            found = True
            break
    if not found:
        raise RuntimeError("Cannot find any suitable spatialite module")
    cur.close()
    con.enable_load_extension(False)


class ThreediDatabase(object):
    def __init__(self, connection_settings, db_type="spatialite", echo=False):
        """

        :param connection_settings:
        db_type (str choice): database type. 'sqlite' and 'postgresql' are
                              supported
        """
        self.settings = connection_settings
        self.db_type = db_type
        self.echo = echo

        self._engine = None
        self._base_metadata = None

    @property
    def engine(self):
        return self.get_engine()

    def get_engine(self, get_seperate_engine=False):

        if self._engine is None or get_seperate_engine:
            if self.db_type == "spatialite":
                engine = create_engine(
                    "sqlite:///{0}".format(self.settings["db_path"]), echo=self.echo
                )
                listen(engine, "connect", load_spatialite)
                if get_seperate_engine:
                    return engine
                else:
                    self._engine = engine

            elif self.db_type == "postgres":
                con = (
                    "postgresql://{username}:{password}@{host}:"
                    "{port}/{database}".format(**self.settings)
                )

                engine = create_engine(con, echo=self.echo)
                if get_seperate_engine:
                    return engine
                else:
                    self._engine = engine

        return self._engine

    def get_metadata(self, including_existing_tables=True, engine=None):

        if including_existing_tables:
            metadata = copy.deepcopy(Base.metadata)
            if engine is None:
                engine = self.engine

            metadata.bind = engine
            metadata.reflect(extend_existing=True)
            return metadata
        else:
            if self._base_metadata is None:
                self._base_metadata = copy.deepcopy(Base.metadata)
            return self._base_metadata

    def get_session(self):
        return sessionmaker(bind=self.engine)()

    def check_connection(self):
        """Check if there a connection can be started with the database

        :return: True if a connection can be established, otherwise raises an
            appropriate error.
        """
        session = self.get_session()
        r = session.execute("select 1")
        return r.fetchone()
