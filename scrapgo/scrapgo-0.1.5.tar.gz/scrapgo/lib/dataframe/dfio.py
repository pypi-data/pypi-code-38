# import os
import pandas as pd

from scrapgo.utils.fileutils import get_file_extension

EXCEL_FILE_EXTENSIONS = ['.xlsx', '.xls', 'xls', 'xlsx', 'excel']
CSV_FILE_EXTENSIONS = ['.csv', 'csv']


def path2dataframe(path, **kwargs):
    ext = get_file_extension(path)
    if ext in EXCEL_FILE_EXTENSIONS:
        dataframe = pd.read_excel(path)
    elif ext in CSV_FILE_EXTENSIONS:
        dataframe = pd.read_csv(path)
    else:
        raise ValueError(f"The File Extension {ext} is not Supported!")
    return dataframe


def dataframe2path(dataframe, filename, extension='csv', index=False, **kwargs):
    if extension in CSV_FILE_EXTENSIONS:
        path = filename + '.csv'
        dataframe.to_csv(path, index=index, **kwargs)
    elif extension in EXCEL_FILE_EXTENSIONS:
        path = filename + '.xlsx'
        dataframe.to_excel(path, index=index, **kwargs)
    elif extension is None:
        print(dataframe.head())
    else:
        msg = f"Output file extension must in xlsx, csv"
        raise ValueError(msg)
