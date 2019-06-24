""" Resolver """
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import cv2
import requests

from tensorflow.logging import debug, error, fatal, info, warn


def imdecode(b):
    decoded = cv2.imdecode(np.asarray(bytearray(b), dtype=np.uint8), cv2.IMREAD_COLOR)

    return None if decoded is None else decoded[:, :, ::-1]


class BaseResolver:
    def __init__(self, name: str, required=False):
        self._name = name
        self._required = required

    @property
    def name(self):
        return self._name

    @property
    def required(self):
        return self._required

    def __call__(self, *args, **kwargs):
        raise NotImplementedError


class FileResolver(BaseResolver):
    def __init__(self, name: str, required=False, fn=None):
        BaseResolver.__init__(self, name, required=required)

        def identity(b):
            return b

        self._fn = fn or identity

    def __call__(self, files, **kwargs):
        if self.required and self.name not in files:
            raise KeyError('`{}` is required'.format(self.name))
        return files.get(self.name, type=lambda f: self._fn(f.read()))


class ImageFileResolver(FileResolver):
    def __init__(self, name: str, required=False):
        FileResolver.__init__(self, name, required=required)

    def __call__(self, files, **kwargs):
        b = FileResolver.__call__(self, files, **kwargs)

        if b is None:
            return None, None

        decoded = imdecode(b)

        if decoded is None:
            raise ValueError('Invalid data on `{}`'.format(self.name))

        return decoded, b


class FormResolver(BaseResolver):
    def __init__(self, name: str, type=None, default=None, required=False):
        BaseResolver.__init__(self, name, required=required)
        self._default = default
        self._type = type

    def __call__(self, form, **kwargs):
        if self.required and self.name not in form:
            raise KeyError('`{}` is required'.format(self.name))
        return form.get(self.name, default=self._default, type=self._type)


class URLResolver(FormResolver):
    def __init__(self, name: str, required=False):
        FormResolver.__init__(self, name, type=str, required=required)

    def __call__(self, form, **kwargs):
        url = FormResolver.__call__(self, form, **kwargs)

        if url is None:
            return None

        try:
            res = requests.get(url)
        except Exception as e:
            info(e)
            raise ValueError('Invalid data on `{}`'.format(self.name))

        return res.content


class ImageURLResolver(URLResolver):
    def __init__(self, name: str, required=False):
        URLResolver.__init__(self, name, required=required)

    def __call__(self, form, **kwargs):
        b = URLResolver.__call__(self, form, **kwargs)

        if b is None:
            return None, None

        decoded = imdecode(b)

        if decoded is None:
            raise ValueError('Invalid data on `{}`'.format(self.name))

        return decoded, b
