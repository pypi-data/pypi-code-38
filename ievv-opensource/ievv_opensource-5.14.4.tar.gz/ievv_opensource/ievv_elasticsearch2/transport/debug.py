import json
from pprint import pformat

import elasticsearch
import elasticsearch.exceptions
import sys

from django.conf import settings
from django.http import QueryDict

from ievv_opensource.utils import ievv_colorize


def _instant_print(text='', color=None, bold=False):
    print(ievv_colorize.colorize(text, color=color, bold=bold))
    sys.stdout.flush()


def _force_json_encodable(data):
    if isinstance(data, str):
        try:
            return json.loads(data)
        except TypeError:
            return data
        except ValueError:
            return data
    else:
        return data


def _instant_prettyjson(data, is_newline_list=False, color=None, bold=False):
    if is_newline_list:
        for line in data.split('\n'):
            _instant_print(line)
    else:
        try:
            pretty = json.dumps(_force_json_encodable(data), indent=4)
        except TypeError:
            pretty = pformat(data)
        print(ievv_colorize.colorize(pretty, color=color, bold=bold))
        sys.stdout.flush()


class DebugTransport(elasticsearch.Transport):
    """
    An ElasticSearch transport class for debugging.

    If this is defined as the transport_class for
    :class:`elasticsearch.client.Elasticsearch`, and the
    :setting:`IEVV_ELASTICSEARCH2_DEBUGTRANSPORT_PRETTYPRINT_ALL_REQUESTS` setting
    is set to ``True``, we prettyprint all requests and responses from
    ElasticSearch.
    """
    def __prettyprint_request(self, method, url, params, body):
        _instant_print()
        _instant_print('>>>>>> prettyprint ElasticSearch request input >>>>>>',
                       color=ievv_colorize.COLOR_BLUE)
        querystring = ''
        if params:
            querydict = QueryDict(mutable=True)
            querydict.update(params)
            querystring = '?' + querydict.urlencode()
        prettyformatted_requestheader = '{method} {url}{querystring}'.format(
            method=method,
            url=url,
            querystring=querystring)
        _instant_print(prettyformatted_requestheader)
        if body:
            _instant_prettyjson(body,
                                is_newline_list=url.endswith('_bulk'))
        _instant_print('<<<<<< prettyprint ElasticSearch request input <<<<<<',
                       color=ievv_colorize.COLOR_BLUE)
        return prettyformatted_requestheader

    def __prettyprint_successful_response(self, response, prettyformatted_requestheader):
        status_code, data = response
        _instant_print()
        _instant_print('>>>>>> {} response >>>>>>'.format(prettyformatted_requestheader),
                       color=ievv_colorize.COLOR_GREEN)
        _instant_print('HTTP status code: {}'.format(status_code))
        _instant_prettyjson(data)
        _instant_print('<<<<<< {} response <<<<<<'.format(prettyformatted_requestheader),
                       color=ievv_colorize.COLOR_GREEN)
        _instant_print()

    def __prettyprint_error_response(self, error, prettyformatted_requestheader):
        _instant_print()
        _instant_print('>>>>>> {} response >>>>>>'.format(prettyformatted_requestheader),
                       color=ievv_colorize.COLOR_RED, bold=True)
        _instant_print('HTTP error code: {}'.format(error.status_code))
        _instant_print('ERROR data:')
        _instant_prettyjson(error.error)
        _instant_print('ERROR info:')
        _instant_prettyjson(error.info)
        _instant_print('<<<<<< {} response <<<<<<'.format(prettyformatted_requestheader),
                       ievv_colorize.COLOR_RED, bold=True)
        _instant_print()

    def perform_request(self, method, url, params=None, body=None):
        print_all_requests = getattr(settings, 'IEVV_ELASTICSEARCH2_DEBUGTRANSPORT_PRETTYPRINT_ALL_REQUESTS', False)
        prettyformatted_requestheader = None
        if print_all_requests:
            prettyformatted_requestheader = self.__prettyprint_request(
                method=method, url=url, params=params, body=body)
        try:
            response = super(DebugTransport, self).perform_request(
                method=method, url=url, params=params, body=body)
        except elasticsearch.exceptions.TransportError as error:
            if print_all_requests:
                self.__prettyprint_error_response(
                    error=error,
                    prettyformatted_requestheader=prettyformatted_requestheader)
            raise

        if print_all_requests:
            self.__prettyprint_successful_response(
                response=response,
                prettyformatted_requestheader=prettyformatted_requestheader)
        return response
