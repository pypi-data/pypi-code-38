import traceback

from tcell_agent.agent import TCellAgent
from tcell_agent.policies.policy_types import PolicyTypes
from tcell_agent.instrumentation.djangoinst.meta import get_appsensor_meta
from tcell_agent.instrumentation.djangoinst.middleware.globalrequestmiddleware import GlobalRequestMiddleware
from tcell_agent.instrumentation.manager import InstrumentationManager
from tcell_agent.instrumentation.djangoinst.compatability import django15or16
from tcell_agent.tcell_logger import get_module_logger


def instrument_database_error_wrapper():
    if not django15or16:
        try:
            from django.db.utils import DatabaseErrorWrapper

            def _tcell_exit(_tcell_original_exit, self, exc_type, exc_value, tb):
                if exc_type is not None:
                    programming_error = getattr(self.wrapper.Database, "ProgrammingError")
                    operational_error = getattr(self.wrapper.Database, "OperationalError")
                    if issubclass(exc_type, programming_error) or issubclass(exc_type, operational_error):
                        appfirewall_policy = TCellAgent.get_policy(PolicyTypes.APPSENSOR)
                        if appfirewall_policy.appfirewall_enabled:
                            request = GlobalRequestMiddleware.get_current_request()
                            if request is not None:
                                meta = get_appsensor_meta(request)

                                stack_trace = traceback.format_tb(tb)
                                stack_trace.reverse()
                                meta.sql_exceptions.append({
                                    "exception_name": exc_type.__name__,
                                    "exception_payload": "".join(stack_trace)
                                })

                return _tcell_original_exit(self, exc_type, exc_value, tb)

            InstrumentationManager.instrument(DatabaseErrorWrapper, "__exit__", _tcell_exit)

        except ImportError:
            pass
        except Exception as e:
            LOGGER = get_module_logger(__name__)
            LOGGER.debug("Could not instrument database error wrapper")
            LOGGER.exception(e)


def handle_django15_exception(request, exc_type, _, tb):
    if django15or16:
        try:
            appfirewall_policy = TCellAgent.get_policy(PolicyTypes.APPSENSOR)
            if appfirewall_policy.appfirewall_enabled:
                from django.db.utils import DatabaseError

                if exc_type is not None and issubclass(exc_type, DatabaseError):
                    meta = get_appsensor_meta(request)
                    stack_trace = traceback.format_tb(tb)
                    stack_trace.reverse()
                    meta.sql_exceptions.append({
                        "exception_name": exc_type.__name__,
                        "exception_payload": "".join(stack_trace)
                    })

        except ImportError:
            pass
        except Exception as exception:
            LOGGER = get_module_logger(__name__)
            LOGGER.debug("Exception in handle_django15_exception: {e}".format(e=exception))
            LOGGER.exception(exception)
