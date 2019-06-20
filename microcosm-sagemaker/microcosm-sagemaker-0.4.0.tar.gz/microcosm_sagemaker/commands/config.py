from microcosm.config.model import Configuration
from microcosm.metadata import Metadata

from microcosm_sagemaker.constants import SagemakerPath


def load_default_microcosm_runserver_config(metadata: Metadata) -> Configuration:
    """
    Construct runserver default configuration.

    """

    config = Configuration(
        # We want our routes to come directly after the root /
        build_route_path=dict(
            prefix="",
        ),

        root_input_artifact_path=SagemakerPath.MODEL,
    )

    return config
