# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import sys

from tcell_agent.instrumentation.flaskinst.appfirewall import run_appfirewall_check
from tcell_agent.instrumentation.flaskinst.blocking import check_patches_blocking
from tcell_agent.instrumentation.flaskinst.check_agent_startup import start_agent
from tcell_agent.instrumentation.flaskinst.database import check_database_errors
from tcell_agent.instrumentation.flaskinst.headers import flask_add_headers
from tcell_agent.instrumentation.flaskinst.redirects import check_location_redirect
from tcell_agent.instrumentation.flaskinst.js_agent import insert_js_agent
from tcell_agent.instrumentation.flaskinst.meta import create_meta, \
    initialize_tcell_context
from tcell_agent.features.request_timing import end_timer
from tcell_agent.tcell_logger import get_module_logger


def _instrument(Flask):
    from tcell_agent.instrumentation.flaskinst.routes import instrument_routes
    instrument_routes()

    from flask.globals import _request_ctx_stack

    tcell_func = Flask.__init__

    def init(self, *args, **kwargs):
        result = tcell_func(self, *args, **kwargs)

        self.before_first_request_funcs.append(start_agent)

        return result

    Flask.__init__ = init

    tcell_preprocess_request = Flask.preprocess_request

    def preprocess_request(self):
        initialize_tcell_context(_request_ctx_stack.top.request)

        result = tcell_preprocess_request(self)

        create_meta(_request_ctx_stack.top.request)
        block_ip_response = check_patches_blocking(_request_ctx_stack.top.request)
        if block_ip_response:
            return block_ip_response

        return result

    Flask.preprocess_request = preprocess_request

    tcell_process_response = Flask.process_response

    def process_response(self, response):
        result = tcell_process_response(self, response)

        from flask.wrappers import Response
        if isinstance(response, Response):
            run_appfirewall_check(_request_ctx_stack.top.request,
                                  result,
                                  result.status_code)
            result = insert_js_agent(_request_ctx_stack.top.request,
                                     result)
            flask_add_headers(_request_ctx_stack.top.request, result)
            check_location_redirect(_request_ctx_stack.top.request, result)

        end_timer(_request_ctx_stack.top.request)

        return result

    Flask.process_response = process_response

    tcell_handle_user_exception = Flask.handle_user_exception

    def handle_user_exception(self, user_exception):
        try:
            create_meta(_request_ctx_stack.top.request)
            exc_type, exc_value, stack_trace = sys.exc_info()
            check_database_errors(_request_ctx_stack.top.request,
                                  exc_type,
                                  stack_trace)
            return tcell_handle_user_exception(self, user_exception)
        except Exception:
            end_timer(_request_ctx_stack.top.request)
            run_appfirewall_check(_request_ctx_stack.top.request,
                                  None,
                                  500)

            from flask._compat import reraise
            exc_type, exc_value, stack_trace = sys.exc_info()
            reraise(exc_type, exc_value, stack_trace)

    Flask.handle_user_exception = handle_user_exception


def instrument_flask():
    try:
        from flask import Flask

        _instrument(Flask)
    except ImportError:
        pass
    except Exception as exception:
        get_module_logger(__name__).debug("Could not instrument flask: {e}".format(e=exception))
        get_module_logger(__name__).exception(exception)
