"""
  Copyright (c) 2017-2019 Atrio, Inc.

  All rights reserved.
"""

import sys

import requests
from requests_toolbelt import MultipartEncoderMonitor

from alfredo import format_si
from alfredo.format_si import format_si


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
        return isinstance(file_like, tuple)

    @staticmethod
    def progress(monitor):
        percentage = 100 * monitor.bytes_read / float(monitor.len)
        read = format_si(monitor.bytes_read)
        total = format_si(monitor.len)

        sys.stderr.write("Uploading... {0:>6.2f}% {1:>11} / {2:<11}\r".format(percentage, read, total))

    def prepare_data_and_files(self, **kwargs):
        files = dict((k, kwargs[k]) for k in kwargs if self.is_file(kwargs[k]))
        data = dict((k, self.prepare_field(kwargs[k])) for k in kwargs if not self.is_file(kwargs[k]))

        if files:
            data.update(files)
            uploader = MultipartEncoderMonitor.from_fields(fields=data, callback=self.progress)
            return {'Content-Type': uploader.content_type}, uploader

        return {}, data

    def get(self, url, headers):
        return self._session.get(url, headers=headers, stream=True)

    def post(self, url, headers, **kwargs):
        extra_headers, uploader = self.prepare_data_and_files(**kwargs)
        headers.update(extra_headers)
        return self._session.post(url, headers=headers, data=uploader, stream=False)

    def put(self, url, headers, **kwargs):
        extra_headers, uploader = self.prepare_data_and_files(**kwargs)
        headers.update(extra_headers)
        return self._session.put(url, headers=headers, data=uploader, stream=False)

    def patch(self, url, headers, **kwargs):
        extra_headers, uploader = self.prepare_data_and_files(**kwargs)
        headers.update(extra_headers)
        return self._session.patch(url, headers=headers, data=uploader, stream=False)

    def delete(self, url, headers):
        return self._session.delete(url, headers=headers)
