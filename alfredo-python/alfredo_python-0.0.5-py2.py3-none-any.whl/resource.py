"""
  Copyright (c) 2017-2019 Atrio, Inc.

  All rights reserved.
"""
import json
import mimetypes
import sys

import ruamel.yaml as yaml
from requests.exceptions import ChunkedEncodingError
from urllib3.exceptions import IncompleteRead

from alfredo.http_service import HttpService
from alfredo.mixins.lazy import LazyMixin
from alfredo.mixins.nested import NestedMixin


class HttpResource(NestedMixin, LazyMixin):
    class Exception(Exception):
        pass

    def __init__(self, parent, path, children):
        LazyMixin.__init__(self)
        NestedMixin.__init__(self, parent, path, children)

        self.headers = {}
        self.http_service = None

    @property
    def http(self):
        if not self.root.http_service:
            self.root.http_service = HttpService()
        return self.root.http_service

    def prepare_field(self, key, value):
        if "__attrs_files" in self._children and key in self.attrs_files and isinstance(value, str):
            content_type, encoding = mimetypes.guess_type(value)
            return value, open(value, 'rb'), content_type
        return value

    def prepare_input(self, **kwargs):
        return {key: self.prepare_field(key, value) for (key, value) in kwargs.items()}

    def retrieve(self):
        return self.parse_response(self.http.get(self.full_path, self.root.headers))

    def create(self, **kwargs):
        input_data = self.prepare_input(**kwargs)
        return self.parse_response(self.http.post(self.full_path, self.root.headers, **input_data))

    def replace(self, **kwargs):
        input_data = self.prepare_input(**kwargs)
        return self.parse_response(self.http.put(self.full_path, self.root.headers, **input_data))

    def update(self, **kwargs):
        input_data = self.prepare_input(**kwargs)
        return self.parse_response(self.http.patch(self.full_path, self.root.headers, **input_data))

    def delete(self):
        return self.parse_response(self.http.delete(self.full_path, self.root.headers))

    def parse_response(self, http_response):
        if http_response.ok and http_response.status_code != 204:
            content_type = http_response.headers['content-type']

            if content_type == 'application/json':
                response_body = http_response.json()
                if 'results' in response_body and 'count' in response_body:
                    return HttpIterableResponse(self, http_response)

            elif content_type == 'text/plain':
                return HttpTextPlainResponse(self, http_response)

            else:
                raise HttpResource.Exception("Unknown content-type {}".format(content_type))

        return HttpSingleResponse(self, http_response)


class HttpPropertyResource(HttpResource):
    def __init__(self, parent, path, children):
        super(HttpPropertyResource, self).__init__(parent, path, children)

    def __getattr__(self, child_path):
        if ("__%s" % child_path) in self._children:
            return self._children[("__%s" % child_path)]
        if (":%s" % child_path) in self._children:
            return HttpMethodResource(self, child_path, self._children[(":%s" % child_path)])
        elif child_path in self._children:
            return HttpPropertyResource(self, child_path, self._children[child_path])
        else:
            return super(HttpPropertyResource, self).__getattr__(child_path)


class HttpMethodResource(HttpPropertyResource):
    def __init__(self, parent, path, children):
        super(HttpMethodResource, self).__init__(parent, path, children)

    def __call__(self, path):
        self._path = str(path)
        return self


class HttpResponse(HttpPropertyResource):
    def __init__(self, resource, status, reason, result):
        super(HttpResponse, self).__init__(resource._parent, resource._path, resource._children)
        self._status = status
        self._reason = reason
        self._result = result
        self._ok = True

    @property
    def reason(self):
        return self._reason

    @property
    def status(self):
        return self._status

    @property
    def ok(self):
        return self._ok and self._status < 400

    @property
    def exit_code(self):
        return 0 if self.ok else self.status / 100

    def __str__(self):
        return yaml.dump(self._result, default_flow_style=False)

    def __repr__(self):
        return "\n%d - %s\n\n%s" % (self._status, self._reason, self)

    def __getitem__(self, item):
        key = list(self._result.keys())[item]
        return key, self._result.__getitem__(key)

    def __getattr__(self, item):
        if item not in self._result:
            raise AttributeError('%r object has no attribute %r' % (self.__class__.__name__, item))
        return self._result[item]

    def native(self):
        return self._result

    def __bool__(self):
        return True

    __nonzero__ = __bool__


class HttpSingleResponse(HttpResponse):
    def __init__(self, resource, http_response):
        super(HttpSingleResponse, self).__init__(resource, http_response.status_code, http_response.reason, {})

        if self.status != 204:
            try:
                self._result = http_response.json()
            except ValueError:
                self._result = {self.status: self.reason}
                self._ok = False


class HttpTextPlainResponse(HttpResponse):
    def __init__(self, resource, http_response):
        super(HttpTextPlainResponse, self).__init__(resource, http_response.status_code, http_response.reason, '')
        self._http_response = http_response
        self.truncated_warning = '\r[truncated content...]\n'

    def stream(self, target=sys.stdout):
        try:
            for line in self._http_response.iter_lines(chunk_size=1):
                target.write(line.decode("utf-8"))
                target.write('\n')
        except KeyboardInterrupt:
            target.write(self.truncated_warning)

    def __str__(self):
        self._result = ''
        number_of_lines = 0
        old_line = None

        for line in self._http_response.iter_lines(chunk_size=1):
            number_of_lines += 1
            if old_line:
                self._result += old_line + '\n'
                if number_of_lines == 5:
                    return self._result + self.truncated_warning
            old_line = line
        self._result += old_line
        return self._result


class HttpIterableResponse(HttpResponse):
    def __init__(self, resource, http_response):
        super(HttpIterableResponse, self).__init__(resource, http_response.status_code, http_response.reason,
                                                   http_response.json())

    def native(self):
        return [item.native() for item in self]

    def __bool__(self):
        return len(self) > 0

    __nonzero__ = __bool__

    def __len__(self):
        return self._result['count']

    def __repr__(self):
        return "\n%d - %s\n\n%d items\n" % (self._status, self._reason, len(self))

    def __str__(self):
        if len(self) == 0:
            return yaml.dump([], default_flow_style=False)
        return "".join(yaml.dump([item._result], default_flow_style=False) for item in self)

    @property
    def items(self):
        return self._result['results']

    def __getitem__(self, key):
        if isinstance(key, slice):
            return iter(self[i] for i in range(*key.indices(len(self))))
        elif isinstance(key, int):
            if key < 0:
                key += len(self)
            if key < 0 or key >= len(self):
                raise IndexError("The index (%d) is out of range." % key)
            while key >= len(self.items):
                current_next = self._result['next']
                self.get_next_page()
                if current_next == self._result['next']:
                    raise IndexError("The index (%d) is out of range." % key)

            if ':id' in self._children and 'id' in self.items[key]:
                return HttpResponse(HttpPropertyResource(self, self.items[key]['id'], self._children[':id']),
                                    200, 'Partial content', self.items[key])
            else:
                return HttpResponse(self, 206, 'Partial content', self.items[key])
        else:
            raise TypeError('invalid argument')

    def get_next_page(self):
        if self._result['next']:
            next_page_value = self.http.get(self._result['next'], self.root.headers).json()
            self._result['results'].extend(next_page_value['results'])
            self._result['next'] = next_page_value['next']
