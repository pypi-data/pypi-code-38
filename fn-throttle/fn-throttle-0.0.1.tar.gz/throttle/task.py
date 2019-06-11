"""
Interfaces
Decorator act like celery.task
"""

from typing import Any, Callable
from functools import wraps

from .node import ThrottleNode

throttle_node = ThrottleNode()


def task(min_interval: float) -> Callable:

    def deco(fn: Callable) -> Callable:
        throttle_node.registry(fn, min_interval=min_interval)

        @wraps(fn)
        def throttled(*args, **kwargs) -> Any:
            return throttle_node.run(fn, args=args, kwargs=kwargs)

        return throttled

    return deco
