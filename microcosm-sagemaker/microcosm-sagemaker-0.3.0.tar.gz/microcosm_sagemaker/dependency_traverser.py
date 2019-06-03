from contextlib import contextmanager
from typing import Any

from microcosm_sagemaker.exceptions import DependencyCycleError


def traverse_component_and_dependencies(component):
    """
    Given a component in a dependency graph, traverses the graph in topological
    order, ie such that all dependencies of a component will be yielded before
    the component itself.

    Each component is expected to have a `dependencies` property that returns
    an iterable of dependency components.  Each component is also expected to
    be hashable.

    """
    yield from _traverse_helper(
        seen=set(),
        reserved=set(),
        component=component,
    )


def _traverse_helper(
    seen: set,
    reserved: set,
    component: Any,
):
    """
    Helper to recursively yield a component and its dependencies.

    `seen` contains a list of all components that have already been visited.
    Its purpose is to prevent us from yielding the same component twice.

    `reserved` is designed to help detect cycles.  We add a component to
    `reserved` just before we visit its dependencies, in order to check that we
    don't see it as one of its transitive dependencies.  We remove it after we
    are done visiting its dependencies, because it is ok if we see the
    component again.  In that case, it will still be in `seen`, so we won't
    visit it again, but it won't be an error, as it would be if the component
    were in `reserved`.

    """
    if component in seen:
        return

    with _reserve(reserved, component):
        for dependency in component.dependencies:
            yield from _traverse_helper(
                seen=seen,
                reserved=reserved,
                component=dependency,
            )

    yield component
    seen.add(component)


@contextmanager
def _reserve(reserved: set, component: Any):
    """
    Adds component to a list of reserved components, erroring if the component
    has already been reserved, then remove component from list of reserved
    components.

    """
    if component in reserved:
        raise DependencyCycleError(component)

    reserved.add(component)
    try:
        yield
    finally:
        reserved.remove(component)
