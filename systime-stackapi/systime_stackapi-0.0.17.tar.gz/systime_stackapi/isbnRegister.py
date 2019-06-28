from .authenticator import Authenticator
from base64 import b64encode, b64decode
from urllib.parse import urlparse
from functools import lru_cache
import requests
import json


class ISBNRegister(Authenticator):
    def __init__(self, service_url, client_key_id, shared_secret, **kwargs):
        self.service_url = service_url
        self.service_token = 'ISBNRegister'
        self.timeout = kwargs.get('timeout', 5)
        super().__init__(client_key_id, shared_secret, **kwargs)

    def create_isbn(self, isbn, domain, customer, description=None):
        path = '/isbn/%s' % isbn

        payload = {
                   'domain': domain,
                   'customer': customer,
                  }

        if description is not None:
            payload['description'] = description

        bearer_token = self.get_service_bearer_token(self.service_token)
        r = requests.post(self.service_url + path, data=json.dumps(payload), headers={'Content-Type': 'application/json', 'Authorization': bearer_token}, timeout=self.timeout)
        r.raise_for_status()
        return(json.loads(r.text))

    def update_isbn(self, isbn, domain, customer, description=None):
        path = '/isbn/%s' % isbn

        payload = {
                   'domain': domain,
                   'customer': customer,
                  }

        if description is not None:
            payload['description'] = description

        bearer_token = self.get_service_bearer_token(self.service_token)
        r = requests.put(self.service_url + path, data=json.dumps(payload), headers={'Content-Type': 'application/json', 'Authorization': bearer_token}, timeout=self.timeout)
        r.raise_for_status()
        return(json.loads(r.text))

    def get_isbn(self, isbn):
        path = '/isbn/%s' % isbn

        bearer_token = self.get_service_bearer_token(self.service_token)
        r = requests.get(self.service_url + path, headers={'Content-Type': 'application/json', 'Authorization': bearer_token}, timeout=self.timeout)
        r.raise_for_status()
        return(json.loads(r.text))

    def delete_isbn(self, isbn):
        path = '/isbn/%s' % isbn

        bearer_token = self.get_service_bearer_token(self.service_token)
        r = requests.delete(self.service_url + path, headers={'Content-Type': 'application/json', 'Authorization': bearer_token}, timeout=self.timeout)
        r.raise_for_status()
        return(json.loads(r.text))
