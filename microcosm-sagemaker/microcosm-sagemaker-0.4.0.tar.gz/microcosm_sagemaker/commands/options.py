from click import Path, option

from microcosm_sagemaker.artifact import RootInputArtifact, RootOutputArtifact
from microcosm_sagemaker.constants import SagemakerPath
from microcosm_sagemaker.input_data import InputData


def input_data_option():
    return option(
        "--input-data",
        type=Path(
            resolve_path=True,
            file_okay=False,
            exists=True,
        ),
        callback=_make_click_callback(InputData),
        default=SagemakerPath.INPUT_DATA,
        help="Path of the folder that houses the train/test datasets",
    )


def input_artifact_option():
    return option(
        "--input-artifact",
        type=Path(
            resolve_path=True,
            file_okay=False,
            exists=True,
        ),
        callback=_make_click_callback(RootInputArtifact),
        default=SagemakerPath.MODEL,
        help="Path from which to load artifact",
    )


def output_artifact_option():
    return option(
        "--output-artifact",
        type=Path(
            resolve_path=True,
            file_okay=False,
            writable=True,
        ),
        callback=_make_click_callback(RootOutputArtifact),
        default=SagemakerPath.MODEL,
        help="Path for outputting trained artifact",
    )


def _make_click_callback(function):
    """
    Given a `function`, returns a callback function that can be used for a
    click option's `callback=` to apply `function` to the value before passing
    the argument to the command

    """
    def callback(ctx, param, value):
        return function(value)

    return callback
