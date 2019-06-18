import threading

from tcell_agent.agent import TCellAgent
from tcell_agent.policies.policy_types import PolicyTypes
from tcell_agent.utils.batches import batches
from tcell_agent.instrumentation.decorators import catches_generic_exception


_ROUTES_SEND_LOCK = threading.Lock()
_ROUTES_SENT = False


def has_route_table_been_sent():
    return _ROUTES_SENT


def set_route_table_has_been_sent():
    global _ROUTES_SENT  # pylint: disable=global-statement
    _ROUTES_SENT = True


@catches_generic_exception(__name__, "Exception reporting routes")
def send_routes(routes):
    for routes_batch in batches(routes, 25):
        TCellAgent.discover_routes(routes_batch)


@catches_generic_exception(__name__, "Error creating routes to report")
def create_and_send_routes(routes_getter_func):
    routes = routes_getter_func()
    send_routes_thread = threading.Thread(target=send_routes,
                                          args=(routes,))
    send_routes_thread.daemon = True
    send_routes_thread.start()


def ensure_routes_sent(routes_getter_func):
    system_enablements = TCellAgent.get_policy(PolicyTypes.SYSTEM_ENABLEMENTS)
    if not system_enablements.send_routes_enabled:
        return
    if has_route_table_been_sent():
        return

    with _ROUTES_SEND_LOCK:
        if has_route_table_been_sent():
            return
        set_route_table_has_been_sent()

    create_and_send_routes(routes_getter_func)
