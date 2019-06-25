"""
@author: magician
@file: pd_csv.py
@date: 2019/06/10
"""
import os

import pandas as pd


def read_csv(file, **kwargs):
    """
    read csv
    :param file:    csv file or csv path
    :param kwargs:  sep:        separator  ','
                    sheet_name: 'Sheet1' or ['Sheet1', 'Sheet2']
                    header:     0 or [0, 1]
                    na_values:  ['NA']
                    usecols:    2 or 'A,C:E' or ['A', 'C'] or [0, 2, 3]
                    skiprows:   skip rows
                    parse_date: ['date_strings'] or {'Date': '%Y-%m-%d'}
                    converters: {'MyBools': bool}
                    dtypes:     {'MyInts': 'int64', 'MyText': str}
    :return: DataFrame
    """
    sep = kwargs.get('sep', ',')
    header = kwargs.get('header', 0)
    na_values = kwargs.get('na_values', ['NA'])
    usecols = kwargs.get('usecols')
    parse_dates = kwargs.get('parse_dates')
    converters = kwargs.get('converters')
    dtypes = kwargs.get('dtypes')

    csv_df = pd.read_csv(file,
                         sep=sep,
                         header=header,
                         na_values=na_values,
                         usecols=usecols,
                         parse_dates=parse_dates,
                         converters=converters,
                         dtypes=dtypes,
                         **kwargs)

    return csv_df


def write_csv(df, **kwargs):
    """
    write csv
    :param df:
    :param kwargs: file_name:     file name
                   file_path:     file path
                   sep:           sep
                   path_or_buf:   path or buffer
                   header:        ['A', 'B']
                   index:         index
    :return: {
        'file_name': file_name,
        'output_path': output_path
    }
    """
    file_name = kwargs.get('file_name', '')
    file_path = kwargs.get('file_path', '')
    output_path = os.path.join(file_path, file_name)
    sep = kwargs.get('sep', ',')
    header = kwargs.get('header')
    index = kwargs.get('index', False)

    df.to_csv(path_or_buf=output_path,
              sep=sep,
              header=header,
              index=index,
              encoding='utf-8')

    return {
        'file_name': file_name,
        'output_path': output_path
    }
