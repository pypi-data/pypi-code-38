from cmndr import Middleware
import jsonpickle

import strongr.core

class CeleryMiddleware(Middleware):
    def __init__(self, wait_for_return):
        self._core = strongr.core.Core
        self._wait_for_return = wait_for_return

    def execute(self, command, next_callable):
        name = command.__module__.split('.')[1] + '.' + command.__class__.__name__.lower()
        command_router = self._core.command_router()
        if not command_router.has_remotable_command_registered(name):
            # if no remotable route is enabled for this command we should
            # proceed as normal
            ret = next_callable(command)
            return ret

        # a remotable route is registered, lets use it!
        result = command_router.get_remotable_command_for(name).delay(jsonpickle.encode(command))
        if self._wait_for_return:
            return result.get(timeout=500)

