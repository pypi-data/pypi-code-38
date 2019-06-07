import requests
from datetime import datetime
from requests_futures.sessions import FuturesSession


class RequestError(Exception):
    def __init__(self,message):
        super(Exception,self).__init__(message)
        self.message = message


class Client(object):
    REFRESH = 240 # 4 minutes less than time out for async request compatibility
    GET = "GET"
    POST = "POST"
    FORMAT_JSON = "application/json"
    FORMAT_XML = "application/json"

    def __init__(self, server_url:str,
                 username:str,
                 password:str,
                 format:str = FORMAT_JSON):
        self.username=username
        self.password=password
        self.login_data = {"username": self.username,"password": self.password}
        self.server_url = server_url + "/" if server_url[-1] != "/" else server_url
        self.session = None  # request session  or future session

        self.header_format=format

        self.access_token = None
        self.refresh_token = None

        self.access_header= None
        self.access_payload= None
        self.access_sig= None

        self.refresh_header=None
        self.refresh_payload=None
        self.refresh_sig=None

        self.expire = None

    def refresh_call(self):
        headers={}
        headers["Content-Type"]=self.header_format
        data = {"refresh":self.refresh_token}
        r = self.session.post(self.server_url+"api/token-refresh/",
                                 json=data,
                                 headers=headers)
        if r.status_code == requests.codes.ok:
            self._set_keys(r)
        else:
            raise RequestError("refresh failed:" + str(r.status_code) + " " + r.text)

    @staticmethod
    def get_actual_response(response):
        """
        will return actual data from request
        :return:
        """
        raise NotImplemented("not implemented")

    def initialize(self):
        """
        initializes tokens and timeouts
        call _set_keys after making request for authorization
        :return:
        """
        raise NotImplemented("not implemented")

    def _set_keys(self, response:requests.Response):
        if response.status_code == requests.codes.ok:
            self.access_token = response.json()["access"]
            import base64
            access_parts = self.access_token.split(".")
            self.access_header= base64.urlsafe_b64decode(access_parts[0].encode('ascii')+b'===')
            self.access_payload= base64.urlsafe_b64decode(access_parts[1].encode('ascii')+b'===')
            self.access_sig= base64.urlsafe_b64decode(access_parts[2].encode('ascii')+b'===')

            if "refresh" in response.json():
                self.refresh_token = response.json()["refresh"]
                refresh_parts = self.refresh_token.split(".")
                self.refresh_header=base64.urlsafe_b64decode(refresh_parts[0].encode('ascii')+b'===')
                self.refresh_payload=base64.urlsafe_b64decode(refresh_parts[1].encode('ascii')+b'===')
                self.refresh_sig=base64.urlsafe_b64decode(refresh_parts[2].encode('ascii')+b'===')
                import json
                self.expire = json.loads(self.refresh_payload)['exp']
        else:
            raise RequestError("set keys failed: " + str(response.status_code) + " " + str(response.text))


class AsyncClient(Client):
    def __init__(self,server_url:str,username:str,password:str):
        super(AsyncClient,self).__init__(server_url,username,password)
        self.session = FuturesSession()
        self.initialize()

    def initialize(self):
        headers={}
        headers["Content-Type"]=self.header_format

        future = self.session.post(self.server_url+"api/token-auth/",
                                   json=self.login_data,
                                   headers=self.header_format)
        r = future.result()
        if r.status_code == requests.codes.ok:
            self._set_keys(self.get_actual_response(r))
        else:
            raise RequestError("initialize failed:" + str(r.status_code) + " " + r.text)


    @staticmethod
    def get_actual_response(response):
        """
        returns the actual response from the future
        :param self:
        :param response:
        :return:
        """
        return response.result()


class SyncClient(Client):

    def __init__(self,server_url:str,username:str,password:str):
        super(SyncClient,self).__init__(server_url,username,password)
        self.session = requests.session()
        self.initialize()

    def initialize(self):
        headers={}
        headers["Content-Type"]=self.header_format
        r = self.session.post(self.server_url+"api/token-auth/",
                              json=self.login_data, headers=headers)
        if r.status_code == requests.codes.ok:
            self._set_keys(self.get_actual_response(r))
        else:
            raise RequestError("initialize failed:" + str(r.status_code) + " " + r.text)


    @staticmethod
    def get_actual_response(response):
        """
        returns the response
        :param response:
        :return:
        """
        return response

