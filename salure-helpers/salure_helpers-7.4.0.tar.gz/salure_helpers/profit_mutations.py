import os
import pandas as pd
import numpy as np
import datetime
import time
from salure_helpers.profit import GetConnector
from salure_helpers.salure_functions import SalureFunctions


class ProfitMutations:
    def __init__(self, profit_env, profit_token, input_dir, output_dir, base_url='rest.afas.online'):
        self.profit = GetConnector(profit_env, profit_token, base_url=base_url)
        self.date = datetime.date.today()
        self.yesterday = datetime.date.today() - datetime.timedelta(1)
        self.filename = 'daily_mutations_{}.xlsx'.format(self.date)
        self.input_dir = input_dir
        self.output_dir = output_dir
        # Create all file paths that are required
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        if not os.path.exists(self.input_dir + 'archive'):
            os.makedirs(self.input_dir + 'archive')
        if not os.path.exists(self.input_dir + 'profit'):
            os.makedirs(self.input_dir + 'profit')
        if not os.path.exists(self.input_dir + 'comparison_data'):
            os.makedirs(self.input_dir + 'comparison_data')
        # Create an Excel file for all sheets to write to
        self.writer = pd.ExcelWriter(self.output_dir + self.filename,
                                     engine='xlsxwriter',
                                     options={'remove_timezone': True})

    def get_data(self, employer=None):
        """
        This function gets all metadata from the specified app connector, then calls all get connectors that are in there.
        ----------
        :param: filters all data from connector on employer.
        :return: returns dict of dataframes, with key being the connector name and value the dataframe with the corresponding data
        In case of an error, a string with the error is returned
        """
        connectors = self.profit.get_metadata()
        if isinstance(connectors, list):
            data = {}
            for key in connectors:
                if employer is None:
                    data[key['id']] = pd.DataFrame(self.profit.get_filtered_data(key['id']))
                else:
                    data[key['id']] = pd.DataFrame(self.profit.get_filtered_data(key['id'], 'employer_code', employer))

            return data
        else:
            raise Exception('Profit connection failed or no metadata was returned')


    def save_to_msgpack(self, df_dict: dict, base_dir: str):
        """
        This function is used to save a dataframe to msgpack
        ----------
        :param df_dict: dictionary of dataframes. Key is dataframe name, value is dataframe
        :param base_dir: base directory to save files to. If this directory doesn't exist, it will be created, including all necessary sub folders
        :return: nothing
        """
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        for df in df_dict:
            df_dict[df].to_msgpack('{}{}.msgpack'.format(base_dir, df))

    def get_changed_data(self, filename :str, check_columns: list, unique_key: str, keep_old_values=True):
        """
        This function reads data from today and yesterday, flags this data according to old and new
        ----------
        :param filename: Base file name where data is gotten from. This base name is appended with date of runtime
        :param check_columns: list of column(s) which you want to be used to check for changes in data
        :param unique_key: list of column(s) which you want to be used in order to group data. This should be the unique key which is always the same in data of today and yesterday
        :return: original input df with all values flagged according to mutation type
        """

        try:
            if os.path.isfile('{dir}{filename}.msgpack'.format(dir=self.input_dir + 'comparison_data/', filename=filename)):
                df_old = pd.read_msgpack('{dir}{filename}.msgpack'.format(dir=self.input_dir + 'comparison_data/', filename=filename))
            else:
                raise Exception('Old datafile doesn\'t exist')
            if os.path.isfile('{dir}{filename}.msgpack'.format(dir=self.input_dir + 'profit/', filename=filename)):
                df_new = pd.read_msgpack('{dir}{filename}.msgpack'.format(dir=self.input_dir + 'profit/', filename=filename))
            else:
                raise Exception('New datafile doesn\'t exist')
            df_old['flag_old'] = 1
            df_new['flag_old'] = 0
            print(df_old[:10].to_string())
            print(df_new[:10].to_string())
            df = pd.concat([df_old, df_new], sort=True).drop_duplicates(subset=check_columns, keep=False)
            if len(df) > 0:
                df.sort_values(by=['flag_old'] + [unique_key], inplace=True, ascending=False)
                df['freq'] = df.groupby(unique_key)[unique_key].transform('count')
                df['change'] = np.where(np.logical_and(df.freq == 1, df.flag_old == 0),
                                        'new',
                                        np.where(np.logical_and(df.freq == 1, df.flag_old == 1),
                                                 'deleted',
                                                 np.where(df.freq >= 2, 'edited', 'nothing')))
                if not keep_old_values:
                    df = df[(df['flag_old'] == 0) | (df['change'] == 'deleted')]
                del df['freq']
                del df['flag_old']

            return df

        except Exception as e:
            SalureFunctions.catch_error(e)

    def process_dataset(self, check_columns: list, sheetname: str, filename: str, unique_key: str, changed_or_edited: str, dateformat=None, export_columns=None, column_value_mapping=None, column_mapping=None):
        """
        This function processes input dataset and runs all operations necessary to export mutations
        ----------
        :param check_columns: list of column(s) which you want to be used to check for changes in data
        :param connector: name of profit connector where data should be gotten from
        :param unique_key: list of column(s) on which to detect if entry already existed in data of previous load
        :param changed_or_edited: string 'edited' if you df contains only edited data, 'new' if df contains new employees data
        :param dateformat: specify custom dateformat if you do not want to use default datetimestamp format
        :param export_columns: column titles of Excel mutation sheet. If not specified, then df columnnames will be used
        :param column_value_mapping: applymap on values in column
        :param column_mapping: applymap on column titlesv
        :return: calls export functions which output changes to chosen format
        """
        try:
            df_mutations = self.get_changed_data(filename, unique_key=unique_key, check_columns=check_columns)
            df_mutations = df_mutations[df_mutations.change == changed_or_edited]
            df_mutations = SalureFunctions.dfdate_to_datetime(df_mutations, dateformat)
            df_mutations = self.detect_changed_values(df_mutations, check_columns, unique_key)
            if len(df_mutations.index) > 0:
                if column_value_mapping is not None:
                    SalureFunctions.applymap(df_mutations['Mutation type'], mapping=column_value_mapping)
                if column_mapping is not None:
                    df_mutations.rename(columns=column_mapping, inplace=True)
            if changed_or_edited == 'edited':
                self.export_mutations_to_excel(df_mutations, sheetname, export_columns)
            else:
                self.export_to_template(df_mutations)
        except Exception as e:
            SalureFunctions.catch_error(e)

    def process_new_employees(self, unique_key: str, filename: str):
        """
        This function is the process trigger to process new employees
        ----------
        :return: nothing
        """
        df_mutations = self.get_changed_data(filename, check_columns=[unique_key], unique_key=unique_key)
        df_mutations = df_mutations[df_mutations.change == 'new']
        df_mutations = SalureFunctions.dfdate_to_datetime(df_mutations, '%d.%m.%Y')
        print(df_mutations[:10].to_string())
        self.export_to_template(df_mutations)

    def detect_changed_values(self, df: pd.DataFrame, check_columns: list, unique_key: str):
        """
        This function compares the current row with the previous row, if the employeenumbers of these rows are the same.
        ----------
        :param df: Provide df which contains only edited data. Mandatory column in this df: employee_id
        :param check_columns: Provide the columns which you want to check for edited data. Only these columns will be checked
        :return: df with only mutations. This df contains four columns: employee, mutation type, old value and new value
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

    def export_mutations_to_excel(self, df: pd.DataFrame, sheetname: str, columns=None):
        """
        This method exports to excel. If no columns are specified, then whole DF is exported. Columns will be the the DF columns
        If columns are specified, these will be used as header row. Only DF columns that are in the columns list, will be filled with data, rest is ignored
        :param df: input dataframe with data
        :param sheetname: sheetname to write to
        :param columns: list of columns which are accepted in Excel. DF column name must match one of these to be processed
        :return: void
        """
        print(sheetname)
        print(df.to_string())
        if columns is not None:
            columns = list(columns)
            df_columns = df.columns.values.tolist()

            # Add data to columns
            for df_column in df_columns:
                if df_column in columns:
                    series = df[df_column]
                    print(series.to_excel(self.writer, sheet_name=sheetname, startcol=columns.index(df_column), index=False, startrow=1, header=False))

            # Add custom headercolumns
            if len(df) > 0:
                worksheet = self.writer.sheets[sheetname]
                workbook = self.writer.book
                header_format = workbook.add_format({'bold': True})
                for i in columns:
                    worksheet.write(0, columns.index(i), i, header_format)
        else:
            df.to_excel(self.writer, sheet_name=sheetname, index=False)


    def export_to_template(self, df):
        # This is the custom export that is different per customer.
        template = self.export_template()
        raise Exception('No export logic defined')


    def export_template(self):
        """
        This function is the place where you specify a custom output template to use when necessary. This template is used by the export_to_template function
        ----------
        :return: returns custom template or an error if no template is specified
        """
        try:
            template = """"""
            if len(template) == 0:
                raise Exception('Specificy an export template before using this!')
            else:
                return template

        except Exception as e:
            SalureFunctions.catch_error(e)

    def move_and_cleanup_files(self):
        # archive contains files up to 90 days
        for file in os.listdir(self.input_dir + 'archive'):
            if os.stat(self.input_dir + 'archive/' + file).st_mtime < time.time() - 90 * 86400:
                os.remove(self.input_dir + 'archive/' + file)
        # old comparison data is moved to archive
        for file in os.listdir(self.input_dir + 'comparison_data'):
            os.rename(self.input_dir + 'comparison_data/' + file, self.input_dir + 'archive/' + str(datetime.datetime.now().date()) + file)
        # new data is moved to comparison data
        for file in os.listdir(self.input_dir + 'profit'):
            os.rename(self.input_dir + 'profit/' + file, self.input_dir + 'comparison_data/' + file)