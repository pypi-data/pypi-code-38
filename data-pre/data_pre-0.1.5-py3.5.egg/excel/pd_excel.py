"""
@author: magician
@file: pd_excel.py
@date: 2019/06/10
"""
import os

import pandas as pd


def read_excel(file, **kwargs):
    """
    read excel
    :param file:    excel file or excel path
    :param kwargs:  sheet_name: 'Sheet1' or ['Sheet1', 'Sheet2']
                    header:     0 or [0, 1]
                    na_values:  ['NA']
                    usecols:    2 or 'A,C:E' or ['A', 'C'] or [0, 2, 3]
                    parse_date: ['date_strings'] or {'Date': '%Y-%m-%d'}
                    converters: {'MyBools': bool}
                    dtypes:     {'MyInts': 'int64', 'MyText': str}
    :return: DataFrame
    """
    sheet_name = kwargs.get('sheet_name')
    header = kwargs.get('header', 0)
    na_values = kwargs.get('na_values', ['NA'])
    usecols = kwargs.get('usecols')
    parse_dates = kwargs.get('parse_dates')
    converters = kwargs.get('converters')
    dtypes = kwargs.get('dtypes')
    # file type(excel file or excel path)
    new_excel = file if os.path.isfile(file) else pd.ExcelFile(file)

    excel_df = pd.read_excel(new_excel,
                             sheet_name=sheet_name,
                             header=header,
                             na_values=na_values,
                             usecols=usecols,
                             parse_dates=parse_dates,
                             converters=converters,
                             dtypes=dtypes)

    return excel_df


def write_excel(df, **kwargs):
    """
    write excel
    :param df:
    :param kwargs: file_name:     file name
                   file_path:     file path
                   engine:        openpyxl or xlsxwriter or xlwt
                   headers:       [['A', 'B'], ['C', 'D']]
                   sheets_names:  'Sheet1' or ['Sheet1', 'Sheet2']
                   index:         index
                   merge_cells:   merge cells

    :return: {
        'file_name': file_name,
        'output_path': output_path
    }
    """
    file_name = kwargs.get('file_name', '')
    file_path = kwargs.get('file_path', '')
    output_path = os.path.join(file_path, file_name)
    engine = kwargs.get('engine')
    headers = kwargs.get('headers') if isinstance(kwargs.get('headers'), list) else [kwargs.get('headers', '')]
    sheet_names = kwargs.get('sheet_names') if isinstance(kwargs.get('sheet_names'), list) else [
        kwargs.get('sheet_names', '')]
    index = kwargs.get('index', False)
    merge_cells = kwargs.get('merge_cells', True)

    with pd.ExcelWriter(output_path, engine=engine) as writer:
        for key, sheet in enumerate(sheet_names):
            df.to_excel(excel_writer=writer,
                        header=headers[key],
                        sheet_name=sheet,
                        index=index,
                        merge_cells=merge_cells,
                        encoding='utf-8')

    return {
        'file_name': file_name,
        'output_path': output_path
    }
