import requests
import pandas as pd
from io import StringIO

def download_gs(code, table, key, element_sep = '@', row_sep = '\n', str_only=False):
    """
    download_gs(code, table, key, element_sep = '@', row_sep = '\\n', str_only=False)
    
    code: identify the google sheet
    table: names of tables, separated by ','
    key: secret key for authentication
    srt_only: return response text instead of pd.dataframe
    """

    master_url = 'https://script.google.com/macros/s/AKfycbzYijGb5eOpWCGZ8gLNb7uZTdshB7dDvXWeEaANDDna7pJYgME/exec'

    data = {
        'code': code,
        'table': table,
        'elementsep': element_sep,
        'rowsep': row_sep,
        'key': key,
    }

    r = requests.post(master_url, data=data)
    if str_only:
        return r.text
    else:
        return pd.read_csv(StringIO(r.text), sep=element_sep)
