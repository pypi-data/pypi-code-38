import sys
import pandas as pd
import numpy as np
import os
import time
import requests
import datetime
from salure_helpers.mysql import MySQL


class SalureFunctions:

    @staticmethod
    def applymap(key: pd.Series, mapping: dict, default=None):
        """
        This function maps a given column of a dataframe to new values, according to specified mapping.
        Column types float and int are converted to object because those types can't be compared and changed
        ----------
        :param key: input on which you want to apply the rename.
        :param mapping: mapping dict in which to lookup the mapping
        :param default_value: fallback if mapping value is not in mapping dict (only for non Series)
        :return: df with renamed columns
        """
        if type(key) == pd.Series:
            if key.dtype == 'float64' or key.dtype == 'int64':
                key = key.astype('object')
            if len(mapping) == 0:
                return 'Geen mapping gespecificeerd'
            else:
                key.replace(to_replace=mapping, inplace=True)

                return key
        else:
            if key in mapping.keys():
                return mapping[key]
            else:
                return default

    @staticmethod
    def catch_error(e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error = str(e)[:400].replace('\'', '').replace('\"', '') + ' | Line: {}'.format(exc_tb.tb_lineno)
        raise Exception(error)

    @staticmethod
    def scheduler_error_handling(e: Exception, task_id, run_id, mysql_con: MySQL, breaking=True, started_at=None):
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
        task_details = mysql_con.select('task_scheduler', 'queue_name, runfile_path', 'WHERE id = {}'.format(task_id))[0]
        taskname = task_details[0]
        customer = task_details[1].split('/')[-1].split('.')[0]

        if breaking:
            # Set scheduler status to failed
            mysql_con.update('task_scheduler', ['status', 'last_error_message'], ['IDLE', 'Failed'], 'WHERE `id` = {}'.format(task_id))
            # Log to database
            mysql_con.raw_query("INSERT INTO `task_execution_log` VALUES ({}, {}, 'CRITICAL', '{}', {}, '{}')".format(run_id, task_id, datetime.datetime.now(), exc_tb.tb_lineno, error), insert=True)
            mysql_con.raw_query("INSERT INTO `task_scheduler_log` VALUES ({}, {}, 'Failed', '{}', '{}')".format(run_id, task_id, started_at, datetime.datetime.now()),
                insert=True)
            # Notify users on Slack
            SalureFunctions.send_error_to_slack(customer, taskname, 'failed')
            raise Exception(error)
        else:
            mysql_con.raw_query("INSERT INTO `task_execution_log` VALUES ({}, {}, 'CRITICAL', '{}', {}, '{}')".format(run_id, task_id, datetime.datetime.now(), exc_tb.tb_lineno, error), insert=True)
            SalureFunctions.send_error_to_slack(customer, taskname, 'contains an error')

    @staticmethod
    def convert_empty_columns_type(df: pd.DataFrame):
        """
        Converts the type of columns which are complete empty (not even one value filled) to object. This columns are
        sometimes int or float but that's difficult to work with. Therefore, change always to object
        :param df: input dataframe which must be converted
        :return: dataframe with new column types
        """
        for column in df:
            if df[column].isnull().all():
                df[column] = None

        return df

    @staticmethod
    def dfdate_to_datetime(df: pd.DataFrame, dateformat=None):
        """
        This function processes input dataset and tries to convert all columns to datetime. If this throws an error, it skips the column
        ----------
        :param df: input dataframe for which you want to convert datetime columns
        :param dateformat: optionally specify output format for datetimes. If empty, defaults to %y-%m-%d %h:%m:%s
        :return: returns input df but all date columns formatted according to datetime format specified
        """
        df = df.apply(lambda col: pd.to_datetime(col, errors='ignore') if col.dtypes == object else col, axis=0)
        if format is not None:
            # optional if you want custom date format. Note that this changes column type from date to string
            df = df.apply(lambda col: col.dt.strftime(dateformat) if col.dtypes == 'datetime64[ns]' else col, axis=0)
            df.replace('NaT', '', inplace=True)

        return df


    @staticmethod
    def send_error_to_slack(customer, taskname, message):
        """
        This function is meant to send scheduler errors to slack
        :param customer: Customername where error occured
        :param taskname: Taskname where error occured
        :return: nothing
        """
        message = requests.get('https://slack.com/api/chat.postMessage',
                               params={'channel': 'C04KBG1T2',
                                       'text': 'The reload task of {taskname} from {customer} {message}. Check the {taskname} log for details'.format(customer=customer,
                                                                                                                                                      taskname=taskname,
                                                                                                                                                      message=message),
                                       'username': 'Task Scheduler',
                                       'token': 'xoxp-4502361743-4844095730-47265352212-271109ebd7'}).content

    @staticmethod
    def gen_dict_extract(key, var):
        """
        Looks up a key in a nested dict until its found.
        :param key: Key to look for
        :param var: input dict (don't set a type for this, since it can be list as well when it recursively calls itself)
        :return: Generator object with a list of elements that are found. Acces with next() to get the first value or for loop to get all elements
        """
        if hasattr(var, 'items'):
            for k, v in var.items():
                if k == key:
                    yield v
                if isinstance(v, dict):
                    for result in SalureFunctions.gen_dict_extract(key, v):
                        yield result
                elif isinstance(v, list):
                    for d in v:
                        for result in SalureFunctions.gen_dict_extract(key, d):
                            yield result

    @staticmethod
    def detect_changes_between_dataframes(df_old: pd.DataFrame, df_actual: pd.DataFrame, check_columns: list, unique_key: str, keep_old_values=False):
        """
        This function reads data from today and yesterday, flags this data according to old and new
        ----------
        :param old_df: A dataframe with the old values
        :param actual_df: A dataframe with the actual value. This one will be compared to the old_df
        :param check_columns: list of column(s) which you want to be used to check for changes in data
        :param unique_key: list of column(s) which you want to be used in order to group data. This should be the unique key which is always the same in data of today and yesterday
        :return: Returns a dataframe with the new colums change_type (deleted, new or edited) and changed_fields (contains all the names of the changed fields)
        """
        df_old['flag_old'] = 1
        df_actual['flag_old'] = 0
        df = pd.concat([df_old, df_actual], sort=True).drop_duplicates(subset=check_columns + [unique_key], keep=False)
        df['freq'] = df.groupby(unique_key)[unique_key].transform('count')
        df['change_type'] = np.where(np.logical_and(df.freq == 1, df.flag_old == 0), 'new',
                                     np.where(np.logical_and(df.freq == 1, df.flag_old == 1), 'deleted',
                                              np.where(df.freq >= 2, 'edited',
                                                       'nothing'
                                                       )
                                              )
                                     )
        # Now check which values in which column are changed. Add the names of this columns to the column 'changed_fields'
        df.sort_values(by=[unique_key] + ['flag_old'], inplace=True, ascending=False)
        df['changed_fields'] = ''
        df.reset_index(inplace=True, drop=True)
        # If the unique key is already in the columns which need to be checked, then don't add this double. Otherwise comparison of rows won't work because two values are returned for an index
        if unique_key in check_columns:
            df_changes = df.loc[:, check_columns].fillna('')
        else:
            df_changes = df.loc[:, check_columns + [unique_key]].fillna('')
        for i in df_changes.index.values:
            curr_row = df_changes.iloc[i]
            prev_row = df_changes.iloc[i - 1]
            if curr_row[unique_key] == prev_row[unique_key] and i != 0:
                unique_columns = curr_row != prev_row
                df.loc[i, 'changed_fields'] = str([key for key, value in unique_columns.iteritems() if value is True and key != 'flag_old'])
        if not keep_old_values:
            df = df[(df['flag_old'] == 0) | (df['change_type'] == 'deleted')]
            del df['flag_old']
        del df['freq']
        return df

    @staticmethod
    def generate_mutation_list_from_dataframes(df: pd.DataFrame, check_columns: list, unique_key: str):
        """
        This function compares the current row with the previous row, if the employeenumbers of these rows are the same.
        ----------
        :param df: Provide df which contains only edited data. Mandatory column in this df: employee_id
        :param check_columns: Provide the columns which you want to check for edited data. Only these columns will be checked
        :return: df with only mutations. This df contains four columns: employee, mutation type, old value and new value. For each mutation type, a new row will be created
        """
        df = df.loc[:, check_columns].fillna('')
        df.reset_index(inplace=True, drop=True)
        changes = pd.DataFrame()
        for i in df.index.values:
            curr_row = df.iloc[i]
            prev_row = df.iloc[i - 1]
            if curr_row[unique_key] == prev_row[unique_key] and i != 0:
                unique_columns = curr_row != prev_row
                new_vals = curr_row.loc[unique_columns]
                old_vals = prev_row.loc[unique_columns]
                for key in old_vals.keys():
                    changes = changes.append({'Employee': curr_row[unique_key], 'Mutation type': key, 'Old Value': old_vals[key], 'New Value': new_vals[key]}, ignore_index=True)

        return changes

    @staticmethod
    def archive_old_files(source_path: str, archive_path: str, comparison_data_path=None, archive_file_age_in_days=90):
        """
        This method moves all files from a source to a specified archive and cleans files from this archive that are older than archive_file_age_in_days
        :param source_path: source where to archive files from
        :param archive_path: archive path
        :param archive_file_age_in_days: all archived files older than this amount of days, will be moved
        :param comparison_data_path: optional comparison data path (standard method for detecting changes). This add extra functionality
        :return:
        """
        for file in os.listdir(archive_path):
            if os.stat(file).st_mtime < time.time() - archive_file_age_in_days * 86400:
                os.remove(archive_path + file)
        # If a comparison data path is specified, this functions moves data from source to comparison, and from comparison to archive
        if comparison_data_path is not None:
            for file in os.listdir(comparison_data_path):
                os.rename(comparison_data_path + file, archive_path + file)
            for file in os.listdir(source_path):
                os.rename(source_path + file, comparison_data_path + file)
        else:
            for file in os.listdir(source_path):
                os.rename(source_path + file, archive_path + file)
