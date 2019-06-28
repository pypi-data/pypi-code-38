import time
import requests
import singer
import json

from tap_framework.client import BaseClient


LOGGER = singer.get_logger()


class ChargebeeClient(BaseClient):

    def __init__(self, config, api_result_limit=100, include_deleted=True):
        super().__init__(config)

        self.api_result_limit = api_result_limit
        self.include_deleted = include_deleted
        self.user_agent = self.config.get('user_agent')

    def get_headers(self):
        headers = {}

        if self.config.get('user_agent'):
            headers['User-Agent'] = self.config.get('user_agent')

        return headers

    def get_params(self, params):

        if params is None:
            params = {}

        params['limit'] = self.api_result_limit
        params['include_deleted'] = self.include_deleted

        return params

    def make_request(self, url, method, params=None, body=None):

        if params is None:
            params = {}

        LOGGER.info("Making {} request to {}".format(method, url))

        response = requests.request(
            method,
            url,
            auth=(self.config.get("api_key"), ''),
            headers=self.get_headers(),
            params=self.get_params(params),
            json=body)

        response.raise_for_status()

        return response.json()
