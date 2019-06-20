from typing import Any, Callable

from microcosm.object_graph import ObjectGraph


def training_initializer():
    """
    Register a microcosm component as a training initializer, so that its init
    method will automatically be called.  This function is designed to be used
    as a decorator on a factory.

    """
    def decorator(func: Callable[[ObjectGraph], Any]):
        def factory(graph):
            component = func(graph)
            graph.training_initializers.register(component)
            return component
        return factory
    return decorator
