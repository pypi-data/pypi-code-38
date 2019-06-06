# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Insert X-Protected-By header
"""
import logging
from collections import Mapping
from copy import copy

from ..exceptions import InvalidArgument
from ..rules import RuleCallback

LOGGER = logging.getLogger(__name__)


def wraps_start_response(original_start_response, callback):
    """ Decorator for start_response
    """

    def custom_start_response(status, response_headers, exc_info=None):
        """ Actually call to start_response, append our header
        """
        callback_headers = copy(callback.headers)

        # Override existing headers
        for i, header in enumerate(response_headers):
            header_name = header[0]
            if header_name in callback_headers.keys():
                response_headers[i] = (
                    header_name,
                    callback_headers.pop(header_name),
                )

        # Add the remaining custom headers
        response_headers += list(callback_headers.items())

        return original_start_response(status, response_headers, exc_info)

    return custom_start_response


def convert_to_str(headers):
    """ Encode a list of headers tuples into latin1
    """
    for header_name, header_value in headers:
        header_name = str(
            header_name.encode("latin-1", errors="replace").decode("latin-1")
        )
        header_value = str(
            header_value.encode("latin-1", errors="replace").decode("latin-1")
        )
        yield (header_name, header_value)


class BaseHeadersInsertCB(RuleCallback):
    """ Base class for header insertion callbacks
    """

    def __init__(self, *args, **kwargs):
        super(BaseHeadersInsertCB, self).__init__(*args, **kwargs)

        if not isinstance(self.data, Mapping):
            msg = "Invalid data type received: {}"
            raise InvalidArgument(msg.format(type(self.data)))

        try:
            self.values = self.data["values"]
        except KeyError:
            msg = "No key 'values' in data (had {})"
            raise InvalidArgument(msg.format(self.data.keys()))

        self._headers = None

    @property
    def headers(self):
        """ Cached property to defer headers data conversio,n
        """
        if self._headers is None:
            self._headers = dict(convert_to_str(self.values))
        return self._headers


class HeadersInsertCB(BaseHeadersInsertCB):
    """ Callback that add the custom sqreen header in WSGI
    """

    def pre(self, original, *args):
        """ Decorate the start_response parameter to append our header on call
        """
        new_args = list(args)
        new_args[-1] = wraps_start_response(args[-1], self)
        return {"status": "modify_args", "args": [new_args, {}]}
