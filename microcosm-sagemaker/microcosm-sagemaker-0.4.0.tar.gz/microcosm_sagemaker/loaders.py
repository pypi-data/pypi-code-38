"""
Loaders to inject SM parameters as microcosm configurations.

"""
import json

from boto3 import client
from microcosm.config.model import Configuration
from microcosm.loaders import load_each
from microcosm.loaders.compose import two_stage_loader
from microcosm.loaders.keys import expand_config
from microcosm.metadata import Metadata
from microcosm.typing import Loader

from microcosm_sagemaker.artifact import RootInputArtifact
from microcosm_sagemaker.commands.config import load_default_microcosm_runserver_config
from microcosm_sagemaker.constants import SagemakerPath
from microcosm_sagemaker.s3 import S3Object


def hyperparameter_loader(metadata: Metadata) -> Configuration:
    """
    Sagemaker only supports single-layer hyperparameters, so we use double underscores
    (__) to signify the delineation between nested dictionaries.  This mirrors the
    formatting of our ENV variables.  Note that these values are all strings by convention,
    so any end applications should.

    This configuration helper parses these into the underlying dictionary structure.

    """
    try:
        with open(SagemakerPath.HYPERPARAMETERS) as raw_file:
            return expand_config(
                json.load(raw_file),
                separator="__",
                skip_to=0,
            )

    except FileNotFoundError:
        return Configuration()


def s3_loader(metadata: Metadata, configuration: Configuration) -> Configuration:
    """
    Opinionated loader that:
    1. Reads all of the hyperparameters passed through by SageMaker
    2. Uses a special `base_configuration` key to read the given configuration from S3

    """
    base_configuration_url = configuration.get("base_configuration", None)

    if base_configuration_url:
        s3 = client("s3")
        s3_object = S3Object.from_url(base_configuration_url)

        object = s3.get_object(Bucket=s3_object.bucket, Key=s3_object.key)
        return Configuration(json.loads(object["Body"].read()))

    return Configuration()


def root_input_artifact_config_loader(metadata: Metadata, config: Configuration) -> Configuration:
    root_input_artifact = RootInputArtifact(config.root_input_artifact_path)

    return root_input_artifact.load_config(metadata)


def train_conventions_loader(initial_loader: Loader) -> Loader:
    return two_stage_loader(
        primary_loader=load_each(
            hyperparameter_loader,
            initial_loader,
        ),
        secondary_loader=s3_loader,
    )


def serve_conventions_loader(initial_loader: Loader) -> Loader:
    return two_stage_loader(
        primary_loader=load_each(
            load_default_microcosm_runserver_config,
            initial_loader,
        ),
        secondary_loader=root_input_artifact_config_loader,
    )


def evaluate_conventions_loader(initial_loader: Loader) -> Loader:
    return two_stage_loader(
        primary_loader=initial_loader,
        secondary_loader=root_input_artifact_config_loader,
    )
