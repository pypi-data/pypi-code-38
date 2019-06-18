# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.tcell_logger import get_module_logger


def is_database_instrumentable():
    instrumentable = False
    try:
        from tcell_agent.instrumentation.djangoinst.compatability import django15or16
        if not django15or16:
            from tcell_agent.instrumentation.djangoinst.dlp import dlp_instrumentation  # noqa pylint: disable=unused-variable
            instrumentable = True
    except ImportError:
        pass
    except Exception as e:
        get_module_logger(__name__).error("Problem importing DLP: {e}".format(e=e))
        get_module_logger(__name__).exception(e)

    return instrumentable


def _instrument(run_dlp_instrumentation):
    from tcell_agent.instrumentation.djangoinst.middleware_access import \
        insert_middleware, is_csrf_middleware_enabled
    from tcell_agent.instrumentation.djangoinst.middleware.csrf_exception_middleware import \
        instrument_csrf_view_middleware
    from tcell_agent.instrumentation.djangoinst.database_error_wrapper import \
        instrument_database_error_wrapper, handle_django15_exception
    from django.core.handlers.base import BaseHandler

    old_load_middleware = BaseHandler.load_middleware

    def load_middleware(*args, **kwargs):
        get_module_logger(__name__).info("Adding middleware")
        insert_middleware(
            "tcell_agent.instrumentation.djangoinst.middleware.body_filter_middleware.BodyFilterMiddleware")
        insert_middleware(
            "tcell_agent.instrumentation.djangoinst.middleware.afterauthmiddleware.AfterAuthMiddleware")
        insert_middleware(
            "tcell_agent.instrumentation.djangoinst.middleware.tcelllastmiddleware.TCellLastMiddleware")
        # insert_middleware(
        #     "tcell_agent.instrumentation.djangoinst.middleware.tcell_data_exposure_middleware.TCellDataExposureMiddleware",
        #     atIdx=0)
        insert_middleware(
            "tcell_agent.instrumentation.djangoinst.middleware.globalrequestmiddleware.GlobalRequestMiddleware",
            atIdx=0)
        insert_middleware(
            "tcell_agent.instrumentation.djangoinst.middleware.timermiddleware.TimerMiddleware")

        if run_dlp_instrumentation:
            pass
            # from tcell_agent.instrumentation.djangoinst.dlp import dlp_instrumentation
            # dlp_instrumentation()

        if is_csrf_middleware_enabled():
            instrument_csrf_view_middleware()

        instrument_database_error_wrapper()

        import tcell_agent.instrumentation.djangoinst.contrib_auth  #  noqa pylint: disable=unused-variable
        return old_load_middleware(*args, **kwargs)

    BaseHandler.load_middleware = load_middleware

    if hasattr(BaseHandler, "handle_uncaught_exception"):
        tcell_handle_uncaught_exception = BaseHandler.handle_uncaught_exception

        def handle_uncaught_exception(self, request, resolver, exc_info):
            handle_django15_exception(request, *exc_info)
            return tcell_handle_uncaught_exception(self, request, resolver, exc_info)

        BaseHandler.handle_uncaught_exception = handle_uncaught_exception


def instrument_django():
    try:
        import django  # pylint: disable=unused-variable

        _instrument(is_database_instrumentable())
    except ImportError:
        pass
    except Exception as e:
        get_module_logger(__name__).debug("Could not instrument django: {e}".format(e=e))
        get_module_logger(__name__).exception(e)
