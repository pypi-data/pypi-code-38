# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
import sys

from ...exceptions import RequestBlocked
from ...runtime_storage import runtime
from ...utils import update_wrapper
from .base import BaseMiddleware


class FlaskMiddleware(BaseMiddleware):
    def __call__(self, original):
        def wrapped(*args, **kwargs):
            """ Call the lifecycles methods with these arguments:
            Flask pre callbacks will receive these arguments:
            (None)
            Flask post callbacks will receive these arguments:
            (None, response)
            Flask failing callbacks will receive these arguments:
            (None, exception)
            """
            try:
                self.strategy.before_hook_point()

                self.execute_pre_callbacks(record_attack=True)

                try:
                    response = original(*args, **kwargs)
                except Exception:
                    self.execute_failing_callbacks(sys.exc_info())
                    raise
                return self.execute_post_callbacks(
                    response, record_attack=True
                )
            except RequestBlocked:
                runtime.clear_request(self.queue, self.observation_queue)
                raise
            finally:
                runtime.clear_request()

        update_wrapper(wrapped, original)

        return wrapped
