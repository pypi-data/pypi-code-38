''' Generic Database Management functions to perform Database Operation '''

import sys
import psycopg2
import datetime
from .common_utility_tool import CommonUtility
from .log import Logger

class DatabaseManagement(object):

    def __init__(self, path=None, filename=None, logger_obj=None):
        log_obj = Logger()
        if path and filename:
            self.logger_obj = log_obj.__get_logger__(path, filename)
        elif logger_obj:
            self.logger_obj = logger_obj

        self.cu_obj = CommonUtility(logger_obj=self.logger_obj)

    # -------------------------------------------------------------------------
    #    Args: insert_table, scriptfile, dbconntion, source_table, email_config
    #  Raises: Raises exception if some condition is failed.
    #    Desc: This function is used to insert records from staging table to dimention table and fact_table
    # -------------------------------------------------------------------------
    def insert_data(self, insert_table, csv_path, scriptfile, dbconntion, source_table, email_config):
        try:

            self.logger_obj.info(insert_table, 'Start Inserting records in {0} table'.format(insert_table))

            # Find insert query statement #
            tablescriptpath = ('{0}{1}/insert.sql').format(scriptfile, insert_table)

            # Open insert query statement #
            with open(tablescriptpath, 'r') as f:
                sql = f.read()

            # Call ExecuteQuery method to run query #
            self.execute_query(sql, dbconntion, insert_table, 'insert')

            self.logger_obj.info(insert_table, 'Data inserted on table {0} successfully.'.format(insert_table), status="completed")
            self.cu_obj.log_to_csv(csv_path, 'insert', datetime.datetime.utcnow(), 0, insert_table, '')

        except Exception as e:
            self.logger_obj.exception(e.args[0])
            msgexp = self.cu_obj.get_detail_exception()
            self.cu_obj.log_error_to_database(insert_table, 'DatabaseManagementTool', 'insert', 'insert_into_dim', msgexp, dbconntion)
            self.cu_obj.send_email(email_config, 'Reduced', insert_table, 'DatabaseManagementTool', 'insert_into_dim', msgexp)
            raise

    # -------------------------------------------------------------------------
    #    Args: tablename, suffix_schema, dbconn
    #  Raises: Raises exception if some condition is failed.
    #    Desc: This function is used to delete records from staging table
    # -------------------------------------------------------------------------
    def delete_table(self, tablename, suffix_schema, dbconn):
        try:
            self.logger_obj.info(tablename, ('Start deleting records from {0} table into Redshift.').format(tablename))
            # delete query statement #
            sql = ('TRUNCATE TABLE {1}.{0}').format(tablename, suffix_schema)

            # Call ExecuteQuery method to run query #
            self.execute_query(sql, dbconn, tablename, 'delete')
            self.logger_obj.info(tablename, ('Records from table {0} is deleted successfully').format(tablename), status = "completed")

        except Exception as e:
            self.logger_obj.exception(e.args[0])
            msgexp = self.cu_obj.get_detail_exception()
            self.cu_obj.log_error_to_database(tablename, 'DatabaseManagementTool', 'delete', 'deleted_table', msgexp, dbconn)
            raise

    # -------------------------------------------------------------------------
    #    Args: tablename, suffix_schema, dbconntion, s3bucket
    #  Raises: Raises exception if some condition is failed.
    #    Desc: This function is used to create a backup table
    # -------------------------------------------------------------------------
    def backup_table(self, tablename, suffix_schema, suffix_bkp, dbconntion, s3bucket):
        self.logger_obj.info(('Start taking back up table {0} into Redshift.').format(tablename))
        try:
            # back up query statement #
            sql = ('insert INTO {1}.{0}{2} SELECT * FROM {1}.{0}').format(tablename, suffix_schema, suffix_bkp)

            # Call ExecuteQuery method to run query #
            self.execute_query(sql, dbconntion, tablename, 'backup')
            self.logger_obj.info(('table {0} is back up successfully').format(tablename))

        except Exception as e:
            self.logger_obj.exception(e.args[0])
            msgexp = self.cu_obj.get_detail_exception()
            self.cu_obj.log_error_to_database(tablename, 'DatabaseManagementTool', 'backup', 'backup_table', msgexp, dbconntion)
            raise

    # -------------------------------------------------------------------------
    #    Args: tablename, suffix_schema, suffix_ren, dbconntion
    #  Raises: Raises exception if some condition is failed.
    #    Desc: This function is used to rename ardent insightreduce redshift tables
    # -------------------------------------------------------------------------
    def rename_table(self, tablename, suffix_schema, suffix_ren, dbconntion):
        try:
            orgtable = tablename.replace("_deleted", "")
            self.logger_obj.info(('Start Rename table {0} into Redshift.').format(orgtable))
            # rename query statement #
            sql = ('ALTER TABLE {2}.{0} RENAME TO {2}.{0}{1}').format(orgtable, suffix_ren, suffix_schema)

            # Call ExecuteQuery method to run query #
            self.execute_query(sql, dbconntion, orgtable, 'rename')
            self.logger_obj.info(('table {0} is rename successfully').format(orgtable))

        except Exception as e:
            self.logger_obj.exception(e)
            msgexp = self.cu_obj.get_detail_exception()
            self.cu_obj.log_error_to_database(orgtable, 'DatabaseManagementTool', 'rename', 'rename_table', msgexp, dbconntion)
            raise

    # -------------------------------------------------------------------------
    #    Args: tablename, suffix_schema, dbconntion
    #  Raises: Raises exception if some condition is failed.
    #    Desc: This function is used to drop ardent insightreduce redshift tables
    # -------------------------------------------------------------------------
    def drop_table(self, tablename, suffix_schema, dbconntion):
        self.logger_obj.info(('Start droping {0} table from Redshift.').format(tablename))
        try:
            # drop query statement #
            sql = ('DROP TABLE IF EXISTS {1}.{0}').format(tablename, suffix_schema)

            # Call ExecuteQuery method to run query #
            self.execute_query(sql, dbconntion, tablename, 'drop')
            self.logger_obj.info(('Table {0} is dropped successfully').format(tablename))

        except Exception as e:
            self.logger_obj.exception(e)
            msgexp = self.cu_obj.get_detail_exception()
            self.cu_obj.log_error_to_database(tablename, 'DatabaseManagementTool', 'drop', 'drop_table', msgexp, dbconntion)
            raise

    # -------------------------------------------------------------------------
    #    Args: tablename, scriptfile, dbconntion
    #  Raises: Raises exception if some condition is failed.
    #    Desc: This function is used to create tables of ardent insightreduce redshift tables
    # -------------------------------------------------------------------------
    def create_table(self, tablename, scriptfile, dbconntion):
        self.logger_obj.info(('Start Creating {0} table into Redshift.').format(tablename))
        try:
            # Find create query statement #
            tablescriptpath = ('{0}{1}/create.sql').format(scriptfile, tablename)

            # Open create query statement #
            with open(tablescriptpath, 'r') as f:
                sql = f.read()

            # Call ExecuteQuery method to run query #
            self.execute_query(sql, dbconntion, tablename, 'create')
            self.logger_obj.info(('table {0} is created successfully').format(tablename))

        except Exception as e:
            self.logger_obj.exception(e)
            msgexp = self.cu_obj.get_detail_exception()
            self.cu_obj.log_error_to_database(tablename, 'DatabaseManagementTool', 'create', 'create_table', msgexp, dbconntion)
            raise

    # -------------------------------------------------------------------------
    #    Args: sql, dbconn, tablename, methodtype
    # Returns: copycount and unloadcount
    #  Raises: Raises exception if some condition is failed.
    #    Desc: This function is used to execute sql queries
    # -------------------------------------------------------------------------
    def execute_query(self, sql, dbconn, tablename, methodtype):
        try:
            # Connection to connect ardent database #
            con = psycopg2.connect(dbname=dbconn['database'], host=dbconn['host'], port=dbconn['port'], user=dbconn['user'], password=dbconn['password'])
            if methodtype in ["copy", "unload"]:
                cur = con.cursor()
                cur.execute(sql)
                rows = cur.fetchone()[0]
                con.commit()
                con.close()
                return rows
            else:
                cur = con.cursor()
                cur.execute(sql)
                con.commit()
            cur.close()
            con.close()

        except psycopg2.OperationalError as err:
            self.logger_obj.exception(err)
            self.execute_query(sql, dbconn, tablename, methodtype)
            return
        except Exception as e:
            self.logger_obj.exception(e.args[0])
            msgexp = self.cu_obj.get_detail_exception()
            self.cu_obj.log_error_to_database(tablename, 'DatabaseManagementTool', 'execute', 'execute_query', msgexp, dbconn)
            raise
