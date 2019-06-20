from abc import ABC, abstractmethod
from typing import Callable

from microcosm.object_graph import ObjectGraph

from microcosm_sagemaker.bundle import Bundle
from microcosm_sagemaker.dependency_traverser import traverse_component_and_dependencies


class BundleOrchestrator(ABC):
    def __init__(self, graph: ObjectGraph):
        pass

    @abstractmethod
    def __call__(
        self,
        bundle: Bundle,
        bundle_handler: Callable[[Bundle], None],
        dependencies_only: bool = False,
    ):
        """
        Given a `bundle`, call `bundle_handler` on `bundle` and all its
        transitive dependencies, ensuring that `bundle_handler` has been called
        on all dependencies of any bundle before it is called on the bundle
        itself.

        If `dependencies_only` is `True`, do not call `bundle_handler` on the
        given `bundle` itself, but rather only its dependencies.

        """
        ...


class SingleThreadedBundleOrchestrator(BundleOrchestrator):
    """
    Performs topological sort on dependencies of `bundle` and calls
    `bundle_handler` on each bundle one at a time.

    """
    def __call__(
        self,
        bundle: Bundle,
        bundle_handler: Callable[[Bundle], None],
        dependencies_only: bool = False,
    ):
        for bundle_to_handle in traverse_component_and_dependencies(bundle):
            if dependencies_only and bundle_to_handle == bundle:
                continue

            bundle_handler(bundle_to_handle)
