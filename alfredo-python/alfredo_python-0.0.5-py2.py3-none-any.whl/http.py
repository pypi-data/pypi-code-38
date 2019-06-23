"""
  Copyright (c) 2017-2018 Atrio, Inc.

  All rights reserved.
"""

import requests
import io


class HttpService(object):
    def __init__(self):
        self._session = requests.session()

    @staticmethod
    def prepare_field(resource):
        try:
            return resource.id
        except AttributeError:
            try:
                return resource['id']
            except TypeError:
                return resource

    @staticmethod
    def is_file(file_like):
        try:
            return isinstance(file_like, io.IOBase) or isinstance(file_like, file)
        except NameError:
            return False

    def prepare_data_and_files(self, **kwargs):
        files = dict((k, kwargs[k]) for k in kwargs if self.is_file(kwargs[k]))
        data = dict((k, self.prepare_field(kwargs[k])) for k in kwargs if not self.is_file(kwargs[k]))
        return data, files

    def get(self, url, headers):
        return self._session.get(url, headers=headers, stream=True)

    def post(self, url, headers, **kwargs):
        data, files = self.prepare_data_and_files(**kwargs)
        return self._session.post(url, headers=headers, data=data, files=files)

    def put(self, url, headers, **kwargs):
        data, files = self.prepare_data_and_files(**kwargs)
        return self._session.put(url, headers=headers, data=data, files=files)

    def patch(self, url, headers, **kwargs):
        data, files = self.prepare_data_and_files(**kwargs)
        return self._session.patch(url, headers=headers, data=data, files=files)

    def delete(self, url, headers):
        return self._session.delete(url, headers=headers)
