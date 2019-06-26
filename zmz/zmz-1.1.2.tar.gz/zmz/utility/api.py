import requests

from zmz.model.resource import Resource
from zmz.model.result import Result
from zmz.utility import base_url


class API(object):

    @staticmethod
    def search(keyword):
        json = requests.get(base_url, params={
            'a': 'search',
            'k': keyword
        }).json()
        return list(map(lambda data: Result(data), json['data']))

    @staticmethod
    def fetch_resource(resource_id):
        json = requests.get(base_url, params={
            'a': 'resource',
            'id': resource_id
        }).json()
        return Resource(json['data'])
