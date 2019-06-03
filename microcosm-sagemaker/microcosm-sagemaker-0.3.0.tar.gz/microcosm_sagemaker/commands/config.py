from microcosm.config.model import Configuration
from microcosm.metadata import Metadata


def load_default_runserver_config(metadata: Metadata) -> Configuration:
    """
    Construct runserver default configuration.

    """

    config = Configuration(
        # We want our routes to come directly after the root /
        build_route_path=dict(
            prefix="",
        ),
    )

    return config
