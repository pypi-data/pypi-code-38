from microcosm.api import defaults
from microcosm.object_graph import ObjectGraph

from microcosm_sagemaker.artifact import RootInputArtifact, RootOutputArtifact
from microcosm_sagemaker.bundle import Bundle
from microcosm_sagemaker.input_data import InputData


@defaults(
    bundle_orchestrator="single_threaded_bundle_orchestrator",
)
class BundleAndDependenciesLoader:
    def __init__(self, graph: ObjectGraph):
        self.bundle_orchestrator = getattr(
            graph,
            graph.config.load_bundle_and_dependencies.bundle_orchestrator,
        )
        self.graph = graph

    def __call__(
        self,
        bundle: Bundle,
        root_input_artifact: RootInputArtifact,
        dependencies_only: bool = False,
    ):
        def load(bundle):
            name = _get_component_name(self.graph, bundle)
            bundle.load(root_input_artifact / name)

        self.bundle_orchestrator(
            bundle=bundle,
            bundle_handler=load,
            dependencies_only=dependencies_only,
        )


def save_bundle(
    graph: ObjectGraph,
    bundle: Bundle,
    root_output_artifact: RootOutputArtifact,
) -> None:
    bundle_name = _get_component_name(graph, bundle)

    nested_output_artifact = root_output_artifact / bundle_name
    nested_output_artifact.init()

    bundle.save(nested_output_artifact)


@defaults(
    bundle_orchestrator="single_threaded_bundle_orchestrator",
)
class BundleAndDependenciesTrainer:
    def __init__(self, graph: ObjectGraph):
        self.bundle_orchestrator = getattr(
            graph,
            graph.config.train_bundle_and_dependencies.bundle_orchestrator,
        )
        self.graph = graph

    def __call__(
        self,
        bundle: Bundle,
        input_data: InputData,
        root_output_artifact: RootOutputArtifact,
        dependencies_only: bool = False,
    ):
        def train(bundle):
            bundle.fit(input_data)
            save_bundle(self.graph, bundle, root_output_artifact)

        self.bundle_orchestrator(
            bundle=bundle,
            bundle_handler=train,
            dependencies_only=dependencies_only,
        )


def _get_component_name(graph, component):
    return next(
        key
        for key, possible_component in graph.items()
        if possible_component == component
    )
