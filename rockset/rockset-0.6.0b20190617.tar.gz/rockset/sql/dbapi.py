"""DB-API implementation backed by Rockset

See http://www.python.org/dev/peps/pep-0249/

TODO:
- Handle DATE, TIME, INTERVAL (etc) data types

"""
from rockset import Client
from rockset.query import QueryStringSQLText
from rockset.sql.exception import *
import rockset

import collections

#
# Global constants
#
# supported DBAPI level
apilevel = '2.0'
# Python extended format codes, e.g. ...WHERE name=%(name)s
paramstyle = 'named'
# Threads may share the module and connections.
threadsafety = 2


def connect(*args, **kwargs):
    """Constructor for creating a connection to Rockset. Any argument that you
    pass to create a Rockset Client_ can be passed here.

    :returns: a :py:class:`Connection` object.
    """
    return Connection(*args, **kwargs)


class Connection(object):
    """Setup a Rockset Client handle
    """

    def __init__(self, *args, **kwargs):
        try:
            self._client = Client(*args, **kwargs)
            self._client.list()
        except rockset.exception.Error as e:
            raise Error.from_rockset_exception(e)

    def close(self):
        pass

    def commit(self):
        pass

    def rollback(self):
        raise NotSupportedError("Rockset does not support transactions")

    def cursor(self, cursor_type=None):
        if cursor_type is None:
            cursor_type = Cursor
        elif not issubclass(cursor_type, Cursor):
            raise ValueError('{} is not a valid cursor type'.format(cursor_type))
        return cursor_type(conn=self, client=self._client)


