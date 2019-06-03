"""
Loaders to inject SM parameters as microcosm configurations.

"""
import json

from boto3 import client
from microcosm.config.model import Configuration
from microcosm.loaders.compose import merge
from microcosm.loaders.keys import expand_config
from microcosm.metadata import Metadata

from microcosm_sagemaker.constants import SagemakerPath
from microcosm_sagemaker.s3 import S3Object


def load_from_hyperparameters(metadata: Metadata) -> Configuration:
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


def load_from_s3(url: str) -> Configuration:
    """
    Loads a S3 formatted url that points to a remote json file, and parses it into a local
    configuration variable.

    """
    def _load(metadata):
        s3 = client("s3")
        s3_object = S3Object.from_url(url)

        object = s3.get_object(Bucket=s3_object.bucket, Key=s3_object.key)
        return Configuration(json.loads(object["Body"].read()))

    return _load


def load_train_conventions(metadata: Metadata) -> Configuration:
    """
    Opinionated loader that:
    1. Reads all of the hyperparameters passed through by SageMaker
    2. Uses a special `base_configuration` key to read the given configuration from S3

    """
    configuration = load_from_hyperparameters(metadata)
    base_configuration_url = configuration.pop("base_configuration", None)

    if base_configuration_url:
        remote_configuration = load_from_s3(base_configuration_url)(metadata)

        # Locally specified hyperparameters should take precedence over the
        # base configuration
        configuration = merge([
            remote_configuration,
            configuration,
        ])

    return configuration


def load_serve_conventions(metadata: Metadata) -> Configuration:
    """
    Loads the configuration.json file from the input artifact directory on the docker

    """
    model_path = SagemakerPath.MODEL
    config_path = model_path / "configuration.json"

    try:
        with open(config_path) as raw_file:
            return expand_config(
                json.load(raw_file),
                skip_to=0,
            )

    except FileNotFoundError:
        return Configuration()
