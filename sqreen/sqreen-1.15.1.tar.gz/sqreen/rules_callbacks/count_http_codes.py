# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Count http codes
"""
import logging

from ..rules import RuleCallback

LOGGER = logging.getLogger(__name__)


def wraps_start_response(original_start_response, callback):
    """ Decorator for start_response
    """

    def custom_start_response(status, response_headers, exc_info=None):
        """ Actually call to start_response, if status is 404 record an attack
        """

        try:
            if status:
                status_code = None
                if isinstance(status, str):
                    status_code = status.split(" ", 1)[0]
                elif isinstance(status, bytes):
                    status_code = status.split(b" ", 1)[0].decode("latin_1")

                if status_code:
                    callback.record_observation("http_code", status_code, 1)
        except Exception:
            LOGGER.exception("Exception in %s", callable.__class__.__name__)

        return original_start_response(status, response_headers, exc_info)

    return custom_start_response


class CountHTTPCodesCB(RuleCallback):
    def pre(self, original, *args):
        """ Decorate the start_response parameter to capture http status code
        """
        new_args = list(args)
        new_args[-1] = wraps_start_response(args[-1], self)
        return {"status": "modify_args", "args": [new_args, {}]}
