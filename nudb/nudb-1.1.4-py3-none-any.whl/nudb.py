# coding: utf-8

import os
import re
import sys
import json
import codecs
import requests
from nudb.tools import check_JSON
from nudb.error import NudbException, ParametersParseException
from nudb.customErrorMessage import custom_error_message

class Nudb(object):

    def __init__(self):        
        # default host and port
        host = 'localhost'
        port = '5800'
        self.api = 'http://%s:%s/nudb/' % (host, port)
        self.db = 'test'

    def connect(self, host, port, db):
        self.api = 'http://%s:%s/nudb/' % (host, port)
        self.db = db

    def get_DB_info(self, timeout=10):
        """
        Get DB info.  
        timeout: timeout (s), default is 10s.
        """

        url = self.api + 'getDBInfo'
        options = {
            'db': self.db,
            'out': 'json'
        }
        
        res = requests.post(url, options, timeout=timeout)
        return json.loads(res.text)

    def rput(self, data, data_type, rec_beg=None, timeout=10):
        """ 
        Insert data to DB.  
        data: Data.  
        data_type: json/text  
        rec_beg: record begin pattern.  
        timeout: timeout (s), default is 10s.
        """

        if data_type != 'text' and data_type != 'json':
            raise ParametersParseException(custom_error_message['WRONG_FORMAT_PARAMETER'])
        if data_type == 'text':
            if not isinstance(data, str):
                raise ParametersParseException(custom_error_message['WRONG_FORMAT'])
            elif not rec_beg:
                raise ParametersParseException(custom_error_message['MISSING_RECBEG_PARAMETER'])
        if data_type == 'json':
            # 檢查為是否為正確的JSON格式, 若正確則判斷是JSON object 或 string
            check = check_JSON(data)
            if check == 1:
                # JSON object
                data = json.dumps(data)
            elif check < 1:
                raise ParametersParseException(custom_error_message['WRONG_FORMAT'])

        url = self.api + 'rput'
        options = {
            'db': self.db,
            'data': data,
            'format': data_type
        }

        # data type: text
        if data_type == 'text':
            # replace \\ -> \
            options['data'] = re.sub('\\\\\\\\', '\\\\', data)
            options['recbeg'] = rec_beg

        res = requests.post(url, options, timeout=timeout)
        return json.loads(res.text)
    
    def fput(self, file_path, data_type, rec_beg=None, timeout=60):
        """ 
        Insert data from file.
        file_path: File path.    
        data_type: json/text  
        rec_beg: record begin pattern.  
        timeout: timeout (s), default is 60s.
        """

        if not os.path.exists(file_path):
            raise ParametersParseException(file_path + custom_error_message['FILE_NOT_EXISTS'])
        if data_type != 'text' and data_type != 'json':
            raise ParametersParseException(custom_error_message['WRONG_FORMAT_PARAMETER'])
        if data_type == 'text' and not rec_beg:
            raise ParametersParseException(custom_error_message['MISSING_RECBEG_PARAMETER'])
        
        url = self.api + 'fput'
        options = {
            'db': self.db,
            'format': data_type
        }
        file_data = {
            'file': codecs.open(file_path, 'rb', 'utf-8')
        }

        if data_type == 'text':
            options['recbeg'] = rec_beg

        res = requests.post(url, options, files=file_data, timeout=timeout)
        return json.loads(res.text)

    def rget(self, data_id, search_field='rid', timeout=10):
        """
        Get data by rid or primary key.  
        data_id: record ID or primary key.  
        search_field: 搜尋的欄位 (rid or key).  
        timeout: timeout (s), default is 10s.
        """

        if search_field != 'rid' and search_field != 'key':
            raise ParametersParseException(custom_error_message['WRONG_SEARCH_FIELD_PARAMETER'])

        url = self.api + 'rget'
        options = {
            'db': self.db,
            'out': 'json',
            search_field: data_id
        }
        
        res = requests.get(url, options, timeout=timeout)
        return json.loads(res.text)

    def rdel(self, data_id, search_field='rid', timeout=10):
        """
        Delete record by rid or primary key.  
        data_id: record ID or primary key.  
        search_field: 搜尋的欄位 (rid or key).  
        timeout: timeout (s), default is 10s.
        """

        if search_field != 'rid' and search_field != 'key':
            raise ParametersParseException(custom_error_message['WRONG_SEARCH_FIELD_PARAMETER'])

        url = self.api + 'rdel'
        options = {
            'db': self.db,
            'out': 'json',
            search_field: data_id
        }
        
        res = requests.post(url, options, timeout=timeout)
        return json.loads(res.text)
    
    def rupdate(self, data_id, data, data_type, search_field='rid', update_method='replaceRecord', timeout=10):
        """ 
        Update record by rid or primary key.  
        data_id: record ID or primary key.  
        data: Data   
        data_type: json/text  
        search_field: 搜尋的欄位 (rid or key).  
        update_method: 更新方式 (replaceRecord or replaceField)  
        timeout: timeout (s), default is 10s.
        """

        if data_type != 'text' and data_type != 'json':
            raise ParametersParseException(custom_error_message['WRONG_FORMAT_PARAMETER'])
        if data_type == 'text' and not isinstance(data, str):
            raise ParametersParseException(custom_error_message['WRONG_FORMAT'])
        if data_type == 'json':
            # 檢查為是否為正確的JSON格式, 若正確則判斷是JSON object 或 string
            check = check_JSON(data)
            if check == 1:
                # JSON object
                data = json.dumps(data)
            elif check < 1:
                raise ParametersParseException(custom_error_message['WRONG_FORMAT'])
        if search_field != 'rid' and search_field != 'key':
            raise ParametersParseException(custom_error_message['WRONG_SEARCH_FIELD_PARAMETER'])
        if update_method != 'replaceRecord' and update_method != 'replaceField':
            raise ParametersParseException(custom_error_message['WRONG_UPDATE_METHOD_PARAMETER'])

        url = self.api + 'rupdate'
        options = {
            'db': self.db,
            'getrec': 'n',
            'out': 'json',
            'format': data_type,
            search_field: data_id
        }

        if data_type == 'text':
            # replace \\ -> \
            data = re.sub('\\\\\\\\','\\\\', data)

        if update_method == 'replaceRecord':
            options['record'] = data
        else:
            options['field'] = data

        res = requests.post(url, options, timeout=timeout)
        return json.loads(res.text)
                
    def search(self, options, timeout=10):
        if not options:
            raise ParametersParseException(custom_error_message['MISSING_QUERY_PARAMETER'])

        url = self.api + 'query'
        res = requests.get(url, options, timeout=timeout)

        if 'out' in options and options['out'] == 'json':
            return json.loads(res.text)
        else:
            return res.text