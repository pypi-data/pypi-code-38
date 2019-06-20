import requests
import pandas as pd
from io import StringIO


def download(code,table,key):
    """Download the requested google sheet table. Return as pd.DataFrame.
    
    Args:
        code (str): Identify the google sheet
        table (str): Names of tables, separated by ','
        key (str): Secret key for authentication
    
    Returns:
        pd.DataFrame: The requested google sheet table.
    """
    master_url = 'https://script.google.com/macros/s/AKfycbzYijGb5eOpWCGZ8gLNb7uZTdshB7dDvXWeEaANDDna7pJYgME/exec'

    data = {
        'code': code,
        'table': table,
        'elementsep': '<element>',
        'rowsep': '<row>',
        'key': key,
    }

    r = requests.post(master_url, data=data).text

    if '\n' in r:
        r = r.replace('\n','<br>')

    r = r.replace('<row>','\n')
    return pd.read_csv(StringIO(r), sep='<element>', engine='python')


def download_gs(code, table, key, element_sep = '@', row_sep = '\n', str_only=False):
    """Deprecated. Use download(code,table,key).
    Download the requested google sheet table. Return as pd.DataFrame.
    
    Args:
        code (str): Identify the google sheet
        table (str): Names of tables, separated by ','
        key (str): Secret key for authentication
        element_sep (str, optional): Element separator used before parsing. Defaults to '@'.
        row_sep (str, optional): Row separator used before parsing. Defaults to '\n'.
        str_only (bool, optional): Return response text instead of pd.dataframe. Defaults to False.
    
    Returns:
        pd.DataFrame: The requested google sheet table.
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
