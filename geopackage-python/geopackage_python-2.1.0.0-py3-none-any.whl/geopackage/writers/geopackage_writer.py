import threading
from os import makedirs
from os.path import dirname, exists, isdir

from rgi.geopackage.utility.sql_utility import get_database_connection


class GeoPackageWriter(object):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def clean(self):
        """
        Run vacuum on the DB to free up space after removing tiles.
        """
        self._database_connection().cursor().execute("VACUUM")

    def close(self):
        """
        closes the database connections and cleans the database
        """
        if getattr(self.__threading, 'db_conn', None):
            self._database_connection().close()
        self.__threading.db_conn = None

    def __init__(self,
                 gpkg_file_path,
                 timeout=500):
        """
        Constructor.

        :param gpkg_file_path: the path where the GeoPackage should be written to or an existing GeoPackage to write
        to
        :type gpkg_file_path: str

        :param timeout: connection's timeout in miliseconds
        :type timeout: float
        """

        # check the gpkg path
        if isdir(gpkg_file_path):
            raise ValueError("The gpkg_file_path cannot be a path to a directory. Path given: {path}"
                             .format(path=gpkg_file_path))
        self.file_path = gpkg_file_path

        # create the file if it doesn't exist
        if not exists(gpkg_file_path):
            # check to make sure the directories are created leading up to the file
            if not exists(dirname(gpkg_file_path)):
                makedirs(dirname(gpkg_file_path))
            # create the file
            with open(gpkg_file_path, 'w'):
                pass

        # this approach makes the database connection thread safe:
        # On some operating systems, a database connection should always be used in the same thread in which it was
        # originally created.
        # SQLite can be safely used by multiple threads provided that no single database connection is used
        # simultaneously in two or more threads.
        self.__threading = threading.local()
        self.__threading.db_conn = get_database_connection(file_path=gpkg_file_path,
                                                           timeout=timeout)
        # save the variables
        self.__timeout = timeout

    def _database_connection(self):
        # this approach makes the database connection thread safe:
        # On some operating systems, a database connection should always be used in the same thread in which it was
        # originally created.
        # SQLite can be safely used by multiple threads provided that no single database connection is used
        # simultaneously in two or more threads.
        if not getattr(self.__threading, 'db_conn', None):
            self.__threading.db_conn = get_database_connection(file_path=self.file_path,
                                                               timeout=self.__timeout)
        return self.__threading.db_conn
