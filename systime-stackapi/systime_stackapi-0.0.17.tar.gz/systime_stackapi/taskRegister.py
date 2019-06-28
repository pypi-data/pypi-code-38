from .authenticator import Authenticator
from base64 import b64encode, b64decode
from urllib.parse import urlparse
from functools import lru_cache
import requests
import json


class TaskRegister(Authenticator):
    def __init__(self, service_url, client_key_id, shared_secret, **kwargs):
        self.service_url = service_url
        self.service_token = 'TaskRegister'
        self.timeout = kwargs.get('timeout', 5)
        super().__init__(client_key_id, shared_secret, **kwargs)

    def get_task(self, task_id):
        path = '/task/{}'.format(task_id)

        bearer_token = self.get_service_bearer_token(self.service_token)
        r = requests.get(self.service_url + path, headers={'Content-Type': 'application/json', 'Authorization': bearer_token}, timeout=self.timeout)
        r.raise_for_status()
        return(json.loads(r.text))


    def create_task(self, description):
        path = '/task/'

        payload = {
                   'description': description
                  }

        bearer_token = self.get_service_bearer_token(self.service_token)
        r = requests.post(self.service_url + path, data=json.dumps(payload), headers={'Content-Type': 'application/json', 'Authorization': bearer_token}, timeout=self.timeout)
        r.raise_for_status()
        return(json.loads(r.text))

    def create_subtask(self, task_id, task_key, description):
        path = '/task/{}/subtask'.format(task_id)

        payload = {
                   'description': description,
                   'task_key': task_key
                  }

        bearer_token = self.get_service_bearer_token(self.service_token)
        r = requests.post(self.service_url + path, data=json.dumps(payload), headers={'Content-Type': 'application/json', 'Authorization': bearer_token}, timeout=self.timeout)
        r.raise_for_status()
        return(json.loads(r.text))

    def create_event(self, task_id, subtask_id, task_key, description):
        path = '/task/{}/subtask/{}/event'.format(task_id, subtask_id)

        payload = {
                   'description': description,
                   'task_key': task_key
                  }

        bearer_token = self.get_service_bearer_token(self.service_token)
        r = requests.post(self.service_url + path, data=json.dumps(payload), headers={'Content-Type': 'application/json', 'Authorization': bearer_token}, timeout=self.timeout)
        r.raise_for_status()
        return(json.loads(r.text))

    def update_task(self, task_id, task_key, status):
        path = '/task/{}'.format(task_id)

        payload = {
                   'task_key': task_key,
                   'status': status
                  }

        bearer_token = self.get_service_bearer_token(self.service_token)
        r = requests.put(self.service_url + path, data=json.dumps(payload), headers={'Content-Type': 'application/json', 'Authorization': bearer_token}, timeout=self.timeout)
        r.raise_for_status()
        return(json.loads(r.text))

    def update_subtask(self, task_id, subtask_id, task_key, status):
        path = '/task/{}/subtask/{}'.format(task_id, subtask_id)

        payload = {
                   'task_key': task_key,
                   'status': status
                  }

        bearer_token = self.get_service_bearer_token(self.service_token)
        r = requests.put(self.service_url + path, data=json.dumps(payload), headers={'Content-Type': 'application/json', 'Authorization': bearer_token}, timeout=self.timeout)
        r.raise_for_status()
        return(json.loads(r.text))
