import sys
import datetime
import inspect
import time
from salure_helpers import MySQL
from salure_helpers.salure_functions import SalureFunctions
import warnings


class TaskScheduler(object):

    def __init__(self, host, user, password, database, task_id, loglevel='INFO'):
        """
        The TaskScheduler is responsible for the logging to the database. Based on this logging, the next reload will
        start or not and warning will be given or not
        :param host: The MySQL host of the customer database
        :param user: MySQL user of the customer
        :param password: MySQL password of the customer
        :param database: the customer database
        :param task_id: The ID from the task as saved in the task_scheduler table in the customer database
        :param loglevel: Chose on which level you want to store the logs. Default is INFO. that means that a logline
        with level DEBUG not is stored
        """
        self.mysql = MySQL(host, user, password, database)
        self.task_id = task_id
        self.loglevel = loglevel
        self.run_id = int(round(time.time() * 100000))
        self.started_at = datetime.datetime.now()
        self.error_count = 0

        # Check if the log tables exists in the customer database. If not, create them
        # Mysql throws a warning when a table already exists. We don't care so we ignore warnings. (not exceptions!)
        warnings.filterwarnings('ignore')
        self.check_if_logging_tables_exists()

        # Start the task and setup the data in the database
        self.start_task()


    def check_if_logging_tables_exists(self):
        """
        This function checks if all the needed tables for the task_scheduler exists. If they don't, this function
        creates the needed tables
        :return: nothing
        """
        # Check if the table task_scheduler exists. If not, create it
        new_table_query = 'CREATE TABLE IF NOT EXISTS `task_scheduler` (' \
                          '`id`                 int(11)         NOT NULL AUTO_INCREMENT,' \
                          '`docker_image`       varchar(255)    DEFAULT NULL,' \
                          '`runfile_path`       varchar(255)    DEFAULT NULL,' \
                          '`next_reload`        timestamp       NULL DEFAULT NULL,' \
                          '`frequency`          varchar(255)    DEFAULT \'{"month":0,"day":1,"hour":0,"minute":0}\',' \
                          '`last_reload`        timestamp       NULL DEFAULT NULL,' \
                          '`last_error_message` varchar(255)    DEFAULT NULL,' \
                          '`status`             varchar(255)    DEFAULT \'IDLE\',' \
                          '`disabled`           tinyint(4)      DEFAULT \'1\',' \
                          '`run_instant`        tinyint(1)      DEFAULT \'0\',' \
                          'sftp_mapping         varchar(255)    NOT NULL DEFAULT \'[]\',' \
                          'PRIMARY KEY (`id`),' \
                          'UNIQUE KEY `task_scheduler_id_uindex` (`id`)' \
                          ') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci'
        self.mysql.raw_query(new_table_query)

        # Check if the table task_scheduler_log exists. If not, create it
        new_table_query = 'CREATE TABLE IF NOT EXISTS `task_scheduler_log` (' \
                          '`reload_id`      bigint          NOT NULL,' \
                          '`task_id`        int             NULL,' \
                          '`reload_status`  varchar(255)    NULL,' \
                          '`started_at`     datetime        NULL,' \
                          '`finished_at`    datetime        NULL)'
        self.mysql.raw_query(new_table_query)

        # Check if the table check_task_execution_log exists. If not, create it
        new_table_query = 'CREATE TABLE IF NOT EXISTS `task_execution_log`(' \
                          '`reload_id`   bigint       NOT NULL,' \
                          '`task_id`     int          NULL,' \
                          '`log_level`   varchar(255) NULL,' \
                          '`created_at`  datetime     NULL,' \
                          '`line_number` int          NULL,' \
                          '`message`     varchar(255) NULL);'
        self.mysql.raw_query(new_table_query)


    def start_task(self):
        """
        Start the task and write this to the database. While the status is running, the task will not start again
        :return: if the update to the database is successful or not
        """
        return self.mysql.update('task_scheduler', ['status'], ['RUNNING'], 'WHERE `id` = {}'.format(self.task_id))


    def write_execution_log(self, message: str, loglevel='INFO'):
        """
        Writes messages to the database. Give the message and the level of the log
        :param message: A string with a message for the log
        :param loglevel: You can choose between DEBUG, INFO, ERROR or CRITICAL (DEBUG is most granulated, CRITICAL the less)
        :return: If the write to the database is successful or not
        """
        allowed_loglevels = ['DEBUG', 'INFO', 'ERROR', 'CRITICAL']
        if loglevel not in allowed_loglevels:
            raise Exception('You\'ve entered a not allowed loglevel. Choose one of: {}'.format(allowed_loglevels))
        else:
            # Get the linenumber from where the logline is executed. Get the stacktrace of this action, jump 1 file up and pick then the linenumber (second item)
            linenumber = inspect.getouterframes(inspect.currentframe())[1][2]
            # Write the logline to the database, depends on the chosen loglevel in the task
            print('{} at line: {}'.format(message, linenumber))
            if self.loglevel == 'DEBUG':
                return self.mysql.raw_query("INSERT INTO `task_execution_log` VALUES ({}, {}, '{}', '{}', {}, '{}')".format(self.run_id, self.task_id, loglevel, datetime.datetime.now(), linenumber, message), insert=True)
            elif self.loglevel == 'INFO' and (loglevel == 'INFO' or loglevel == 'ERROR' or loglevel == 'CRITICAL'):
                return self.mysql.raw_query("INSERT INTO `task_execution_log` VALUES ({}, {}, '{}', '{}', {}, '{}')".format(self.run_id, self.task_id, loglevel, datetime.datetime.now(), linenumber, message), insert=True)
            elif self.loglevel == 'ERROR' and (loglevel == 'ERROR' or loglevel == 'CRITICAL'):
                return self.mysql.raw_query("INSERT INTO `task_execution_log` VALUES ({}, {}, '{}', '{}', {}, '{}')".format(self.run_id, self.task_id, loglevel, datetime.datetime.now(), linenumber, message), insert=True)
            elif self.loglevel == 'CRITICAL' and loglevel == 'CRITICAL':
                return self.mysql.raw_query("INSERT INTO `task_execution_log` VALUES ({}, {}, '{}', '{}', {}, '{}')".format(self.run_id, self.task_id, loglevel, datetime.datetime.now(), linenumber, message), insert=True)


    def error_handling(self,e: Exception, breaking=True):
        """
        This function handles errors that occur in the scheduler. Logs the traceback, updates run statuses and notifies users
        :param e: the Exception that is to be handled
        :param task_id: The scheduler task id
        :param mysql_con: The connection which is used to update the scheduler task status
        :param logger: The logger that is used to write the logging status to
        :param breaking: Determines if the error is breaking or code will continue
        :param started_at: Give the time the task is started
        :return: nothing
        """
        # Format error to a somewhat readable format
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error = str(e)[:400].replace('\'', '').replace('\"', '') + ' | Line: {}'.format(exc_tb.tb_lineno)
        # Get scheduler task details for logging
        task_details = self.mysql.select('task_scheduler', 'docker_image, runfile_path', 'WHERE id = {}'.format(self.task_id))[0]
        taskname = task_details[0]
        customer = task_details[1].split('/')[-1].split('.')[0]

        if breaking:
            # Set scheduler status to failed
            self.mysql.update('task_scheduler', ['status', 'last_reload', 'last_error_message'],
                              ['IDLE', datetime.datetime.now(), 'Failed'],
                              'WHERE `id` = {}'.format(self.task_id))
            # Log to database
            self.mysql.raw_query(
                "INSERT INTO `task_execution_log` VALUES ({}, {}, 'CRITICAL', '{}', {}, '{}')".format(self.run_id, self.task_id,
                                                                                                      datetime.datetime.now(),
                                                                                                      exc_tb.tb_lineno,
                                                                                                      error),
                insert=True)
            self.mysql.raw_query(
                "INSERT INTO `task_scheduler_log` VALUES ({}, {}, 'Failed', '{}', '{}')".format(self.run_id, self.task_id,
                                                                                                self.started_at,
                                                                                                datetime.datetime.now()),
                insert=True)
            # Notify users on Slack
            SalureFunctions.send_error_to_slack(customer, taskname, 'failed')
            raise Exception(error)
        else:
            self.mysql.raw_query(
                "INSERT INTO `task_execution_log` VALUES ({}, {}, 'CRITICAL', '{}', {}, '{}')".format(self.run_id, self.task_id,
                                                                                                      datetime.datetime.now(),
                                                                                                      exc_tb.tb_lineno,
                                                                                                      error),
                insert=True)
            SalureFunctions.send_error_to_slack(customer, taskname, 'contains an error')

        self.error_count += 1


    def finish_task(self, reload_instant=False):
        """
        At the end of the script, write the outcome to the database. Write if the task is finished with or without errors,
        Also clean up the execution_log table when the number of lines is more than 1000
        :return:
        """
        # If reload instant is true, this adds an extra field 'run_instant' to the update query, and sets the value to 1. This makes the task reload immediately after it's finished
        field = ['run_instant', 'next_reload'] if reload_instant else []
        value = ['1', datetime.datetime.now()] if reload_instant else []
        if self.error_count > 0:
            self.mysql.update('task_scheduler', ['status', 'last_reload', 'last_error_message'],
                         ['IDLE', datetime.datetime.now(), 'FinishedFail'],
                         'WHERE `id` = {}'.format(self.task_id))
            self.mysql.raw_query(
                "INSERT INTO `task_scheduler_log` VALUES ({}, {}, 'FinishedFail', '{}', '{}')".format(self.run_id, self.task_id, self.started_at, datetime.datetime.now()), insert=True)
        else:
            self.mysql.update('task_scheduler', ['status', 'last_reload', 'last_error_message'] + field,
                         ['IDLE', datetime.datetime.now(), 'FinishedSucces'] + value,
                         'WHERE `id` = {}'.format(self.task_id))
            self.mysql.raw_query(
                "INSERT INTO `task_scheduler_log` VALUES ({}, {}, 'FinishedSuccess', '{}', '{}')".format(self.run_id, self.task_id, self.started_at, datetime.datetime.now()), insert=True)
            # Clean up execution log
        self.mysql.delete("task_execution_log",
                     "WHERE task_id = {} AND reload_id NOT IN (SELECT reload_id FROM (SELECT reload_id FROM `task_execution_log` ORDER BY created_at DESC LIMIT 1000) temp)".format(
                         self.task_id))
