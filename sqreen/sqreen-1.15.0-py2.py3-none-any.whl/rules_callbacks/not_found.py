# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Look for 404 error
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

        if "404" in status:
            request = callback.storage.get_current_request()
            if request is not None:
                infos = {
                    "path": request.path,
                    "host": request.hostname,
                    "verb": request.method,
                    "ua": request.client_user_agent,
                }
                callback.record_attack(infos)

        return original_start_response(status, response_headers, exc_info)

    return custom_start_response


class NotFoundCB(RuleCallback):
    def pre(self, original, *args):
        """ Decorate the start_response parameter to append our header on call
        """
        new_args = list(args)
        new_args[-1] = wraps_start_response(args[-1], self)
        return {"status": "modify_args", "args": [new_args, {}]}
