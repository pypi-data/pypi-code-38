"""
Manage *hynet*'s database connections.
"""

import logging
import textwrap

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from hynet.data.structure import (SCHEMA_VERSION,
                                  Base,
                                  DBInfo,
                                  DBBus,
                                  DBBranch,
                                  DBConverter,
                                  DBInjector,
                                  DBShunt,
                                  DBScenario)
from hynet.types_ import DBInfoKey

_log = logging.getLogger(__name__)

DIALECT_PREFIX_SEPARATOR = ':///'
DESCRIPTION_LINE_LENGTH = 75


def connect(database_uri):
    """
    Return a connection to the specified *hynet* grid database.

    Parameters
    ----------
    database_uri : str
        URI or file name of the *hynet* grid database.

    Returns
    -------
    database : DBConnection
        Connection to the *hynet* grid database.
    """
    if DIALECT_PREFIX_SEPARATOR not in database_uri:
        database_uri = 'sqlite' + DIALECT_PREFIX_SEPARATOR + database_uri
    return DBConnection(database_uri)


class DBConnection:
    """
    Manager for a *hynet* grid database connection.

    See Also
    --------
    hynet.data.connection.DBTransaction
    """

    def __init__(self, database_uri):
        """
        Establish a connection to the specified *hynet* grid database.

        Parameters
        ----------
        database_uri: str
            URI of the *hynet* grid database.
        """
        # Create an engine and bind it to the metadata and session maker
        self.database_uri = database_uri
        self.engine = create_engine(database_uri)

        Base.metadata.bind = self.engine
        Base.metadata.create_all(self.engine)  # Create tables if they're absent

        self._session_maker = sessionmaker(bind=self.engine)

        # Check database version or, if empty, initialize it
        with DBTransaction(self) as transaction:
            try:
                version = transaction.query(DBInfo).filter(
                    DBInfo.key == DBInfoKey.VERSION).one().value
                if float(version) < float(SCHEMA_VERSION):
                    raise IOError("Deprecated database version '"
                                  + version.value + "' (expected '"
                                  + SCHEMA_VERSION + "' or higher)")
            except NoResultFound:
                transaction.add(DBInfo(key=DBInfoKey.VERSION,
                                       value=SCHEMA_VERSION))
        _log.debug("Connected to database '{:s}'".format(self.database_uri))

    @property
    def empty(self):
        """Return True if the database does not contain grid information."""
        is_empty = True
        with DBTransaction(self) as transaction:
            for table in [DBBus, DBBranch, DBConverter,
                          DBInjector, DBShunt, DBScenario]:
                if transaction.query(table).first() is not None:
                    is_empty = False
                    break
        return is_empty

    @property
    def version(self):
        """Return the *hynet* grid database format version of this database."""
        return self.get_setting(DBInfoKey.VERSION)

    @property
    def grid_name(self):
        """Return the name of the grid in this database."""
        try:
            return self.get_setting(DBInfoKey.GRID_NAME)
        except ValueError:
            return ''

    @grid_name.setter
    def grid_name(self, value):
        """Set the name of the grid in this database."""
        self.set_setting(DBInfoKey.GRID_NAME, value)

    @property
    def description(self):
        """
        Return the description of this database.

        Before the text is returned, the description retrieved from the database
        is wrapped to an appropriate column width to improve readability.
        """
        try:
            description = self.get_setting(DBInfoKey.DESCRIPTION)
            return textwrap.fill(description, width=DESCRIPTION_LINE_LENGTH)
        except ValueError:
            return ''

    @description.setter
    def description(self, value):
        """Set the description of this database."""
        self.set_setting(DBInfoKey.DESCRIPTION, value)

    def get_setting(self, key):
        """
        Return the database setting for the specified key.

        Parameters
        ----------
        key : DBInfoKey
            The key for which the value shall be retrieved.

        Returns
        -------
        value : str
            The value associated with the provided key.

        Raises
        ------
        ValueError
            If the setting was not found.
        """
        with DBTransaction(self) as transaction:
            try:
                setting = transaction.query(DBInfo)\
                            .filter(DBInfo.key == key).one().value
            except NoResultFound:
                raise ValueError("Setting '{:s}' was not found.".format(key))
        return setting

    def set_setting(self, key, value):
        """
        Set the database setting for the specified key.

        Parameters
        ----------
        key : DBInfoKey
            The key for which the value shall be set.
        value : str
            Value to be set.

        Raises
        ------
        ValueError
            If the value is not a string.
        """
        if not isinstance(value, str):
            raise ValueError("The setting value must be a string.")

        with DBTransaction(self) as transaction:
            try:
                setting = transaction.query(DBInfo)\
                            .filter(DBInfo.key == key).one()
            except NoResultFound:
                transaction.add(DBInfo(key=key, value=value))
            else:
                setting.value = value
                transaction.update(setting)

    def start_session(self):
        """
        Return a new database session as an SQLAlchemy Session object.

        **Remark:** This function is for internal use.
        """
        return self._session_maker()


class DBTransaction:
    """
    Database transaction that is automatically committed at the exit block.
    """

    def __init__(self, database):
        """
        Create a database transaction.

        Parameters
        ----------
        database: DBConnection
            Connection to the *hynet* grid database.
        """
        self._session = database.start_session()

    def __enter__(self):
        """
        Initiate the transaction.

        Returns
        -------
        DBTransaction
            ``self``.
        """
        return self

    def __exit__(self, type_, value, traceback):
        """
        Commit the transaction.

        Attempts to commit the current transaction. In case that the commit
        fails, a roll back of the transaction is attempted.

        Parameters
        ----------
        type_ : Exception class or None
            In case of an exception, class of the exception. None otherwise.
        value : Exception instance or None
            In case of an exception, the exception object. None otherwise.
        traceback : object or None
            In case of an exception, object with traceback info. None otherwise.
        """
        if type_ is None:
            self._session.commit()
        else:
            self._session.rollback()
        self._session.close()
        self._session = None
        return False  # In case of an exception, reraise it

    def add(self, object_):
        """Add an object to the session."""
        self._session.add(object_)

    def add_all(self, collection):
        """Add a collection of objects to the session."""
        self._session.add_all(collection)

    def update(self, object_):
        """Update the state of the object in the session."""
        self._session.merge(object_)

    def delete(self, object_):
        """Mark the object as deleted in the session."""
        self._session.delete(object_)

    def delete_all(self, collection):
        """Mark a collection of objects as deleted"""
        for object_ in collection:
            self.delete(object_)

    def query(self, object_type):
        """Return a new SQLAlchemy Query object for this session."""
        return self._session.query(object_type)

    def execute(self, query):
        """Execute the SQL expression construct or string statement."""
        return self._session.execute(query)
