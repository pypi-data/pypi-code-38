# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
import sys

from ...exceptions import RequestBlocked
from ...frameworks.pyramid_framework import PyramidResponse
from ...runtime_storage import runtime
from ...utils import update_wrapper
from .base import BaseMiddleware


class PyramidMiddleware(BaseMiddleware):
    def __call__(self, handler):
        def wrapped(request, *args, **kwargs):
            """ Call the lifecycles methods with these arguments:
            Pyramid pre callbacks will receive these arguments:
            (None, request)
            Pyramid post callbacks will receive these arguments:
            (None, response)
            Pyramid failing callbacks will receive these arguments:
            (None, exception)
            """
            from pyramid.response import Response

            try:
                self.strategy.before_hook_point()
                pre_args = (request,)
                self.execute_pre_callbacks(pre_args, record_attack=True)

                try:
                    response = handler(request, *args, **kwargs)
                except Exception as e:
                    if isinstance(e, Response):
                        self.execute_post_callbacks(e)
                    else:
                        self.execute_failing_callbacks(sys.exc_info())
                    raise

                return self.execute_post_callbacks(
                    response, record_attack=True
                )
            except RequestBlocked:
                is_uwsgi = "uwsgi.version" in request.environ

                # In uwsgi 2.0.14, raising an AttackBlocked kill the connection
                # Instead return a 500 error
                if is_uwsgi:
                    response = Response("Internal Server Error")
                    response.status_int = 500
                    runtime.store_response(PyramidResponse(response))
                    runtime.clear_request(self.queue, self.observation_queue)
                    return response

                runtime.clear_request(self.queue, self.observation_queue)
                raise
            finally:
                runtime.clear_request()

        update_wrapper(wrapped, handler)

        return wrapped
