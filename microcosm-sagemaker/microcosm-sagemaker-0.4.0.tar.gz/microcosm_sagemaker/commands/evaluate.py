"""
Main evaluation CLI

"""
from click import command
from microcosm.loaders import load_from_dict
from microcosm.object_graph import ObjectGraph

from microcosm_sagemaker.app_hooks import create_evaluate_app
from microcosm_sagemaker.commands.options import input_artifact_option, input_data_option
from microcosm_sagemaker.input_data import InputData


@command()
@input_data_option()
@input_artifact_option()
def main(input_data, input_artifact):
    graph = create_evaluate_app(
        extra_loader=load_from_dict(
            root_input_artifact_path=input_artifact.path,
        ),
    )

    run_evaluate(
        graph=graph,
        input_data=input_data,
    )


def run_evaluate(
    graph: ObjectGraph,
    input_data: InputData,
) -> None:
    # Evaluate
    graph.active_evaluation(graph.active_bundle, input_data)
