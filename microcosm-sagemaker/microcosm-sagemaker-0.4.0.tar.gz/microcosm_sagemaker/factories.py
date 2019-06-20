"""
Consumer factories.

"""
from microcosm.api import defaults
from microcosm.object_graph import ObjectGraph

from microcosm_sagemaker.artifact import RootInputArtifact


def configure_active_bundle(graph):
    if not getattr(graph.config, "active_bundle", ""):
        return None
    return getattr(graph, graph.config.active_bundle)


def configure_active_evaluation(graph):
    if not getattr(graph.config, "active_evaluation", ""):
        return None
    return getattr(graph, graph.config.active_evaluation)


@defaults(
    perform_load=True,
)
def load_active_bundle_and_dependencies(graph: ObjectGraph):
    """
    Loads the active bundle and its dependencies immediately upon instantation.

    """
    if not graph.config.load_active_bundle_and_dependencies.perform_load:
        return

    root_input_artifact = RootInputArtifact(graph.config.root_input_artifact_path)

    graph.bundle_and_dependencies_loader(
        bundle=graph.active_bundle,
        root_input_artifact=root_input_artifact,
    )


def configure_sagemaker(graph):
    """
    Instantiates all the necessary sagemaker factories.

    """
    graph.use(
        "active_bundle",
        "active_evaluation",
        "bundle_and_dependencies_loader",
        "bundle_and_dependencies_trainer",
        "random",
        "training_initializers",
    )
