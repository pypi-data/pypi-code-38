"""
Holds a replica of the MySQL object from the old dynamo
"""

import sys
import logging
# I don't know why this is not importing for Python 2.6 on Travis
import MySQLdb # pylint: disable=import-error


LOG = logging.getLogger(__name__)


class MySQL(object):
    """
    Some "convenience" wrapper for MySQLdb.
    Try to rewrite so that this isn't used.
    """

    def __init__(self, host='', user='', passwd='', config_file='', config_group='', db=''):
        self._connection_parameters = {}
        if config_file:
            self._connection_parameters['read_default_file'] = config_file
            self._connection_parameters['read_default_group'] = config_group
        if host:
            self._connection_parameters['host'] = host
        if user:
            self._connection_parameters['user'] = user
        if passwd:
            self._connection_parameters['passwd'] = passwd
        if db:
            self._connection_parameters['db'] = db

        self._connection = MySQLdb.connect(**self._connection_parameters)

    def close(self):
        """Close the database. Needs to be called by the process that built this object."""
        self._connection.close()

    def query(self, sql, *args):
        """
        :param str sql: The SQL query to execute
        :param args: Used to fill the SQL query
        :returns: If the query is an INSERT, return the inserted row id
                  (0 if no insertion happened).
                  If the query is a SELECT, return an array of::

                    - tuples if multiple columns are called
                    - values if one column is called

        :rtype: str, int, or list of tuples
        """

        cursor = self._connection.cursor()

        if LOG.getEffectiveLevel() == logging.DEBUG:
            if not args:
                LOG.debug(sql)
            else:
                LOG.debug(sql + ' % ' + str(args))

        try:
            for _ in range(10):
                try:
                    cursor.execute(sql, args)
                    break
                except MySQLdb.OperationalError: # pylint: disable=c-extension-no-member
                    LOG.error(str(sys.exc_info()[1]))
                    last_except = sys.exc_info()[1]
                    # reconnect to server
                    cursor.close()
                    self._connection = MySQLdb.connect(**self._connection_parameters)
                    cursor = self._connection.cursor()

            else: # 10 failures
                LOG.error('Too many OperationalErrors. Last exception:')
                raise last_except

        except:
            LOG.error('There was an error executing the following statement:')
            LOG.error(sql[:10000])
            LOG.error(sys.exc_info()[1])
            raise

        result = cursor.fetchall()

        if cursor.description is None:
            # insert query
            return cursor.lastrowid if cursor.lastrowid != 0 else cursor.rowcount

        elif result and len(result[0]) == 1:
            # single column requested
            return [row[0] for row in result]

        return list(result)
