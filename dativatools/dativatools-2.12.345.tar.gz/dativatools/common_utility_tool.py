''' Generic Common Utility functions to perform Common Notification Operation '''

import sys
import smtplib
import email
import email.utils
import os
import time
import psycopg2
import csv
import datetime
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .log import Logger


class CommonUtility(object):

    def __init__(self, path=None, filename=None, logger_obj=None):
        if path and filename:
            log_obj = Logger()
            self.logger_obj = log_obj.__get_logger__(path, filename)
        elif logger_obj:
            self.logger_obj = logger_obj
    # -------------------------------------------------------------------------
    # Returns: Error Message in Details
    #  Raises: Raises exception if some condition is failed.
    #    Desc: This function is used to get details description about any exception at the time of execution
    # -------------------------------------------------------------------------
    def get_detail_exception(self):
        return str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + ' Line:' + str(sys.exc_info()[2].tb_lineno)

    # -------------------------------------------------------------------------
    #    Args: csv_path, action, insert_time, record_count, table_name, filename
    #  Raises: Raises exception if some condition is failed.
    #    Desc: This function is to log activity performed into CSV file
    # -------------------------------------------------------------------------
    def log_to_csv(self, csv_path, action, insert_time, record_count, table_name, filename):
        data = [action, insert_time, record_count, table_name, filename]
        if not os.path.exists(os.path.join(csv_path, 'csv')):
            os.makedirs(os.path.join(csv_path, 'csv'))
        f = open(os.path.join(csv_path, 'csv', datetime.datetime.utcnow().strftime('activity_%Y-%m-%d.csv')), 'a')
        w = csv.writer(f, delimiter=',', lineterminator='\n')
        w.writerow(data)
        f.close()

    # -------------------------------------------------------------------------
    #    Args: csv_path, action, insert_time, record_count, table_name, filename
    #  Raises: Raises exception if some condition is failed.
    #    Desc: This function is used to log error generated during execution into the database table error_log_table
    # -------------------------------------------------------------------------
    def log_error_to_database(self, tablename, script_name, Type, function_name, error_msg, dbconntion):
        try:
            self.logger_obj.info('', 'Logging error detail into database table error_log_table.')
            con = psycopg2.connect(dbname=dbconntion['database'], host=dbconntion['host'], port=dbconntion['port'], user=dbconntion['user'], password=dbconntion['password'])
            sql = "INSERT INTO etl.error_log_table (tablename, script_name, Type,function_name, error_msg) VALUES (%s, %s, %s, %s, %s)"
            data = (tablename, script_name, Type, function_name, error_msg)
            cur = con.cursor()
            cur.execute(sql, data)
            con.commit()
            cur.close()
            con.close()
            self.logger_obj.info('', 'Logging error detail into database table error_log_table completed.')
        except Exception as e:
            self.logger_obj.exception(e.args[0])
            raise

    # -------------------------------------------------------------------------
    #    Args: email_config, job_type, table, script_name, function_name, err_msg
    #  Raises: Raises exception if some condition is failed.
    #    Desc: This function checks exporter importer job and if job interupted then trigger email
    # -------------------------------------------------------------------------
    def send_email(self, email_config, job_type, table, script_name, function_name, err_msg):
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = ('{0} : {1}').format(email_config['subject'], job_type)
            msg['From'] = email_config['send_from']
            msg['To'] = email_config['send_to']
            msg['cc'] = email_config['cc']
            utc_from_epoch = time.time()
            msg['Date'] = email.utils.formatdate(utc_from_epoch, localtime=True)

            message = ("Following are the details for job Failure of {0} \nTablename : {1} \nscriptName : {2} \nfunctionName : {3} \nError Message : {4}").format(job_type, table, script_name, function_name, err_msg)
            msg.attach(MIMEText(message, 'plain'))
            receiver = [email_config['send_to']] + email_config['cc'].split(",")
            smtp = smtplib.SMTP(email_config['smtpserver'])
            smtp.login(email_config['smtplogin'], email_config['smtppassword'])
            smtp.sendmail(email_config['send_from'], receiver, msg.as_string())
            smtp.quit()

        except Exception as inst:
            raise inst
