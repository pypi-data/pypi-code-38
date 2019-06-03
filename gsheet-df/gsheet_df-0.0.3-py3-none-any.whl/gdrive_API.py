import requests
import numpy as np
import pandas as pd
import xlrd
import io

def download_excel(code, table, key):
    """
    download_excel(code, table, key)
    
    code: identify the excel file
    table: names of table
    key: secret key for authentication
    """
    ok, f = _download_file(code, key)
    if not ok:
        return pd.DataFrame({'error': [f]})
    wb = xlrd.open_workbook(file_contents=f.read())
    df = pd.read_excel(wb, sheet_name=table, engine='xlrd')
    f.close()
    return df

def download_excel_all(code, key):
    """
    download_excel_all(code, key)
    
    code: identify the excel file
    key: secret key for authentication
    """
    ok, f = _download_file(code, key)
    if not ok:
        return {'error': pd.DataFrame({'error': [f]})}
    wb = xlrd.open_workbook(file_contents=f.read())
    df_dict = pd.read_excel(wb, sheet_name=None, engine='xlrd')
    f.close()
    return df_dict

def _download_file(code, key):
    master_url = 'https://script.google.com/macros/s/AKfycbwysCzhIGDzw6YgJh0eSJDBbmRYdcMtYfTwvePw-AfXVrxnqXld/exec'
    data = {
        'code': code,
        'key': key,
    }
    r = requests.post(master_url, data=data)
    try:
        b = io.BytesIO(np.array(r.json()["result"], dtype=np.uint8))
    except:
        return False, r.text
    return True, b