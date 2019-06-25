"""
@author: magician
@file: pd_params.py
@date: 2019/06/05
"""
READ_FILE = {
    'xls': 'excel.pd_excel.read_excel',
    'xlsx': 'excel.pd_excel.read_excel',
    'csv': 'csv.pd_csv.read_csv',
    'json': 'json.pd_json.read_json',
    'zip': 'pickle.pd_zip.read_pickle'
}

WRITE_FILE = {
    'xls': 'excel.pd_excel.write_excel',
    'xlsx': 'excel.pd_excel.write_excel',
    'csv': 'csv.pd_csv.write_csv',
    'json': 'json.pd_json.write_json',
    'zip': 'pickle.pd_zip.write_pickle'
}
