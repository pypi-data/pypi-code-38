#!/usr/local/bin/python3
"""
The spectre module is used to make access to Lumeta's Spectre API
a little easier (Lumeta and Spectre are trademarks of the Lumeta Corporation).
"""
import requests
import urllib3
import spectreapi


class Response:
    """
    This class is used to present the results of a "GET" API call
    It handles iterating through the results and fetching pages as
    needed from the server
    """

    def __init__(self, server, api, params):
        self.server = server
        self.api = api
        self.params = params
        self.page = 0
        self.page_line = 0
        self.results = self.server.getpage(api, params, page=self.page)

        if "total" in self.results.json():
            self.total = self.results.json()['total']
        else:
            self.total = 1

    def rewind(self):
        '''Used to reset state after iterating over results'''
        self.page = 0
        self.page_line = 0
        self.results = self.server.getpage(
            self.api, self.params, page=self.page)

    def __iter__(self):
        return self

    def __next__(self):
        '''This facilitates being able to iterate over the results of a GET'''
        if self.page * self.server.page_size + self.page_line == self.total:
            self.rewind()
            raise StopIteration

        if self.page_line < self.server.page_size:
            self.page_line += 1
            try:
                return self.results.json()['results'][self.page_line - 1]
            except IndexError:
                self.rewind()
                raise StopIteration  # This could happen if the underlying query shrinks under us

        else:
            self.page_line = 1
            self.page += 1
            self.results = self.server.getpage(
                self.api, self.params, page=self.page)
            try:
                return self.results.json()['results'][0]
            except IndexError:
                self.rewind()
                raise StopIteration  # This could happen if the underlying query shrinks under us

    @property
    def result(self):
        """Return result 0 (the only result for singletons"""
        return self.values()[0]

    def values(self):
        """Return the values from the API call"""
        return self.results.json()['results']


