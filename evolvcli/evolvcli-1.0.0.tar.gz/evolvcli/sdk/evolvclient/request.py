import requests

from urllib import parse

from .util import EvolvError
from .collections import ACCOUNTS, METAMODELS, ENVIRONMENTS, EXPERIMENTS, CANDIDATES


class EvolvRequest:

    COLLECTION_TO_PATH = {
        ACCOUNTS: 'https://{domain}/{version}/accounts',
        METAMODELS: 'https://{domain}/{version}/accounts/{account_id}/metamodels',
        ENVIRONMENTS: 'https://{domain}/{version}/accounts/{account_id}/environments',
        EXPERIMENTS: 'https://{domain}/{version}/accounts/{account_id}/metamodels/{metamodel_id}/experiments',
        CANDIDATES: 'https://{domain}/{version}/accounts/{account_id}/metamodels/{metamodel_id}/'
                    'experiments/{experiment_id}/candidates'
    }

    def __init__(self, config=None):
        """Instantiates the EvolvRequest instance.

        :param EvolvConfig config: the configuration of the account
        """
        self._config = config

    class BadResponse(EvolvError):
        """Raised when the request to the Experiment API returns response code >= 400"""
        pass

    @property
    def headers(self):
        """Headers to be sent with all requests.

        :return: dictionary of headers
        :rtype: dict
        """
        header_obj = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        if self._config.bearer_token:
            header_obj['Authorization'] = 'Bearer {}'.format(self._config.bearer_token)
        elif self._config.api_key:
            header_obj['Authorization'] = 'Api-Key {}'.format(self._config.api_key)
        else:
            raise Exception("No Authentication credentials supplied in the configuration.")

        return header_obj

    def request_path(self, collection, entity_id=None, content_only=False, query=None, account_id=None,
                     metamodel_id=None, experiment_id=None):
        """Generates a path for the request being sent to the Experiment API.

        :param string collection: the entity being requested
        :param guid entity_id: the unique identifier of the entity being requested
        :param boolean content_only: determines whether call is purely for object's content
        :param dict query: query for the underlying graph database
        :param string account_id: unique identifier for an account
        :param string metamodel_id: unique identifier for an metamodel
        :param string experiment_id: unique identifier for an experiment
        :return: a valid experiment api path
        :rtype: string
        """
        url = self.COLLECTION_TO_PATH[collection].format(domain=self._config.api_domain,
                                                         version=self._config.api_version, account_id=account_id,
                                                         metamodel_id=metamodel_id, experiment_id=experiment_id)

        if entity_id:
            url += '/{}'.format(entity_id)

        if content_only:
            url += '/content'

        if query:
            url += '?{}'.format(parse.urlencode(query))

        return url

    def get(self, collection, entity_id, content_only=False, version=None, account_id=None, metamodel_id=None,
            experiment_id=None):
        """Performs a get request to the Experiment API.

        :param string collection: the entity being requested
        :param guid entity_id: the unique identifier of the entity being requested
        :param boolean content_only:  determines whether call is purely for object's content
        :param string version: version of the content being requested
        :param string account_id: unique identifier for an account
        :param string metamodel_id: unique identifier for an metamodel
        :param string experiment_id: unique identifier for an experiment
        :return: a single json object
        :rtype: dict
        """
        if version:
            request_url = self.request_path(collection, entity_id=entity_id, content_only=content_only,
                                            query={'version': version}, account_id=account_id,
                                            metamodel_id=metamodel_id, experiment_id=experiment_id)
        else:
            request_url = self.request_path(collection, entity_id=entity_id, content_only=content_only,
                                            account_id=account_id, metamodel_id=metamodel_id,
                                            experiment_id=experiment_id)

        response = requests.get(request_url, headers=self.headers)

        if not response.ok:
            raise self.BadResponse('GET request failed for {} with status code {} and'
                                   ' response message: {}'.format(collection,
                                                                  response.status_code,
                                                                  response.content.decode()))

        return self.json_response(response)

    def query(self, collection, query=None, account_id=None, metamodel_id=None, experiment_id=None):
        """Performs a get request with query params attached.

        :param string collection: the entity being requested
        :param string query: query for the underlying graph database
        :param string account_id: unique identifier for an account
        :param string metamodel_id: unique identifier for an metamodel
        :param string experiment_id: unique identifier for an experiment
        :return: list of json objects
        :rtype: list
        """
        if query:
            request_url = self.request_path(collection, query={'query': query}, account_id=account_id,
                                            metamodel_id=metamodel_id, experiment_id=experiment_id)
        else:
            request_url = self.request_path(collection, account_id=account_id, metamodel_id=metamodel_id,
                                            experiment_id=experiment_id)

        response = requests.get(request_url, headers=self.headers)

        if not response.ok:
            raise self.BadResponse(
                'GET request failed for {} with status code {} and response message: {}'.format(collection,
                                                                                                response.status_code,
                                                                                                response.content))

        return self.json_response(response, many=True)

    def post(self, collection, json, account_id=None, metamodel_id=None, experiment_id=None):
        """Performs a post request to the Experiment API.

        :param string collection: the entity being added
        :param dict json: the payload to be sent
        :param string account_id: unique identifier for an account
        :param string metamodel_id: unique identifier for an metamodel
        :param string experiment_id: unique identifier for an experiment
        :return: a single json object
        :rtype: dict
        """
        request_url = self.request_path(collection, account_id=account_id, metamodel_id=metamodel_id,
                                        experiment_id=experiment_id)

        response = requests.post(request_url, json=json, headers=self.headers)

        if not response.ok:
            raise self.BadResponse(
                'POST request failed for {} with status code {} and response message: {}'.format(collection,
                                                                                                 response.status_code,
                                                                                                 response.content))

        return self.json_response(response)

    def put(self, collection, entity_id, json, account_id=None, metamodel_id=None, experiment_id=None):
        """Performs a put request to the experiment api

        :param string collection: the entity being modified
        :param guid entity_id: the unique identifier of the entity being requested
        :param dict json: the payload to be sent
        :param string account_id: unique identifier for an account
        :param string metamodel_id: unique identifier for an metamodel
        :param string experiment_id: unique identifier for an experiment
        :return: a single json object
        :rtype: dict
        """
        request_url = self.request_path(collection, entity_id=entity_id, account_id=account_id,
                                        metamodel_id=metamodel_id, experiment_id=experiment_id)

        response = requests.put(request_url, json=json, headers=self.headers)

        if not response.ok:
            raise self.BadResponse(
                'PUT request failed for {} with status code {} and response message: {}'.format(collection,
                                                                                                response.status_code,
                                                                                                response.content))

        return self.json_response(response)

    def patch(self, collection, entity_id, json, account_id=None, metamodel_id=None, experiment_id=None):
        """Performs a patch request to the experiment api

        :param string collection: the entity being modified
        :param guid entity_id: the unique identifier of the entity being requested
        :param dict json: the payload to be sent
        :param string account_id: unique identifier for an account
        :param string metamodel_id: unique identifier for an metamodel
        :param string experiment_id: unique identifier for an experiment
        :return: a single json object
        :rtype: dict
        """
        request_url = self.request_path(collection, entity_id=entity_id, account_id=account_id,
                                        metamodel_id=metamodel_id, experiment_id=experiment_id)

        response = requests.patch(request_url, json=json, headers=self.headers)

        if not response.ok:
            raise self.BadResponse(
                'PATCH request failed for {} with status code {} and response message: {}'.format(collection,
                                                                                                  response.status_code,
                                                                                                  response.content))

        return self.json_response(response)

    @staticmethod
    def json_response(r, many=False):
        """Translates the response of the experiment API to json even if its empty.

        :param Response r: a response instance
        :param boolean many: indicates whether response is a Json list or not
        :return: a json representation of the response content
        :rtype: dict
        """
        if not r.content and not many:
            return {}
        elif not r.content and many:
            return []

        content_type = r.headers.get('Content-Type')
        if content_type == 'application/yaml':
            return {
                'response_yaml': True,
                'content': r.content.decode()
            }

        return r.json()