class Cursor(object):
    """These objects represent a database cursor, which is used to manage the
    context of a fetch operation. Cursors created from the same connection are
    not isolated, i.e., any changes done to the database by a cursor are
    immediately visible by the other cursors.
    """
    def __init__(self, conn, client):
        """DBAPI Cursor
        """
        self._conn = conn
        self._client = client
        self._arraysize = 1

        # number of records to fetch for auto pagination
        self._iter_batchsize = 10000
        self._reset()

    def _reset(self):
        """Reset state of the Cursor back to empty"""
        self._cursor = None
        self._cursor_iter = None
        self._schema = {}
        self._fields = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _get_fields(self):
        # nothing to do if no queries have been executed yet
        if self._cursor is None:
            return None

        # TODO: come up with a better way to do this
        # get all results and infer schema from them
        try:
            results = self._cursor.results()
        except rockset.exception.Error as e:
            raise Error.from_rockset_exception(e)

        # build a row with all possible fields, by merging all into one
        for r in results:
            self._schema.update(r)

        # make a list of fields and types, and return
        self._fields = [(k, type(self._schema[k]).__name__)
            for k in sorted(self._schema)]

        return self._fields

    @property
    def description(self):
        """This read-only attribute is a sequence of 7-item sequences.

        Each of these sequences contains information describing one result
        column:
            name
            type_code
            display_size (optional, always None for now)
            internal_size (optional, always None for now)
            precision (optional, always None for now)
            scale (optional, always None for now)
            null_ok (optional, always True for now)

        The first two items (name and type_code) are mandatory, the other
        five are optional and are set to None if no meaningful values can be
        provided.

        This attribute will be None for operations that do not return rows or
        if the cursor has not had an operation invoked via the .execute*()
        method yet.

        The type_code can be interpreted by comparing it to the Type Objects
        specified in the section below.
        """
        if self._cursor is None:
            return None

        return [
            # name, type_code, display_size, internal_size, precision, scale,
            # null_ok
            (f, t, None, None, None, None,
                (f != '_id')) for (f, t) in self._get_fields()
        ]

    @property
    def rowcount(self):
        return -1

    def close(self):
        """Close the cursor now (rather than whenever __del__ is called).

        The cursor will be unusable from this point forward; an Error (or
        subclass) exception will be raised if any operation is attempted with
        the cursor.
        """
        self._reset()

    def execute(self, operation, parameters=None):
        """Prepare and execute a database operation (query or command).
        Parameters may be provided as sequence or mapping and will be bound to
        variables in the operation. Variables are specified in ``pyformat``
        notation.

        Return values are not defined.
        """
        q = QueryStringSQLText(operation)
        if parameters:
            if not isinstance(parameters, dict):
                raise ProgrammingError("Unsupported type for query parameters: "
                    "expected: `dict` found: `{}`".format(type(parameters)))
            q.P.update(parameters)

        # setup the cursor
        self._cursor = self._client.sql(q=q)
        # setup an iterator to fetch results
        self._cursor_iter = iter(self._cursor.results())

    def executemany(operation, seq_of_parameters):
        """Prepare a database operation (query or command) and then execute it
        against all parameter sequences or mappings found in the sequence
        ``seq_of_parameters``.

        Only the final result set is retained.

        Return values are not defined.
        """
        for parameters in seq_of_parameters:
            self.execute(operation, parameters)

    def _fetchonedoc(self):
        if self._cursor is None:
            raise ProgrammingError(message='no query has been executed yet')
        try:
            one = next(self._cursor_iter)
        except StopIteration:
            return None
        except rockset.exception.Error as e:
            raise Error.from_rockset_exception(e)
        return one

    def fetchone(self):
        """Fetch the next row of a query result set, returning a single
        sequence, or None when no more data is available.

        An Error (or subclass) exception is raised if the previous call to
        .execute*() did not produce any result set or no call was issued yet.
        """
        one = self._fetchonedoc()
        if one is None:
            return None
        r = []
        for (f, t) in self._get_fields():
            if f in one:
                r.append(one[f])
            else:
                r.append(None)
        return tuple(r)

    def fetchmany(self, size=None):
        """Fetch the next set of rows of a query result, returning a sequence
        of sequences (e.g. a list of tuples). An empty sequence is returned
        when no more rows are available.

        The number of rows to fetch per call is specified by the parameter. If
        it is not given, the cursor's arraysize determines the number of rows
        to be fetched. The method should try to fetch as many rows as indicated
        by the size parameter. If this is not possible due to the
        specified number of rows not being available, fewer rows may be
        returned.

        An Error (or subclass) exception is raised if the previous call to
        .execute*() did not produce any result set or no call was issued yet.
        """
        if size is None:
            size = self.arraysize
        result = []
        for _ in range(size):
            one = self.fetchone()
            if one is None:
                break
            else:
                result.append(one)
        return result

    def fetchall(self):
        """Fetch all (remaining) rows of a query result, returning them as a
        sequence of sequences (e.g. a list of tuples).

        An Error (or subclass) exception is raised if the previous call to
        .execute*() did not produce any result set or no call was issued yet.
        """
        result = []
        while True:
            one = self.fetchone()
            if one is None:
                break
            else:
                result.append(one)
        return result

    @property
    def arraysize(self):
        """This read/write attribute specifies the number of rows to fetch at a
        time with .fetchmany(). It defaults to 1 meaning to fetch a single row
        at a time.
        """
        return self._arraysize

    @arraysize.setter
    def arraysize(self, value):
        self._arraysize = value

    def setinputsizes(self, sizes):
        pass

    def setoutputsize(self, size, column=None):
        pass

    # Optional DB-API Extensions
    @property
    def connection(self):
        return self._conn

    def __next__(self):
        """Return the next row from the currently executing SQL statement using
        the same semantics as .fetchone(). A ``StopIteration`` exception is
        raised when the result set is exhausted.
        """
        one = self.fetchone()
        if one is None:
            raise StopIteration
        else:
            return one

    next = __next__

    def __iter__(self):
        """Return self to make cursors compatible to the iteration protocol."""
        return self

class DictCursor(Cursor):
    def fetchone(self):
        return self._fetchonedoc()

#
# Type Objects
# See https://www.python.org/dev/peps/pep-0249/#implementation-hints-for-module-authors
#
class _DBAPITypeObject:
    def __init__(self, *values):
        self.values = values

    def __cmp__(self, other):
        if other in self.values:
            return 0
        if other < self.values:
            return 1
        else:
            return -1

Binary = str
STRING = _DBAPITypeObject(['string'])
BINARY = _DBAPITypeObject(['object', 'array'])
NUMBER = _DBAPITypeObject(['int', 'float'])
DATETIME = _DBAPITypeObject('date', 'time', 'timestamp', 'datetime')
ROWID = _DBAPITypeObject()
BOOL = _DBAPITypeObject(['bool'])
