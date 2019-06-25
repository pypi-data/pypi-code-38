# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Flask hook strategy
"""

from logging import getLogger

from ..middlewares import FlaskMiddleware
from .framework import FrameworkStrategy

LOGGER = getLogger(__name__)


def replace_wsgi_app(original, middleware):
    return middleware(original)


class FlaskStrategy(FrameworkStrategy):
    """ Strategy for Flask peripheric callbacks.

    It injects functions that calls pre and post callbacks in the Flask
    request workflow
    """

    MODULE_NAME = "flask.app"
    HOOK_CLASS = "Flask"
    HOOK_METHOD = "full_dispatch_request"

    def __init__(
        self,
        strategy_key,
        observation_queue,
        queue,
        import_hook,
        before_hook_point=None,
    ):
        super(FlaskStrategy, self).__init__(
            strategy_key,
            observation_queue,
            queue,
            import_hook,
            before_hook_point,
        )

        self.middleware = FlaskMiddleware(self, observation_queue, queue)
        self.wrapper = replace_wsgi_app
