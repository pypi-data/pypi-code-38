import logging
from rockset import Q, F
import rockset.sql as rs
import sqlparse
from .packages.parseutils.meta import FunctionMetadata, ForeignKey
from .encodingutils import unicode2utf8, PY2, utf8tounicode

_logger = logging.getLogger(__name__)


class RSExecute(object):
    def __init__(self, api_server, api_key, workspace, **kwargs):
        self.api_server = api_server
        self.api_key = api_key
        self.workspace = workspace
        self.account = None
        self.username = None
        self.superuser = False
        self.connect()

    def connect(self, api_server=None, api_key=None, workspace=None, **kwargs):
        api_server = (api_server or self.api_server)
        api_key = (api_key or self.api_key)
        workspace = (workspace or self.workspace)
        conn = rs.connect(
            api_server=api_server,
            api_key=api_key,
            workspace=workspace,
            **kwargs
        )
        self.account = ''  # TODO: set this from conn object, post auth
        self.username = ''  # TODO: set this from conn object, post auth
        self.superuser = True  # TODO: set this from conn object, post auth
        cursor = conn.cursor()
        if hasattr(self, 'conn'):
            self.conn.close()
        self.conn = conn
        self.conn.autocommit = True

    def _select_one(self, cur, sql):
        """
        Helper method to run a select and retrieve a single field value
        :param cur: cursor
        :param sql: string
        :return: string
        """
        cur.execute(sql)
        return cur.fetchone()

    def failed_transaction(self):
        return False

    def valid_transaction(self):
        return False

    def run(self, statement, exception_formatter=None, on_error_resume=False):
        """Execute the sql in the database and return the results.

        :param statement: A string containing one or more sql statements
        :param exception_formatter: A callable that accepts an Exception and
               returns a formatted (title, rows, headers, status) tuple that can
               act as a query result.
        :param on_error_resume: Bool. If true, queries following an exception
               (assuming exception_formatter has been supplied) continue to
               execute.

        :return: Generator yielding tuples containing
                 (title, rows, headers, status, query, success)
        """
        # Remove spaces and EOL
        statement = statement.strip()
        if not statement:  # Empty string
            yield (None, None, None, None, statement, False)

        # Split the sql into separate queries and run each one.
        for sql in sqlparse.split(statement):
            # Remove spaces, eol and semi-colons.
            sql = sql.rstrip(';')

            try:
                yield self.execute_normal_sql(sql) + (sql, True)
            except rs.exception.DatabaseError as e:
                _logger.debug("sql: %r, error: %r", sql, e)

                if (self._must_raise(e) or not exception_formatter):
                    raise

                yield None, None, None, exception_formatter(e), sql, False

                if not on_error_resume:
                    break

    def _must_raise(self, e):
        """Return true if e is an error that should not be caught in ``run``.

        ``OperationalError``s are raised for errors that are not under the
        control of the programmer. Usually that means unexpected disconnects,
        which we shouldn't catch; we handle uncaught errors by prompting the
        user to reconnect. We *do* want to catch OperationalErrors caused by a
        lock being unavailable, as reconnecting won't solve that problem.

        :param e: DatabaseError. An exception raised while executing a query.

        :return: Bool. True if ``run`` must raise this exception.

        """
        return isinstance(e, rs.exception.OperationalError)

    def execute_normal_sql(self, split_sql):
        """Returns tuple (title, rows, headers, status)"""
        _logger.debug('Regular sql statement. sql: %r', split_sql)
        cur = self.conn.cursor()
        cur.execute(split_sql)

        title = ''

        # cur.description will be None for operations that do not return
        # rows.
        if cur.description:
            headers = [x[0] for x in cur.description]
            return title, cur, headers, ''
        else:
            _logger.debug('No rows in result.')
            return title, None, None, ''

    def search_path(self):
        """Returns the current search path as a list of schema names"""
        return self.schemata()

    def schemata(self):
        """Returns a list of schema names in the database"""
        return ['commons']

    def _relations(self):
        """Get table or view name metadata
        :return: (schema_name, rel_name) tuples
        """
        try:
            for resource in self.conn._client.list():
                for workspace in self.schemata():
                    yield (workspace, resource.name)
        except:
            return []

    def tables(self):
        """Yields (schema_name, table_name) tuples"""
        for row in self._relations():
            yield row

    def views(self):
        """Yields (schema_name, view_name) tuples.
        """
        return []

    def _columns(self):
        """Get column metadata for tables and views
        :return: list of (schema_name, relation_name, column_name, column_type) tuples
        """
        try:
            for (workspace, collection) in self._relations():
                sql = Q('describe "{}"'.format(collection))
                desc = self.conn._client.sql(sql)
                for d in desc:
                    f = F
                    for dp in d['path']:
                        f = f[dp]
                    yield (workspace, collection, f.sqlexpression(), d['type'], False, None)
        except:
            return []

    def table_columns(self):
        return []

    def view_columns(self):
        return []

    def databases(self):
        return ['rockset']

    def foreignkeys(self):
        return []

    def functions(self):
        return []

    def datatypes(self):
        dtypes = ['int', 'float', 'bool', 'string', 'array', 'document']
        for workspace in self.schemata():
            for dt in dtypes:
                yield (workspace, dt)

    def casing(self):
        """Yields the most common casing for names used in db functions"""
        return
