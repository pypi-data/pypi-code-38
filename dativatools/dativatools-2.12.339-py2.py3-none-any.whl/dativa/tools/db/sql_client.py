import pandas as pd
import logging
import os
import csv
import datetime
from importlib import import_module

logger = logging.getLogger("dativa.tools.sql_client")


class ParamParser:
    """
    Class to parse SQL parameters into a common format
    """

    named_styles = {
        'named': ':{name}',
        'pyformat': '%({name}){type}'
    }

    sequence_styles = {
        'qmark': '?',
        'numeric': ':{index}',
        'format': '%{type}',
    }

    styles = {**named_styles, **sequence_styles}

    index = 0

    def _get_param(self, param):
        self.index = self.index + 1
        return self.styles[self.paramstyle].format(name=param, type="s", sequence=self.index)

    def __init__(self, paramstyle):
        self.paramstyle = paramstyle
        logger.debug("Queries will use paramstyle = {0}".format(paramstyle))
        if paramstyle != 'pyformat':
            logger.warning("The paramstyle {0} has not been tested and may not work".format(paramstyle))

    @staticmethod
    def parse_for_logging(sql, params):

        return sql.format(**params)

    def parse_sql_params(self, sql, params):

        # validate
        try:
            self.parse_for_logging(sql, params)
        except KeyError:
            raise
        except TypeError:
            raise TypeError('params must be a dict, found {}'.format(type(params)))

        if len(params) > 0:
            self.index = 0
            new_sql = ""
            new_params = []
            for segment in sql.replace("'{", "{").replace("}'", "}").replace("{", "}").split("}"):
                if segment in params:
                    new_sql = new_sql + self._get_param(segment)
                    new_params.append(params[segment])
                else:
                    new_sql = new_sql + segment

            if self.paramstyle in self.named_styles:
                return new_sql, params
            else:
                return new_sql, new_params
        else:
            return sql, params


