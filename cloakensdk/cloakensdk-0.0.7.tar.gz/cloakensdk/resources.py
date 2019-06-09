import requests
from datetime import datetime
from cloakensdk.client import Client


class Resource(object):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    OPTIONS= "OPTIONS"

    def __init__(self,client,method=None):
        self.client=client
        self.base = self.client.server_url+"api/"
        self.endpoint=None  # assign endpoint to append to self.base
        self.request_url=None  # final url to make the request call
        self.method = method
        self.valid_codes = {Resource.GET:[200],
                            Resource.POST:[201,200],
                            Resource.DELETE:[200]}
        self.json={}  # any json data to send with request
        self.params={}  # any query string parameters to send with request
        self.headers={}  # any headers to send with request

    def full_request(self):
        """
        returns response and data for sync requests
        :param headers:
        :param method:
        :param path:
        :param json:
        :param params:
        :param valid_codes
        :return:
        """
        r = self.request()
        return self.data(r)

    def request(self):
        """
        For async requests  self.response is set to a future
        For synchronous requests self.response is set to the response
        :param headers:
        :param method:
        :param path:
        :param json:
        :param params:
        :return:
        """
        #expired = True
        expired = True if datetime.utcnow().timestamp() > self.client.expire-30 else False # 30 second buffer
        if expired:
            self.client.refresh_call()
        headers_req = {} if self.headers is None else self.headers
        headers_req["Authorization"]="Bearer "+self.client.access_token
        headers_req["Content-Type"]=self.client.header_format
        return self.client.session.request(self.method,
                                 json=self.json,
                                 url=self.request_url,
                                 params=self.params,
                                 headers=headers_req)

    def data(self, response):
        """
        Test for html error code and return data
        :param response
        :return:
        """
        actual_response = self.client.get_actual_response(response)
        result = {}
        if actual_response.status_code in self.valid_codes[self.method]:
            result["status"] = "Success"
            result["response_code"] = actual_response.status_code
            result["data"] = actual_response.json()
        else:
            result["status"] = "Failed"
            result["response_code"] = actual_response.status_code
            result["data"] = actual_response.content.decode('utf8')
        return result


class ResourcePaged(Resource):

    def __init__(self,client,method=Resource.GET):
        super(ResourcePaged,self).__init__(client,method)
        self.first=True
        self.next=None #data field with next url
        self.previous=None #data field with previous url
        # for next if null we are done paging

    def __iter__(self):
        return self

    def __next__(self):
        if self.next is not None or self.first is not False:
            self.first=False
            if self.next is not None:
                self.request_url=self.next
            response = super(ResourcePaged,self).full_request()
            self.next = response["data"]["next"]
        else:
            raise StopIteration


class Url(ResourcePaged):

    def __init__(self,client:Client, method=Resource.GET):
        """
        For options make an OPTIONS request
        :param client:
        """
        super(Url,self).__init__(client,method)
        self.endpoint = "urls/"

    def create(self,url:str,
               unshortened_url:str
                ):
        self.request_url='{base}{endpoint}'.format(base=self.base,
                                                     endpoint=self.endpoint)

        """
        +--------+--------------------------------------------------------------------------+
        | HTTP | CRUD 
        += == == == = == == == == == == == == == == == == == == == == == == == == == == == ==
        +--------+--------------------------------------------------------------------------+
        | POST | / api / urls /
        +--------+--------------------------------------------------------------------------+
        """

        self.method=Resource.POST
        self.json["url"]=url
        self.json["unshortened_url"]=unshortened_url

    def unshorten(self,url:str):
        """

        +--------+--------------------------------------------------------------------------+
        | HTTP | Action
        += == == == = == == == == == == == == == == == == == == == == == == == == == == == ==
        +--------+--------------------------------------------------------------------------+
        | POST | / api / urls / {action} /
        +--------+--------------------------------------------------------------------------+
        """

        self.request_url='{base}{endpoint}{action}'.format(base=self.base,
                                                   endpoint=self.endpoint,
                                                action="unshorten/")
        self.method=Resource.POST
        self.json={"url":url}

