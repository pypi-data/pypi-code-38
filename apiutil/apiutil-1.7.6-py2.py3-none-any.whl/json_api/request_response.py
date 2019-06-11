# -*- coding: utf-8 -*-

import json
from abc import ABCMeta
from collections import Mapping
from cachingutil import JsonFileCache
from tableutil import Table
from requests.models import CaseInsensitiveDict
from classutils.decorators import class_cache_result


# TODO: This does not handle bad responses!
class JsonApiRequestResponse(Mapping):

    REQUEST = u'request'
    REQUEST_HEADERS = u'request_headers'
    REQUEST_METHOD = u'request_method'
    REQUEST_DATA = u'request_data'
    RESPONSE = u'response'
    RESPONSE_HEADERS = u'response_headers'
    STATUS_CODE = u'status_code'

    CASE_INSENSITIVE_DICTS = (REQUEST_HEADERS,
                              RESPONSE_HEADERS)

    def __init__(self,
                 request,
                 response,
                 request_headers=None,
                 request_method=None,
                 request_data=None,
                 response_headers=None,
                 status_code=None):

        self._request = request
        self._response = response

        try:
            self._request_method = response.request.method
        except AttributeError:
            self._request_method = request_method

        try:
            self._request_headers = response.request.headers
        except AttributeError:
            self._request_headers = CaseInsensitiveDict(request_headers)

        try:
            self._request_data = response.request.data
        except AttributeError:
            self._request_data = request_data

        try:
            self._response_headers = response.headers
        except AttributeError:
            self._response_headers = CaseInsensitiveDict(response_headers)

        try:
            self._response_json = response.json()
        except (AttributeError, ValueError):
            if isinstance(response, dict):
                # If we have a dict object set it as the json response
                self._response_json = response

            else:
                # If we have anything else setup an empty dict as this is supposed to be json
                self._response_json = {}

        try:
            self._status_code = response.status_code
        except AttributeError:
            self._status_code = status_code

    @property
    def request(self):
        return self.json()[self.REQUEST]

    @property
    def response(self):
        return self.json()[self.RESPONSE]

    @property
    # @class_cache_result  # TODO: Figure out why I can't cache this. Get infinite recursion
    def request_response_dictionary(self):

        result = {self.REQUEST:  self._request,
                  self.RESPONSE: self._response_json}

        if self._request_method:
            result[self.REQUEST_METHOD] = self._request_method

        if self._request_headers:
            result[self.REQUEST_HEADERS] = self._request_headers

        if self._request_data:
            result[self.REQUEST_HEADERS] = self._request_data

        if self._response_headers:
            result[self.RESPONSE_HEADERS] = self._request_headers

        if self._status_code:
            result[self.STATUS_CODE] = self._status_code

        return result

    def json(self):
        return self.request_response_dictionary

    @staticmethod
    def serialise(data):
        """
        Can't serialise requests.models.CaseInsensitiveDict
        Return request_response_dictionary, but with CaseInsensitiveDicts
        converted to regular dicts.

        :param data: JsonApiRequestResponse
        :return: dict
        """
        request_response_dictionary = data.request_response_dictionary
        for cid in JsonApiRequestResponse.CASE_INSENSITIVE_DICTS:
            if cid in request_response_dictionary:
                request_response_dictionary[cid] = dict(request_response_dictionary[cid])
        return request_response_dictionary

    @property
    @class_cache_result
    def table(self):
        """
        :return: Table representing the object
        """
        return Table.init_from_tree(tree=self.json(),
                                    title=self.request)

    def __getitem__(self, item):
        return self.response[item]

    def __getattr__(self, item):
        try:
            return self.response[item]

        except KeyError:
            raise AttributeError(u'Response does not have attribute {i}'.format(i=item))

    def __iter__(self):
        return iter(self.response)

    def __len__(self):
        return len(self.response)


class JsonApiRequestResponseFileCache(JsonFileCache):

    __metaclass__ = ABCMeta  # Marks this as an abstract class

    # Also re-implement key and fetch_from_source
    # Optionally modify OBJECT_PAIRS_HOOK

    OBJECT_PAIRS_HOOK = None

    def encode(self,
               data):
        """
        :param data: JsonApiRequestResponse
        :return: JSON string
        """
        serialised = JsonApiRequestResponse.serialise(data)
        return json.dumps(serialised)

    def decode(self,
               encoded):
        return JsonApiRequestResponse(**json.loads(encoded))

