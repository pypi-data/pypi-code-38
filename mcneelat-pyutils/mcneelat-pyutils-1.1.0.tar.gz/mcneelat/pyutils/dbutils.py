from mcneelat.pyutils.confutils import AbstractLogUtils
import psycopg2


class AbstractDBUtils(AbstractLogUtils):
    """Class containing handy methods common to working with any SQL database."""

    def __init__(self, dbconn, verbose=True):
        """
        Initialize class.
        :param dbconn: database connection object
        """
        self.dbconn = dbconn
        self.verbose = verbose
        self.cursor = self.dbconn.cursor()
        AbstractLogUtils.__init__(self, verbose)

    def select(self, sql):
        """
        Execute a SQL SELECT statement.
        :param sql: SQL SELECT statement
        :return: results of executed statement
        """
        results = []
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        while row is not None:
            results.append(row)
            row = self.cursor.fetchone()
        return results

    def runsql(self, sql, commit=True):
        """
        Execute a SQL statement of any type that doesn't require a result (i.e. not SELECT).
        :param sql: SQL statement to execute
        :param commit: whether or not to commit any changes made by the statement
        :return: None
        """
        self.cursor.execute(sql)
        if commit:
            self.dbconn.commit()

    def runsqlmulti(self, sql):
        """
        Execute multiple SQL statements as a batch.
        :param sql: SQL statement to execute
        :return: None
        """
        for s in sql:
            self.runsql(s, False)
        self.dbconn.commit()

    def close(self):
        """
        Close and database resources.
        :return: None
        """
        self.log("[*] Closing database connection...")
        self.cursor.close()
        self.dbconn.close()


class PGUtils(AbstractDBUtils):
    """Class to initialize a connection to a PostgreSQL database."""

    def __init__(self, conf_data, schema=None, verbose=True):
        """
        Initialize class.
        :param conf_data: configuration data to initialize database
        :param schema: database schema location
        """
        self.conf_data = conf_data
        self.schema = schema
        if verbose:
            print("[*] Connecting to database...")
        dbconn = psycopg2.connect(**conf_data["DB_CONN_INFO"])
        AbstractDBUtils.__init__(self, dbconn, verbose)
