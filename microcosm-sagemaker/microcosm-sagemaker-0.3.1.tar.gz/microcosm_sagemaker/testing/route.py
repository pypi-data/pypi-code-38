"""
Example CRUD routes tests.

Tests are sunny day cases under the assumption that framework conventions
handle most error conditions.

"""
from pathlib import Path

from microcosm.loaders import load_each

from microcosm_sagemaker.app_hooks import create_serve_app
from microcosm_sagemaker.artifact import RootInputArtifact
from microcosm_sagemaker.commands.config import load_default_runserver_config


class RouteTestCase:
    """
    Helper base class for writing tests of a route.

    """
    root_input_artifact_path: Path

    def setup(self) -> None:
        root_input_artifact = RootInputArtifact(self.root_input_artifact_path)

        self.graph = create_serve_app(
            testing=True,
            extra_loader=load_each(
                load_default_runserver_config,
                root_input_artifact.load_config,
            ),
        )

        self.client = self.graph.flask.test_client()

        self.graph.load_bundle_and_dependencies(
            bundle=self.graph.active_bundle,
            root_input_artifact=root_input_artifact,
        )
