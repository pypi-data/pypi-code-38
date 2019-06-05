#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dns import reversename, resolver
import logging


class DNSBLResults(object):
    def __init__(
            self,
            data,
            auth_tokens=None,
            **kwargs
    ):
        from .provider import supports as provider_support
        from .utils import get_data_type
        self.data_type = get_data_type(data)
        if not auth_tokens:
            auth_tokens = {}
        self.auth_tokens = auth_tokens
        self.data = data
        self.results = []
        self.match_categories = []
        self.detailed_results = []
        for provided in provider_support[self.data_type]:
            try:
                results = provided(self.data, auth_tokens=self.auth_tokens)
            except DNSBLAuthException as e:
                logging.warning(e)
                continue
            self.results.append(results)

            if results.match_categories:
                for match in results.match_categories:
                    self.match_categories.append('{}: {}'.format(results.__class__.__name__, match))

            if results.detailed_results:
                self.detailed_results.append(results.detailed_results)

        if not self.match_categories:
            self.match_categories = ['None']

    def __str__(self):
        result_text = ''
        if len(self.results) == 0 or self.match_categories[0] == 'None':
            return 'No results for {} {}.'.format(self.data_type, self.data)
        for results in self.results:
            if results.match:
                result_text += '{}: {}\n\n'.format(results.__class__.__name__, str(results))
        return result_text.rstrip()


class DNSBLException(Exception):
    pass


class DNSBLAuthException(DNSBLException):
    pass


class DNSBLBase(object):
    def __init__(
            self,
            auth_tokens=None,
            **kwargs
    ):
        if not auth_tokens:
            auth_tokens = {}
        self.auth_tokens = auth_tokens
        self.host = 'example.com'
        self.query_type = 'A'
        self.answer = None
        self.match = None
        self.result = None
        self.match_categories = []
        self.detailed_results = None
        self.category_info = None
        self.resolver = None
        self.supports = ''
        self.data = None

    def __str__(self):
        if self.match:
            match_text = 'Matched {} categorie(s): {}'.format(
                len(self.match_categories),
                '; '.join(self.match_categories)
            )
        else:
            match_text = 'Did not match'
        detailed_results_string = ''
        if self.detailed_results:
            detailed_results_string = '\n        Detailed Results: {}\n        More Info: {}'.format(
                self.detailed_results,
                self.category_info
            )
        return '{} {}\n    {}.{}'.format(self.supports, self.data, match_text, detailed_results_string)

    def do_query(self, query, query_type):
        try:
            answer = self.resolver.query(query, query_type)
        except resolver.NXDOMAIN:
            answer = False
        return answer

    @staticmethod
    def reverse_ip(ip):
        rev = reversename.from_address(ip).to_text()
        if rev.endswith('.ip6.arpa.'):
            return rev[:-10]
        elif rev.endswith('.in-addr.arpa.'):
            return rev[:-14]
