"""
Main evaluation CLI

"""
from click import command
from microcosm.object_graph import ObjectGraph

from microcosm_sagemaker.app_hooks import create_evaluate_app
from microcosm_sagemaker.artifact import RootInputArtifact
from microcosm_sagemaker.commands.options import input_artifact_option, input_data_option
from microcosm_sagemaker.input_data import InputData


@command()
@input_data_option()
@input_artifact_option()
def main(input_data, input_artifact):
    graph = create_evaluate_app(
        extra_loader=input_artifact.load_config,
    )

    run_evaluate(
        graph=graph,
        input_data=input_data,
        root_input_artifact=input_artifact,
    )


def run_evaluate(
    graph: ObjectGraph,
    input_data: InputData,
    root_input_artifact: RootInputArtifact,
) -> None:
    # Load the saved artifact
    graph.load_bundle_and_dependencies(
        bundle=graph.active_bundle,
        root_input_artifact=root_input_artifact,
    )

    # Evaluate
    graph.active_evaluation(graph.active_bundle, input_data)
