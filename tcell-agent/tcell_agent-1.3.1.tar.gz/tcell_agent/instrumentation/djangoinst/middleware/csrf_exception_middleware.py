from tcell_agent.instrumentation.djangoinst.meta import get_appsensor_meta
from tcell_agent.instrumentation.manager import InstrumentationManager
from tcell_agent.tcell_logger import get_module_logger


def instrument_csrf_view_middleware():
    from django.middleware.csrf import CsrfViewMiddleware

    def _tcell_reject(_tcell_original_reject, self, request, reason):
        try:
            meta = get_appsensor_meta(request)
            meta.csrf_reason = reason
        except Exception as exception:
            LOGGER = get_module_logger(__name__)
            LOGGER.error("{}: {}".format("Error in setting csrf exception in meta", exception))
            LOGGER.exception(exception)

        return _tcell_original_reject(self, request, reason)

    InstrumentationManager.instrument(CsrfViewMiddleware, "_reject", _tcell_reject)
