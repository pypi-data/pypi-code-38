# -*- coding: utf-8 -*-

import requests
import simplejson as json
import urllib3

from omxware import OmxResponse
from omxware.config.Configuration import Configuration
from omxware.exceptions.ServiceException import ServiceException

# Disable the SSL warning
urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Connection:
    """OMXWare connect class"""
    hosturl = ''
    token = ''
    # session: requests.Session
    # config: Configuration
    headers = {}

    def __init__(self, config: Configuration):
        self.__config = config
        self.__hosturl = config.server_url()
        self.__token = config.token()

    def __setHeaders(self):
        self.__token = self.__config.token()
        self.token = self.config().auth_token()
        user_email = self.__config.user_info().get('email')
        self.__headers = {
                        'From': ''+user_email,
                        'User-Agent': 'application/json',
                        'Authorization': 'Bearer '+self.token
                      }

    def connect(self):
        self.__token = self.__config.token()

        """Connect to the OMXWare services"""
        self.__session = requests.Session()
        self.__setHeaders()

    def config(self):
        return self.__config

    def get(self, methodurl, headers: {}, payload=None):
        """Issue a HTTP GET request

        Arguments:
          methodurl -- relative path to the GET method
          headers -- HTTP headers
          payload -- (optional) additional payload (HTTP body)
        """

        self.connect()

        if self.__session is None:
            raise Exception("No connection has been established")

        headers.update(self.__headers)
        response = self.__session.get(
                                        self.__hosturl + methodurl,
                                        verify=False,
                                        params=payload,
                                        headers=headers
                                        )

        # TODO: OmxResponse should be able to handle the response.status_code as well
        if response.status_code < 200 or response.status_code >= 300:
            raise self._process_http_response(response)

        r = OmxResponse.OmxResponse(self, response)
        return r

    def get_file(self, methodurl, headers: {}, payload=None):
        """Issue a HTTP GET request to get a files as a String

        Arguments:
          methodurl -- relative path to the GET method
          headers -- HTTP headers
          payload -- (optional) additional payload (HTTP body)
        """

        self.connect()

        if self.__session is None:
            raise Exception("No connection has been established")

        headers.update(self.__headers)
        response = self.__session.get(
                                        self.__hosturl + methodurl,
                                        verify=False,
                                        params=payload,
                                        headers=headers
                                        )

        # TODO: OmxResponse should be able to handle the response.status_code as well
        if response.status_code < 200 or response.status_code >= 300:
            raise self._process_http_response(response)

        r = response.text
        return r

    def post(self, methodurl, parameters=None, headers={}, files=None):
        """Issue a HTTP POST request

        Arguments:
        methodurl -- relative path to the POST method
        parameters -- (optional) form parameters
        headers -- (optional) HTTP headers
        files -- (optional) multi-part form file content
        """

        self.connect()

        if self.__session is None:
            raise Exception("No connection has been established")

        headers.update(self.__headers)
        response = self.__session.post(
                                        self.__hosturl + methodurl,
                                        data=parameters,
                                        verify=False,
                                        headers=headers,
                                        files=files
                                        )

        if response.status_code < 200 or response.status_code >= 300:
            raise self._process_http_response(response)

        return OmxResponse(self, response)

    def delete(self, methodurl, headers={}, payload=None):
        """Issue a HTTP DELETE request

        Arguments:
        methodurl -- relative path to the POST method
        headers -- HTTP headers
        payload -- (optional) additional payload (HTTP body)
        """

        self.connect()

        if self.__session is None:
            raise Exception("No connection has been established")

        headers.update(self.headers)

        response = self.__session.delete(self.hosturl + methodurl, verify=False, params=payload, headers=headers)

        if response.status_code < 200 or response.status_code >= 300:
            raise self._process_http_response(response)
        return response

    def disconnect(self):
        """Disconnect from OMXWare services"""
        if self.__session is None:
            raise Exception("No connection has been established")

        self.__session.close()
        self.__session = None

    def _process_http_response(self, response):
        """Internal method for processing HTTP response"""
        try:
            responseJ = json.loads(response.text)
        except SyntaxError:
            return ServiceException(response.text, response.status_code)
        except ValueError:
            return ServiceException(response.text, response.status_code)
        return ServiceException(responseJ['message'], response.status_code)
