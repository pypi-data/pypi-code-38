import requests
from .HTTPError import HTTPError

class API: 
    def __init__(self, host):
        if host[-1:] != "/":
            host = host + "/"

        self.host = host
        self.headers = {}

    def set_header(self, header, value):
        self.headers[header] = value
        return self

    def set_headers(self, headers):
        self.headers = headers
        return self

    def post(self, endpoint, json = {}):
        r = requests.post(self.host + endpoint, headers=self.headers, json=json) 

        if r.status_code > 299:
            raise HTTPError(r.json())

        if len(r.content) == 0:
            return r
            
        return r.json()

    def get(self, endpoint):
        r = requests.get(self.host + endpoint, headers=self.headers)

        if r.status_code > 299:
            raise HTTPError(r.json())

        if len(r.content) == 0:
            return r
            
        return r.json()

    def delete(self, endpoint):
        r = requests.delete(self.host + endpoint, headers=self.headers)

        if r.status_code > 299:
            raise HTTPError(r.json())

        if len(r.content) == 0:
            return r
            
        return r.json()