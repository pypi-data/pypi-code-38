import traceback

from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.policies.policy_types import PolicyTypes
from tcell_agent.tcell_logger import get_module_logger


@catches_generic_exception(__name__, "Error checking for database errors")
def check_database_errors(request, exc_type, tb):
    try:
        appfirewall_policy = TCellAgent.get_policy(PolicyTypes.APPSENSOR)
        if appfirewall_policy.appfirewall_enabled:
            from sqlalchemy.exc import DatabaseError

            if issubclass(exc_type, DatabaseError):
                stack_trace = traceback.format_tb(tb)
                stack_trace.reverse()
                request._appsensor_meta.sql_exceptions.append({
                    "exception_name": exc_type.__name__,
                    "exception_payload": "".join(stack_trace)
                })
    except ImportError:
        pass
    except Exception as exception:
        LOGGER = get_module_logger(__name__)
        LOGGER.debug("Exception during database errors check: {e}".format(e=exception))
        LOGGER.exception(exception)
