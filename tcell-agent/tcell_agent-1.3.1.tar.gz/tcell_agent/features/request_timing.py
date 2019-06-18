import datetime

from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.tcell_logger import get_module_logger


# Note: easy to mock in tests
def get_current_time():
    return datetime.datetime.now()


@catches_generic_exception(__name__, "Error in end_timer")
def end_timer(request):
    if request._tcell_context.start_time != 0:
        endtime = get_current_time()
        request_time = int((endtime - request._tcell_context.start_time).total_seconds() * 1000)
        TCellAgent.request_metric(
            request._tcell_context.route_id,
            request_time,
            request._tcell_context.remote_address,
            request._tcell_context.user_agent,
            request._tcell_context.session_id,
            request._tcell_context.user_id
        )
        get_module_logger(__name__).debug(
            "{} request took {}".format(request._tcell_context.path, request_time)
        )


@catches_generic_exception(__name__, "Error in start_timer")
def start_timer(request):
    request._tcell_context.start_time = get_current_time()
