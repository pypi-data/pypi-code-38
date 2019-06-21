import chardet
import os
import pandas as pd


def detect_encoding(file_path):
    data = open(file_path, "rb").read()
    encoding = chardet.detect(data)
    if encoding['encoding'] == 'utf-8':
        return 'utf-8-sig'
    else:
        return encoding['encoding']


def is_file(input_data):
    return isinstance(input_data, str) and os.path.isfile(input_data)


def is_dataframe(input_data):
    return isinstance(input_data, pd.DataFrame.__class__)