class SqlClient:
    """
    A wrapper for PEP249 connection objects to provide additional logging and simple execution
    of queries and optional writing out of results to DataFrames or CSV

    The client runs mult-statement SQL queries from file or from strings and can return the
    result of the final SQL statement in either a DataFrame or as a CSV

    Parameters:
    - db_connection - a connection object from a PEP249 compliant class
    """

    def __init__(self, db_connection, humour=None):

        self.connection = db_connection
        self.cursor = self.connection.cursor()
        paramstyle = import_module(db_connection.__class__.__module__.split(".")[0]).paramstyle
        self.parser = ParamParser(paramstyle)
        self.humour = humour
        if humour:
            logger.warning('humourous mode engaged, use at own risk')

    def _log_query(self, query, parameters):
        logger.debug("#EXECUTING QUERY @{0}".format(datetime.datetime.now()))
        logger.debug("#PARAMETERS {0}".format(parameters))
        if self.humour == 'bad':
            try:
                import requests
                a = requests.get("https://icanhazdadjoke.com/", headers={"Accept": "application/json"})
                logger.info("#JOKE {0}".format(a.json()['joke']))
            except Exception:  # yes it's broad but i'm really not going to ever care that those 3 lines didn't run correctly
                pass  # probably shouldn't have been doing it anyway.
        i = 1
        for line in query.split("\n"):
            if i < 5:
                logger.debug("{0:03} {1}".format(i, line))
            else:
                logger.debug("{0:03} {1}".format(i, line))
            i = i + 1
        logger.debug("running...")

    @staticmethod
    def _clear_archive(file):
        if file:
            # clear the file
            open(file, 'w').close()

    @staticmethod
    def _archive_query(logged_query, parameters, file):
        logger.debug('logging query to file: {}'.format(file))
        with open(file, 'a+') as f:
            f.write('-- Ran query on: {:%Y-%m-%d %H:%M:%S}\n'.format(datetime.datetime.now()))
            f.write('-- Parameters: {0}\n'.format(parameters))
            f.write(logged_query + ';\n')
        logger.debug('Running...')

    def _report_rowcount(self, execution_time):
        if self.cursor.rowcount >= 0:
            logger.debug("Completed in {0}s. {1} rows affected\n".format(
                execution_time.seconds,
                self.cursor.rowcount))
        else:
            logger.debug("Completed in {0}s\n".format(execution_time.seconds))

    @staticmethod
    def _get_queries(query_file, replace):
        if query_file[-4:] == ".sql":
            if os.path.isfile(query_file):
                logger.debug("Loading query from {0}".format(query_file))
                f = open(query_file, "r")
                text = f.read()
                f.close()
            else:
                logger.error("File {0} does not exist".format(query_file))
                raise OSError("File {0} does not exist".format(query_file))
        else:
            text = query_file

        for key in replace:
            text = text.replace(key, replace[key])

        # split into multiple commands....
        for command in text.split(";"):
            if command.strip() != "":
                yield command.strip()

    def _run_and_log_sql(self, command, parameters, pandas=False, archive_query=False, dry_run=False):

        sql, params = self.parser.parse_sql_params(command, parameters)

        df = None

        if command != '':
            self._log_query(command, parameters)
            if archive_query:
                logged_sql = self.parser.parse_for_logging(command, parameters)
                self._archive_query(logged_sql, parameters, archive_query)
            start_time = datetime.datetime.now()
            if not dry_run:
                if pandas:
                    df = pd.read_sql(sql,
                                     self.connection,
                                     params=params)
                else:
                    self.cursor.execute(sql, params)

                self._report_rowcount(datetime.datetime.now() - start_time)

        return df

    def execute_query(self, query, parameters=None, replace=None, first_to_run=1, archive_query=False, dry_run=False):
        """
        Runs a query and ignores any output

        Parameters:
        - query - the query to run, either a SQL file or a SQL query
        - parameters - a dict of parameters to substitute in the query
        - replace - a dict or items to be replaced in the SQL text
        - first_to_run - the index of the first query in a multi-command query to be executed
        - archive_query - save the query that is run to file. Default=False,

        """
        parameters = dict() if parameters is None else parameters
        replace = dict() if replace is None else replace

        self._clear_archive(archive_query)
        i = 1
        for command in self._get_queries(query, replace):
            if i >= first_to_run:
                logger.debug("RUNNING STATEMENT {0}...".format(i))
                self._run_and_log_sql(command=command,
                                      parameters=parameters,
                                      pandas=False,
                                      archive_query=archive_query,
                                      dry_run=dry_run
                                      )
            i = i + 1

        self.connection.commit()

    def execute_query_to_df(self, query, parameters=None, replace=None, dry_run=False, archive_query=False):
        """
        Runs a query and returns the output of the final statement in a DataFrame.

        Parameters:
        - query - the query to run, either a SQL file or a SQL query
        - parameters - a dict of parameters to substitute in the query
        - replace - a dict or items to be replaced in the SQL text

        """

        parameters = dict() if parameters is None else parameters
        replace = dict() if replace is None else replace
        self._clear_archive(archive_query)

        # create a list of the commands...
        commands = [command for command in self._get_queries(query, replace)]

        # run all but the last one
        for command in commands[:-1]:
            self._run_and_log_sql(command=command,
                                  parameters=parameters,
                                  pandas=False,
                                  dry_run=dry_run,
                                  archive_query=archive_query)

        # now run the last one as a select
        df = self._run_and_log_sql(command=commands[-1],
                                   parameters=parameters,
                                   pandas=True,
                                   dry_run=dry_run,
                                   archive_query=archive_query)

        self.connection.commit()

        if not dry_run and len(df) == 0:
            logger.info("No results returned")
            return pd.DataFrame()
        else:
            return df

    def execute_query_to_csv(self, query, csvfile, parameters=None, replace=None, append=False, archive_query=False,
                             dry_run=False):
        """
        Runs a query and writes the output of the final statement to a CSV file.

        Parameters:
        - query - the query to run, either a SQL file or a SQL query
        - csvfile - the file name to save the query results to
        - parameters - a dict of parameters to substitute in the query
        - replace - a dict or items to be replaced in the SQL text
        """

        parameters = dict() if parameters is None else parameters
        replace = dict() if replace is None else replace

        self._clear_archive(archive_query)

        # run each command in turn
        for command in self._get_queries(query, replace):
            self._run_and_log_sql(command=command,
                                  parameters=parameters,
                                  pandas=False,
                                  archive_query=archive_query,
                                  dry_run=dry_run)
        if not dry_run:
            # delete an existing file if we are not appending
            if os.path.exists(csvfile) and append:
                file_mode = 'a'
            else:
                file_mode = 'w'

            # now get the data
            with open(csvfile, file_mode) as f:
                writer = csv.writer(f, delimiter=',')

                # write the header if we are writing to the beginning of the file
                if file_mode == 'w':
                    writer.writerow([desc[0] for desc in self.cursor.description])

                for row in self.cursor:
                    writer.writerow(row)
