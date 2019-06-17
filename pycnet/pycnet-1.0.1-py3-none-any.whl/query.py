import requests
import xml.etree.ElementTree as et
import pandas as pd
from collections import OrderedDict

_query_token = ''


def set_token(token):
    """Set the token key to access the database.

    Args:
        token (str): The token.
    """
    global _query_token
    _query_token = token


def query(sql):
    """Query the database.

    Args:
        sql (str): The SQL statement.

    Returns:
        pd.DataFrame: Return as DataFrame.
    """
    global _query_token
    if _query_token == '':
        raise Exception('Please set_token first!')

    url = 'https://www2.pyc.edu.hk/pycnet/sqladmin/request_xml.php'
    token = f'Bearer {_query_token}'
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    data = {'query': sql}
    response = requests.post(url, json=data, headers=headers).text

    try:
        xroot = et.fromstring(response)

        all_rows = []
        for i, item in enumerate(xroot):
            row = OrderedDict()
            for element in item:
                row[element.tag] = element.text
            all_rows.append(row)
        df = pd.DataFrame(all_rows)
        df = df.apply(pd.to_numeric, errors='ignore')
        return df

    except:
        raise Exception('''
        There is an error when parsing response from pycnet.
        Error msg:
        ''' + response)
