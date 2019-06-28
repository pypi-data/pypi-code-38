import logging
import os
import csv
import datetime
from importlib import import_module

try:
    import pandas as pd
except ImportError:
    pd = None

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

    def __init__(self, paramstyle, logger):
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

    def __init__(self,
                 db_connection,
                 humour=None,
                 logging_level=logging.DEBUG,
                 log_query_text=False,
                 logger=logging.getLogger("dativa.tools.sql_client")):

        self._logger = logger
        self.connection = db_connection
        self.cursor = self.connection.cursor()
        paramstyle = import_module(db_connection.__class__.__module__.split(".")[0]).paramstyle
        self.parser = ParamParser(paramstyle, self._logger)
        self.logging_level = logging_level
        self.humour = humour
        if humour:
            self._logger.warning('humourous mode engaged, use at own risk')
        self._counter = 0
        self._log_query_text = log_query_text


    @staticmethod
    def _clean_dict(d):
        block_words = ["secret", "password"]
        clean = {}
        for param in d:
            if any(x.lower() in param.lower() for x in block_words):
                clean[param] = "*" * len(d[param])
            else:
                clean[param] = d[param]

        return clean

    def _log_query(self, query, parameters):
        self._logger.log(self.logging_level, "Executing part {0}: {1}".format(self._counter, query.split("\n")[0]))
        self._logger.debug("Parameters {0}".format(self._clean_dict(parameters)))
        if self.humour == 'bad':
            try:
                import requests
                a = requests.get("https://icanhazdadjoke.com/", headers={"Accept": "application/json"})
                self._logger.info("#JOKE {0}".format(a.json()['joke']))
            except Exception:  # yes it's broad but i'm really don't care that those 3 lines didn't run correctly
                pass  # probably shouldn't have been doing it anyway.

        if self._log_query_text:
            for line in query.split("\n"):
                self._logger.log(self.logging_level, "{0:03} {1}".format(i, line))

    def _clear_archive(self, file):
        if file:
            if not os.path.exists(os.path.dirname(file)):
                os.makedirs(os.path.dirname(file))
            # clear the file
            open(file, 'w').close()
            self._logger.log(self.logging_level, 'logging query to file: {}'.format(file))

    def _archive_query(self, logged_query, parameters, file):
        with open(file, 'a+') as f:
            f.write('-- Ran query on: {:%Y-%m-%d %H:%M:%S}\n'.format(datetime.datetime.now()))
            f.write('-- Parameters: {0}\n'.format(self._clean_dict(parameters)))
            f.write(logged_query + ';\n')

    def _report_rowcount(self, execution_time):
        if self.cursor.rowcount >= 0:
            self._logger.log(self.logging_level, "Completed in {0}s. {1} rows affected".format(
                execution_time.seconds,
                self.cursor.rowcount))
        else:
            self._logger.log(self.logging_level, "Completed in {0}s".format(execution_time.seconds))

    def _get_queries(self, query_file, replace):
        if query_file[-4:] == ".sql":
            if os.path.isfile(query_file):
                self._logger.log(self.logging_level, "Loading query from {0}".format(query_file))
                f = open(query_file, "r")
                text = f.read()
                f.close()
            else:
                self._logger.error("File {0} does not exist".format(query_file))
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
                    if not pd:
                        raise ImportError("pandas is not installed. Please install pandas and try again")
                    df = pd.read_sql(sql,
                                     self.connection,
                                     params=params)
                else:
                    self.cursor.execute(sql, params)

                self._report_rowcount(datetime.datetime.now() - start_time)

        return df

    def _reset_counter(self):
        self._counter = 1

    def _increment_counter(self):
        self._counter = self._counter + 1

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
        self._reset_counter()
        for command in self._get_queries(query, replace):
            if self._counter >= first_to_run:
                self._run_and_log_sql(command=command,
                                      parameters=parameters,
                                      pandas=False,
                                      archive_query=archive_query,
                                      dry_run=dry_run
                                      )
            self._increment_counter()

        self.connection.commit()

    def execute_query_to_df(self, query, parameters=None, replace=None, first_to_run=1, dry_run=False, archive_query=False):
        """
        Runs a query and returns the output of the final statement in a DataFrame.

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

        # create a list of the commands...
        commands = [command for command in self._get_queries(query, replace)]

        # run all but the last one
        self._reset_counter()
        for command in commands[:-1]:
            if self._counter >= first_to_run:
                self._run_and_log_sql(command=command,
                                      parameters=parameters,
                                      pandas=False,
                                      dry_run=dry_run,
                                      archive_query=archive_query)
            self._increment_counter()

        # now run the last one as a select
        df = self._run_and_log_sql(command=commands[-1],
                                   parameters=parameters,
                                   pandas=True,
                                   dry_run=dry_run,
                                   archive_query=archive_query)

        self.connection.commit()

        if not dry_run and len(df) == 0:
            self._logger.info("No results returned")
            return pd.DataFrame()
        else:
            return df

    def execute_query_to_csv(self,
                             query,
                             csvfile,
                             parameters=None,
                             replace=None,
                             append=False,
                             first_to_run=1,
                             archive_query=False,
                             dry_run=False):
        """
        Runs a query and writes the output of the final statement to a CSV file.

        Parameters:
        - query - the query to run, either a SQL file or a SQL query
        - csvfile - the file name to save the query results to
        - parameters - a dict of parameters to substitute in the query
        - replace - a dict or items to be replaced in the SQL text
        - first_to_run - the index of the first query in a multi-command query to be executed
        """

        parameters = dict() if parameters is None else parameters
        replace = dict() if replace is None else replace

        self._clear_archive(archive_query)

        # run each command in turn
        self._reset_counter()
        for command in self._get_queries(query, replace):
            if self._counter >= first_to_run:
                self._run_and_log_sql(command=command,
                                      parameters=parameters,
                                      pandas=False,
                                      archive_query=archive_query,
                                      dry_run=dry_run)
            self._increment_counter()

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
