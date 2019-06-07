from __future__ import absolute_import
from __future__ import unicode_literals

import json
import jwt
import datetime
import requests
import urllib3

__all__ = [
    'ERROR', 'Warning',
    'InterfaceERROR', 'DatabaseERROR',
    'InternalERROR', 'OperationalERROR',
    'ProgrammingERROR', 'DataERROR', 'NotSupportedERROR',
]


class ERROR(Exception):
    pass


class Warning(Exception):
    pass


class InterfaceERROR(ERROR):
    pass


class DatabaseERROR(ERROR):
    pass


class InternalERROR(DatabaseERROR):
    pass


class OperationalERROR(DatabaseERROR):
    pass


class ProgrammingERROR(DatabaseERROR):
    pass


class IntegrityERROR(DatabaseERROR):
    pass


class DataERROR(DatabaseERROR):
    pass


class NotSupportedERROR(DatabaseERROR):
    pass



class uptycs_rest_call(object):


    def __init__(self, url=None,
                 customer_id=None,
                 key=None,
                 secret=None,
                 verify_ssl=False,
                 api=None,
                 method=None,
                 post_data=None,
                 media_type = None,
                 **kwargs):

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.baseurl = url
        self.customer_id = customer_id
        self.final_url = ("%s/public/api/customers/%s%s" %
                          (url, customer_id, api))
        self.key = key
        self.secret = secret
        self.method = method
        self.verify_ssl = verify_ssl
        self.post_data = post_data
        self.media_type = media_type

        self.header = {}
        utcnow = datetime.datetime.utcnow()
        date = utcnow.strftime("%a, %d %b %Y %H:%M:%S GMT")
        authVar = jwt.encode({'iss': self.key}, self.secret, algorithm='HS256')
        authorization = "Bearer %s" % (authVar.decode('utf-8'))
        self.header['date'] = date
        self.header['Authorization'] = authorization

        self._is_response_json = False
        self._error = None
        self._response_content = None


    @property
    def is_response_json(self):
        return self._is_response_json


    @property
    def response_content(self):
        return self._response_content


    @property
    def errir(self):
        return self._error

    def rest_api_call(self):

        if self.method.lower() == 'get' :
            try:
                response = requests.get(url=self.final_url,
                                        headers=self.header,
                                        verify=self.verify_ssl)
                if (response and response.status_code in
                        [requests.codes.ok, requests.codes.bad]):
                    self._is_response_json = True
                self._response_content = response.content.decode('utf-8')
            except requests.exceptions.RequestException as e:
                self._error = "ERROR: {}".format(e)
                raise OperationalERROR(self._error)

        elif self.method.lower() == 'post':
            if self.post_data:
                try:
                    response = requests.post(url=self.final_url,
                                             headers=self.header,
                                             json=self.post_data,
                                             verify=self.verify_ssl,
                                             timeout=None)
                    if (response and response.status_code in
                              [requests.codes.ok, requests.codes.bad]):
                        self._is_response_json = True
                    self._response_content = response.content.decode('utf-8')
                except requests.exceptions.RequestException as e:
                    self._error = "ERROR: {}".format(e)
                    raise OperationalERROR(self._error)

            else:
                raise OperationalERROR("ERROR: with post method. "
                                        "please pass post data json")

        elif self.method.lower() == 'put':
            if self.post_data:
                try:
                    response = requests.put(url=self.final_url,
                                              headers=self.header,
                                              json=self.post_data,
                                              verify=self.verify_ssl,
                                              timeout=None)
                    if (response and response.status_code in
                            [requests.codes.ok, requests.codes.bad]):
                        self._is_response_json = True
                    self._response_content = response.content.decode('utf-8')
                except requests.exceptions.RequestException as e:
                    self._error = "ERROR: {}".format(e)
                    raise OperationalERROR(self._error)

            else:
                raise OperationalERROR("ERROR: with put method. "
                                    "please pass post data json")

        elif self.method.lower() == 'delete':
            try:
                response = requests.delete(url=self.final_url,
                                           headers=self.header,
                                           verify=self.verify_ssl,
                                           timeout=None)
                if (response and response.status_code in [requests.codes.ok,
                                     requests.codes.bad]):
                    self._is_response_json = False
                self._response_content = response.content.decode('utf-8')
            except requests.exceptions.RequestException as e:
                self._error = "ERROR: {}".format(e)
                raise OperationalERROR(self._error)
        else:
            raise OperationalERROR("ERROR: Unknown request")


