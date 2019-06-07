from __future__ import absolute_import
from __future__ import unicode_literals

import json
import jwt
import datetime
import requests
import re
import logging

_logger = logging.getLogger(__name__)

__all__ = [
    'Error', 'Warning',
    'InterfaceError', 'DatabaseError',
    'InternalError', 'OperationalError',
    'ProgrammingError', 'DataError', 'NotSupportedError',
]


class Error(Exception):
    pass


class Warning(Exception):
    pass


class InterfaceError(Error):
    pass


class DatabaseError(Error):
    pass


class InternalError(DatabaseError):
    pass


class OperationalError(DatabaseError):
    pass


class ProgrammingError(DatabaseError):
    pass


class IntegrityError(DatabaseError):
    pass


class DataError(DatabaseError):
    pass


class NotSupportedError(DatabaseError):
    pass


class connection(object):

    def __init__(self, url=None, customerid=None, key=None, secret=None,
                 database=None, hostname=None, verify_ssl=True, **kwargs):

        # We want to supress the warnings message
        self.baseurl = ("%s/public/api/customers/%s" %
                        (url, customerid))
        self.audit_store_url = ("%s/public/api/customers/%s/auditQuery" %
                                (url, customerid))
        self.global_schema_url = ("%s/public/api/customers/%s/schema/global" %
                                  (url, customerid))
        self.realtime_schema_url = ("%s/public/api/customers/%s/%s" %
                                    (url, customerid, "schema/realtime"))
        self.query_job_url = ("%s/public/api/customers/%s/queryJobs" %
                              (url,customerid))

        self.customerid = customerid
        self.key = key
        self.secret = secret
        self.database = database.lower()
        self.hostname = hostname
        self._result_set = tuple()
        self._description = tuple()
        self._error = None
        self._rowcount = -1
        self._status = True
        self._arraysize = -1
        self._json_result = {}
        self.query_id = None
        self.query_status = None
        self.verify_ssl = verify_ssl
        self.query_id_url = None

        # create a header for session.
        self.header = {}
        utcnow = datetime.datetime.utcnow()
        date = utcnow.strftime("%a, %d %b %Y %H:%M:%S GMT")
        authVar = jwt.encode({'iss': self.key}, self.secret, algorithm='HS256')
        authorization = "Bearer %s" % (authVar.decode('utf-8'))
        self.header['date'] = date
        self.header['Authorization'] = authorization

    def run_query(self, sql):

        # prepare the query object and execute the sql
        query_object = {}
        final_url = self.query_job_url
        if self.database == 'realtime':
            query_object['type'] = "realtime"
            query_object['query'] = sql
            query_object['filters'] = {}
            query_object['filters']['live'] = 'true'
            if self.hostname:
                query_object['filters']['hostName'] = self.hostname

        if self.database == 'global':
            query_object['query'] = sql
            query_object['type'] = "global"


        if self.database == 'audit':
            final_url = self.audit_store_url
            query_object['query'] = sql

        _logger.debug(final_url)
        response = requests.post(final_url,
                                 headers=self.header,
                                 json=query_object,
                                 verify=self.verify_ssl)  # type: url response

        return response


    @property
    def current_database(self):
        return self.database

    @property
    def description(self):
        if self._description is None:
            return None
        return self._description

    @property
    def rowcount(self):
        return self._rowcount

    @property
    def status(self):
        return self._status

    def wrap_text(self, text):
        wrapped_text = '\n'.join(line.strip() for line in
                                re.findall(r'.{1,70}(?:\s+|$)', text))
        return wrapped_text.encode('ascii','ignore')

    def hostname_in_resultset(self, asset_id):
        for info in self._json_result['summaries']:
            if asset_id == info['asset']['id']:
                return info['asset']['hostName']
        return asset_id


    def execute(self, sql, arg=None, **kwargs):
        self._result_set = tuple()
        self._description = tuple()
        self._rowcount = -1
        self._arraysize = -1
        self._json_result = {}

        sql_string_array = sql.lower().split()
        sql_string = " ".join(str(x) for x in sql_string_array)
        if sql_string.startswith('show databases', 0,
                                    len('show databases')):
            self.list_databases()
            return self._result_set

        if sql_string.startswith('kill '):
            self.cancel_query(self.query_id)
            return self._result_set

        if sql_string.startswith('show tables descriptions', 0,
                    len('show tables descriptions')):
            if not arg:
                self.get_tables_description()
            else:
                self.get_tables_description(arg[0])
            return self._result_set

        if sql_string.startswith('show tables', 0,
                    len('show tables')):
            self.get_tables()
            return self._result_set

        if sql_string.startswith('show column names', 0,
                                    len('show column names')):
            self.get_columns()
            return self._result_set

        if sql_string.startswith('describe',0, len('describe')):
            if not arg:
                self.describe_table_columns()
            else:
                self.describe_table_columns(arg[0])
            return self._result_set

        if sql_string.startswith('set hostname =', 0,
                                len('set hostname =')):
            if len(sql_string_array) == 4:
                asset_name = sql_string_array[3]

                if ((asset_name.startswith('"') and
                    asset_name.endswith('"')) or
                    (asset_name.startswith("'") and
                    asset_name.endswith("'"))):
                    self.hostname = asset_name[1:-1]
                self._result_set = tuple()
                self._description = tuple()
                self._rowcount = -1
                return self._result_set

        response = self.run_query(sql)

        self.response_to_tuple(response)

        return self._result_set


    # function to get the status of query_id and response
    def query_id_status(self):

        self.query_id_url = self.query_job_url + "/" + self.query_id
        response = requests.get(url=self.query_id_url,
                                headers=self.header,
                                verify=self.verify_ssl)
        if response.status_code == requests.codes.ok:
            json_content = json.loads(response.content.decode('utf-8'))
        else:
            raise OperationalError('ERROR: failed to get query status')
        while (json_content['status'] not in
                    ['FINISHED',
                     'ERROR',
                    'CANCELLED']):
            response = requests.get(url=self.query_id_url,
                                    headers=self.header,
                                    verify=self.verify_ssl)

            if response.status_code == requests.codes.ok:
                json_content = json.loads(response.content.decode('utf-8'))
            else:
                raise OperationalError('ERROR: failed to get query status')

        query_result_url = self.query_id_url + "/results"
        result_response = requests.get(url=query_result_url,
                                       headers=self.header,
                                       verify=self.verify_ssl)
        self.delete_query()

        return json_content, json.loads(result_response.content.decode('utf-8'))


    def delete_query(self):
        # cleanup the query from Uptycs after capturing the data
        delete_query = requests.delete(url=self.query_id_url,
                                       headers=self.header,
                                       verify=self.verify_ssl)
        if delete_query.status_code != requests.codes.ok:
            _logger.info("failed to delete query")


    def cancel_query(self, query_id):

        cancel_json = {"status": "CANCELLED" }
        _logger.debug("URL: %s ", self.query_id_url)
        query_status = requests.put(url=self.query_id_url,
                                    json=cancel_json,
                                    headers=self.header,
                                    verify=self.verify_ssl)
        if query_status.status_code != requests.codes.ok:
            _logger.info("failed to cancel the query")
            self.delete_query()
        else:
            self.delete_query()
            self._description = tuple()
            self._result_set = tuple()
            self._arraysize = -1
            self._rowcount = -1


    # response to tuple converter
    def response_to_tuple(self, response):

        # check if we have content as JSON if not then send the error
        if response.status_code in [ requests.codes.ok, requests.codes.bad]:

            if self.database in ['realtime', 'global']:

                _json_response = json.loads(response.content.decode('utf-8'))
                self.query_id = _json_response['id']
                (query_response_json,
                    json_result) = self.query_id_status()

                if  query_response_json['status'] == 'ERROR':
                    _logger.debug(query_response_json['error'])
                    brief_messg = None
                    detail_messg = None
                    if 'brief' in query_response_json['error']['message']:
                        brief_messg = query_response_json['error']['message']['brief']
                    if 'detail' in query_response_json['error']['message']:
                        detail_messg = query_response_json['error']['message']['detail']
                    if (not brief_messg and detail_messg):
                        self._error = detail_messg
                    elif (not detail_messg and brief_messg):
                        self._error = brief_messg
                    else:
                        self._error = (brief_messg +
                                        '\n' +
                                        detail_messg)

                    # reset all the property elements for tuples
                    self._result_set = tuple()
                    self._description = tuple()
                    self._rowcount = -1
                    self._json_result = {}
                    self._arraysize = -1

                    raise OperationalError(self._error)

                if ('columns' in query_response_json and
                    query_response_json['columns'] and
                    len(query_response_json['columns']) != 0):

                    columns = []
                    description_arr = []
                    if self.database == 'realtime':
                        description_arr.append(tuple(('hostName',
                                                      None,
                                                      None,
                                                      None,
                                                      None,
                                                      None,
                                                      None)))
                    for col in query_response_json['columns']:
                        columns.append(col['name'])
                        description_arr.append(tuple((col['name'],
                                                      None,
                                                      None,
                                                      None,
                                                      None,
                                                      None,
                                                      None)))

                    self._description = tuple(description_arr)

                    if ('items' in json_result and len(
                            json_result['items']) != 0):
                        rows = []

                        if self.database == 'realtime':
                            for item in json_result['items']:
                                row = []
                                row.append(item['asset']['hostName'])
                                for col in columns:
                                    if col in item['rowData']:
                                        row.append(item['rowData'][col])
                                    else:
                                        row.append(None)
                                rows.append(tuple(row))
                        else:
                            for item in json_result['items']:
                                row = []
                                for col in columns:
                                    row.append(item['rowData'][col])
                                rows.append(tuple(row))

                        self._json_result = json_result
                        self._result_set = rows
                        self._arraysize = len(rows)
                        self._rowcount = len(self._result_set)
            else:
                json_result = json.loads(response.content.decode('utf-8'))
                rows = []

                if ('columns' in json_result and len(
                        json_result['columns']) != 0):

                    columns = []
                    description_arr = []

                    for col in json_result['columns']:
                        columns.append(col['name'])
                        description_arr.append(tuple((col['name'],
                                                      None,
                                                      None,
                                                      None,
                                                      None,
                                                      None,
                                                      None)))

                    self._description = tuple(description_arr)

                if ('items' in json_result and len(
                        json_result['items']) != 0):
                    for item in json_result['items']:
                        row = []
                        for col in columns:
                            row.append(item[col])
                        rows.append(tuple(row))

                self._json_result = json_result
                self._result_set = rows
                self._arraysize = len(rows)
                self._rowcount = len(self._result_set)
                if "error" in json_result:
                    error_code = json_result['error']['code']
                    brief_messg = json_result['error']['message']['brief']
                    detail_messg = json_result['error']['message']['detail']
                    self._error = error_code + brief_messg + '\n' + detail_messg

                    # reset all the property elements for tuples
                    self._result_set = tuple()
                    self._description = tuple()
                    self._rowcount = -1
                    self._json_result = {}
                    self._arraysize = -1

                    raise OperationalError(self._error)
        else:


            self._result_set = tuple()
            self._description = tuple()
            self._rowcount = -1
            self._arraysize = -1
            self._json_result = {}

            raise OperationalError(response)


    def get_tables(self):
        if self.database == 'global':
            final_url = self.global_schema_url

        if self.database == 'realtime':
            final_url = self.realtime_schema_url

        if self.database == 'audit':
            description_arr = [('tableName',
                                None,
                                None,
                                None,
                                None,
                                None,
                                None)]
            self._description = tuple(description_arr)
            rows = [('api_audit_logs',)]
            self._result_set = rows
            self._arraysize = len(rows)
            self._rowcount = len(self._result_set)
            return self._result_set

        response = requests.get(final_url, headers=self.header,
                                verify=self.verify_ssl)  # type: url response
        if response.status_code in [ requests.codes.ok, requests.codes.bad]:
            json_result = json.loads(response.content.decode('utf-8'))
        else:
            raise OperationalError(response)

        description_arr = [('tableName',
                            None,
                            None,
                            None,
                            None,
                            None,
                            None)]
        self._description = tuple(description_arr)
        rows = []
        for items in json_result['tables']:
            rows.append(tuple((items['name'],)))
        self._result_set = rows
        self._arraysize = len(rows)
        self._rowcount = len(self._result_set)
        return self._result_set


    def get_tables_description(self, table_like=None):
        if self.database == 'global':
            final_url = self.global_schema_url
            description_arr = [('name',
                                None,
                                None,
                                None,
                                None,
                                None,
                                None),
                               ('description',
                                None,
                                None,
                                None,
                                None,
                                None,
                                None)]
            self._description = tuple(description_arr)

        if self.database == 'realtime':
            description_arr = [('name',
                                None,
                                None,
                                None,
                                None,
                                None,
                                None),
                               ('description',
                                None,
                                None,
                                None,
                                None,
                                None,
                                None)]
            self._description = tuple(description_arr)
            final_url = self.realtime_schema_url

        if self.database == 'audit':
            description_arr = [('name', None, None, None, None, None, None)]
            self._description = tuple(description_arr)
            rows = [('api_audit_logs',)]
            self._result_set = rows
            self._arraysize = len(rows)
            self._rowcount = len(self._result_set)
            return self._result_set

        response = requests.get(final_url,
                                headers=self.header,
                                verify=self.verify_ssl)  # type: url response
        if response.status_code in [ requests.codes.ok,
                                     requests.codes.bad]:
            json_result = json.loads(response.content.decode('utf-8'))
        else:
            raise OperationalError(response)

        rows = []
        for items in json_result['tables']:
            if table_like:
                if table_like in items['name']:
                    rows.append(tuple((items['name'],
                                       self.wrap_text(items['description']),)))
            else:
                rows.append(tuple((items['name'],
                                   self.wrap_text(items['description']),)))
        self._result_set = rows
        self._arraysize = len(rows)
        self._rowcount = len(self._result_set)
        return self._result_set


    def get_columns(self, table_like=None):

        description_arr = [('tableName',
                            None,
                            None,
                            None,
                            None,
                            None,
                            None),
                           ('columnName',
                            None,
                            None,
                            None,
                            None,
                            None,
                            None)]
        self._description = tuple(description_arr)

        if self.database == 'global':
            final_url = self.global_schema_url
        if self.database == 'realtime':
            final_url = self.realtime_schema_url
        if self.database == 'audit':
            response = self.run_query('SELECT * FROM api_audit_logs WHERE 1=2')
        else:
            response = requests.get(final_url,
                                    headers=self.header,
                                    verify=self.verify_ssl)

        if response.status_code in [ requests.codes.ok,
                                     requests.codes.bad]:
            json_result = json.loads(response.content.decode('utf-8'))
        else:
            raise OperationalError(response)

        rows = []

        if self.database == 'audit':
            if (table_like == 'api_audit_logs' and
                    'columns' in json_result):
                for col in json_result['columns']:
                    rows.append(tuple((table_like, col['name'])))
                self._result_set = rows
                self._arraysize = len(rows)
                self._rowcount = len(self._result_set)
                return self._result_set

        for items in json_result['tables']:
            if table_like:
                if table_like == items['name']:
                    for col in items['columns']:
                        rows.append(tuple((items['name'], col['name'])))
            else:
                for col in items['columns']:
                    rows.append(tuple((items['name'], col['name'])))
        self._result_set = rows
        self._arraysize = len(rows)
        self._rowcount = len(self._result_set)
        return self._result_set


    def describe_table_columns(self, table_like=None):

        if not table_like:
            raise OperationalError("ERROR: DESCRIBE requires a table name")

        if self.database == 'global':
            final_url = self.global_schema_url
            description_arr = [('name',
                                None,
                                None,
                                None,
                                None,
                                None,
                                None),
                               ('type',
                                None,
                                None,
                                None,
                                None,
                                None,
                                None),
                               ('description',
                                None,
                                None,
                                None,
                                None,
                                None,
                                None)]
            self._description = tuple(description_arr)

        if self.database == 'realtime':
            final_url = self.realtime_schema_url
            description_arr = [('name',
                                None,
                                None,
                                None,
                                None,
                                None,
                                None),
                               ('type',
                                None,
                                None,
                                None,
                                None,
                                None,
                                None),
                               ('description',
                                None,
                                None,
                                None,
                                None,
                                None,
                                None)]
            self._description = tuple(description_arr)

        if self.database == 'audit':
            response = self.run_query('SELECT * FROM api_audit_logs WHERE 1=2')
        else:
            response = requests.get(final_url,
                                    headers=self.header,
                                    verify=self.verify_ssl)  # type: url

        if (response.status_code in [ requests.codes.ok,
                                     requests.codes.bad]):
            json_result = json.loads(response.content.decode('utf-8'))
        else:
            raise OperationalError(response)

        rows = []

        if self.database == 'audit':
            description_arr = [('tableName',
                                None,
                                None,
                                None,
                                None,
                                None,
                                None),
                               ('columnName',
                                None,
                                None,
                                None,
                                None,
                                None,
                                None)]
            self._description = tuple(description_arr)
            if (table_like == 'api_audit_logs'
                    and 'columns' in json_result):
                for col in json_result['columns']:
                    rows.append(tuple((table_like,
                                       col['name'])))
                self._result_set = rows
                self._arraysize = len(rows)
                self._rowcount = len(self._result_set)
                return self._result_set

        for items in json_result['tables']:
            if table_like:
                if table_like == items['name']:
                    for col in items['columns']:
                        if 'description' in col:
                            col_description = self.wrap_text(col['description'])
                        else:
                            col_description = None
                        rows.append(tuple((col['name'],
                                           col['type'],
                                           col_description)))
        self._result_set = rows
        self._arraysize = len(rows)
        self._rowcount = len(self._result_set)
        return self._result_set


    def list_databases(self):
        description_arr = [('seq',
                            None,
                            None,
                            None,
                            None,
                            None,
                            None),
                           ('name',
                            None,
                            None,
                            None,
                            None,
                            None,
                            None),
                           ('description',
                            None,
                            None,
                            None,
                            None,
                            None,
                            None)]
        self._description = tuple(description_arr)
        rows = [(1, 'global', 'Global store'),
                (2, 'realtime', 'Real time store'),
                (3, 'audit', 'Audit store')]
        self._result_set = rows
        self._arraysize = len(rows)
        self._rowcount = len(self._result_set)
        return self._result_set

    # Overloading len function for this class
    def __len__(self):
        if self._result_set is None:
            return 0
        return len(self._result_set)

    # overloading list function for this class
    def __list__(self):
        return self._result_set

    def __iter__(self):
        self.num = 0
        return self

    def __next__(self):
        if (self.num >= self._rowcount):
            raise StopIteration
        result = self._result_set[self.num]
        self.num += 1
        return result

    def next(self):
        if (self.num >= self._rowcount):
            raise StopIteration
        result = self._result_set[self.num]
        self.num += 1
        return result

    def fetchall(self):

        result_set = self._result_set
        self._result_set = tuple()
        self._rowcount = -1
        self._arraysize = -1
        self._json_result = {}
        return result_set

    def commit(self):
        pass

    def rollback(self):
        raise NotSupportedError

    def close(self):
        self._result_set = tuple()
        self._description = tuple()
        self._rowcount = -1
        self._status = False
        self._arraysize = -1
        self._json_result = {}
        pass

