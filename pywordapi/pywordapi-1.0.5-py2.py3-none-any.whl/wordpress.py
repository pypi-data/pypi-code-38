"""
File: wordpress.py
Author: Allan Chang
Email: allan@clchang.net
Github: https://github.com/clchangnet
Description: Wordpress API
"""

import json
import urllib.parse

import requests

DEFAULT_METHODS = {
    "get_posts": "wp-json/wp/v2/posts?_embed",
    "get_categories": "wp-json/wp/v2/categories",
}


class ApiCall:  # pylint: disable=too-few-public-methods
    """ contruct the request url """

    def __init__(self, api_url, proxy=None):
        self.api_url = api_url
        self.proxy = proxy
        self.query = ""

    def request(self, method_name):
        """ build the api url """
        self._build_post_request(method_name)

    def _build_post_request(self, method_name):
        """docstring for _build_post_request"""
        self.query = urllib.parse.urljoin(
            self.api_url,
            DEFAULT_METHODS[method_name]
            )


class Wordpress(ApiCall):
    """ make api call and retrieve postdata from wordpress sites"""

    def __getattr__(self, method_name):
        """ Return a callable API method if `method` is in DEFAULT_METHODS """
        if method_name in DEFAULT_METHODS:

            def handler_function(*args):
                """docstring for handlerFunction"""
                return self._make_request(method_name, args)

            return handler_function
        raise AttributeError

    @staticmethod
    def is_empty(any_structure):
        """ check is data structure empty"""
        if any_structure:
            return False
        return True

    @staticmethod
    def _http_get(url, proxy):
        proxyDict = None
        if proxy is not None:
            proxyDict = {
                "http": proxy,
                "https": proxy
                }
        try:
            response = requests.get(url, proxies=proxyDict)
            return response.content
        except requests.ConnectionError:
            return json.dumps([{'error': 'ConnectionError'}])

    def _make_request(self, method_name, args):
        """docstring for _make_request"""
        self.request(method_name)
        if self.is_empty(args):
            data = self._http_get(self.query, self.proxy)
            try:
                return json.loads(data)[0]
            except Exception:
                return json.loads('{"error": "JsonDecodeError"}')
        return None
