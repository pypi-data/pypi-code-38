"""
Example CRUD routes tests.

Tests are sunny day cases under the assumption that framework conventions
handle most error conditions.

"""
from pathlib import Path

from microcosm.loaders import load_from_dict

from microcosm_sagemaker.app_hooks import create_serve_app


class RouteTestCase:
    """
    Helper base class for writing tests of a route.

    """
    root_input_artifact_path: Path

    def setup(self) -> None:
        self.graph = create_serve_app(
            testing=True,
            extra_loader=load_from_dict(
                root_input_artifact_path=self.root_input_artifact_path,
            ),
        )

        self.client = self.graph.flask.test_client()
