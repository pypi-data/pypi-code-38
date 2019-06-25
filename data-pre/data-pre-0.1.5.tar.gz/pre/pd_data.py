"""
@author: magician
@file: pd_data.py
@date: 2019/06/05
"""
import importlib

import pandas as pd
import numpy as np

from pre.pd_params import READ_FILE, WRITE_FILE
from pre.pd_utils import check_type


class PdData(object):
    """
    PdData
    """

    def __init__(self, file, file_type):
        """
        init file,file_type
        :param file:
        :param file_type:  file type
        """
        self.file = file
        self.file_type = file_type
        # df = pd.DataFrame()

    def read_file(self, **kwargs):
        """
        read excel, csv, pickle(at this time)
        :param:  kwargs  drop_flag: True or False
        :return: DataFrame
        """
        drop_flag = kwargs.get('drop_flag')
        if 'drop_flag' in list(kwargs.keys()):
            kwargs.pop('drop_flag')
        if self.file_type not in list(READ_FILE.keys()):
            return '{0} file type is not supported at this time!'.format(self.file_type)

        reader = importlib.import_module(READ_FILE[self.file_type])
        df = reader(self.file, **kwargs)
        # drop duplicates data
        df.drop_duplicates(inplace=bool(drop_flag))

        return df

    def write_file(self, df, **kwargs):
        """
        write excel, csv, pickle(at this time)
        :param:  df     DataFrame
        :param:  kwargs
        :return: File
        """
        if self.file_type not in list(WRITE_FILE.keys()):
            return '{0} file type is not supported at this time!'.format(self.file_type)

        writer = importlib.import_module(WRITE_FILE[self.file_type])
        new_file = writer(df, **kwargs)

        return new_file

    @staticmethod
    def df_preview(df, **kwargs):
        """
        preview DataFrame
        :param: df      DataFrame
        :param: kwargs: pre_list      index or label
                        data_index    row or column
                        dtype         int or string
        :return: DataFrame
        """
        pre_list = kwargs.get('pre_list', [])
        data_index = kwargs.get('data_index', 'row')
        dtype = kwargs.get('dtype', 'int')
        error = ''
        new_df = pd.DataFrame()
        if pre_list < 1 or not isinstance(pre_list, list):
            error = 'pre_list data is error!'
        elif len(pre_list) == 2:
            if dtype == 'int':
                error = check_type(pre_list, dtype)
                if not error:
                    if pre_list[-1] == 0:
                        new_df = df.head(pre_list[0])
                    elif pre_list[0] == 0:
                        new_df = df.tail(pre_list[0])
                    else:
                        new_df = df.iloc[pre_list[0]:pre_list[-1]]
            elif dtype == 'string':
                error = check_type(pre_list, dtype)
                new_df = df.loc[pre_list, :] if data_index == 'row' else df.loc[:, pre_list]
            else:
                error = 'dtype error!'
        else:
            if dtype == 'string':
                new_df = df.loc[pre_list, :] if data_index == 'row' else df.loc[:, pre_list]
            else:
                error = 'dtype error!'

        if error:
            return error

        return new_df

    @staticmethod
    def df_remove(df, **kwargs):
        """
        DataFrame remove
        :param: df      DataFrame
        :param: kwargs  rows:    list
                        columns: list
        :return: DataFrame
        """
        rows = kwargs.get('rows', [])
        columns = kwargs.get('columns', [])
        new_df = df.drop(index=rows, columns=columns, inplace=True)

        return new_df

    @staticmethod
    def df_select(df, **kwargs):
        """
        DataFrame select
        :param: df      DataFrame
        :param: kwargs:    rows:    list
                           columns: list
                           dtype:   int or string
        :return: DataFrame
        """
        rows = kwargs.get('rows', [])
        columns = kwargs.get('columns', [])
        dtype = kwargs.get('dtype')
        data = []
        new_df = pd.DataFrame()
        data.extend(rows)
        data.extend(columns)
        error = check_type(data, dtype)
        if not error:
            if dtype == 'int':
                if len(rows) == 2 and len(columns) == 2:
                    new_df = df.iloc[rows[0]:rows[-1], columns[0]:columns[-1]]
                else:
                    error = 'rows or columns error!'
            else:
                new_df = df.loc[rows, columns]

        if error:
            return error

        return new_df

    @staticmethod
    def df_style(df, **kwargs):
        """
        DataFrame style
        :param: df      DataFrame
        :param: kwargs: is_style_func:      True or False
                        background_color:   background color
                        color:              font color
                        border_color:       border color
                        style_map_func:     style map function
                        style_func:         style function
                        precision:          precision
        :return: DataFrame
        """
        is_style_func = kwargs.get('is_style_func', False)

        if is_style_func:
            background_color = kwargs.get('background_color')
            color = kwargs.get('color')
            border_color = kwargs.get('border_color')
            new_df = df.style.set_properties(
                **{
                    'background-color': background_color,
                    'color': color,
                    'border-color': border_color
                })
        else:
            style_map_func = kwargs.get('style_map_func')
            style_func = kwargs.get('style_func')
            precision = kwargs.get('precision', 2)
            new_df = df.style.applymap(style_map_func).apply(style_func).set_precision(precision)

        return new_df

    @staticmethod
    def df_pivot(df, **kwargs):
        """
        DataFrame pivot table
        :param kwargs:   is_style_func:      True or False
                         background_color:   background color
                         color:              font color
                         border_color:       border color
                         style_map_func:     style map function
                         style_func:         style function
                         precision:          precision
        :return: DataFrame
        """
        values = kwargs.get('values', [])
        index = kwargs.get('index', [])
        columns = kwargs.get('columns', [])
        fill_value = kwargs.get('fill_value', 0)
        aggfunc = kwargs.get('aggfunc', np.sum)
        dropna = kwargs.get('dropna', True)

        new_df = pd.pivot_table(df,
                                values=values,
                                index=index,
                                columns=columns,
                                fill_value=fill_value,
                                aggfunc=aggfunc,
                                dropna=dropna)

        return new_df

    @staticmethod
    def df_total(df, **kwargs):
        """
        DataFrame subtotal total
        :param df:     DataFrame
        :param kwargs: subtotal:    subtotal
                       group_level: level       'Location'
                       total_list:  total       ('All', 'Total')
        :return: DataFrame
        """
        subtotal = kwargs.get('subtotal', 'Subtotal')
        group_level = kwargs.get('group_level', '')
        total_list = kwargs.get('total_list', ('All', 'Total'))
        if total_list != 2 or not isinstance(total_list, tuple):
            return 'total_list must have two element tuple'

        new_df = pd.concat([
            d.append(d.sum().rename((k, subtotal)))
            for k, d in df.groupby(level=group_level)
        ]).append(df.sum().rename(total_list))

        return new_df

    @staticmethod
    def df_array(df, **kwargs):
        """
        DataFrame to array
        :param df:     DataFrame
        :param kwargs:
        :return: DataFrame
        """
        return df.to_numpy().tolist()

    @staticmethod
    def df_index_drop(df, **kwargs):
        """
        Multi-index DataFrame downgrade
        :param df:     DataFrame
        :param kwargs: drop_key: or 'produce_quantity'
        :return: DataFrame
        """
        drop_key = kwargs.get('drop_key', 0)

        new_df = df.copy(deep=True)
        if drop_key in new_df.index:
            new_df.index = new_df.index.droplevel(drop_key)
        else:
            new_df.columns = new_df.columns.droplevel(drop_key)

        return new_df

    @staticmethod
    def df_reshape(df, **kwargs):
        """
        Multi-index DataFrame reshape
        :param df:     DataFrame
        :param kwargs:
        :return: DataFrame
        """
        return pd.DataFrame(df.to_records())

    @staticmethod
    def df_statistics(df, **kwargs):
        """
        DataFrame statistics
        :param df:     DataFrame
        :param kwargs:
        :return: DataFrame
        """
        pass

    @staticmethod
    def df_pre(df, **kwargs):
        """
        DataFrame preprocessing
        :param df:     DataFrame
        :param kwargs:
        :return: DataFrame
        """
        pass
