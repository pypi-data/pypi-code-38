"""
Main web service CLI

"""
from click import command, option
from microcosm.loaders import load_each
from microcosm.object_graph import ObjectGraph

from microcosm_sagemaker.app_hooks import create_serve_app
from microcosm_sagemaker.artifact import RootInputArtifact
from microcosm_sagemaker.commands.config import load_default_runserver_config
from microcosm_sagemaker.commands.options import input_artifact_option


@command()
@option(
    "--host",
    default="127.0.0.1",
)
@option(
    "--port",
    type=int,
)
@option(
    "--debug/--no-debug",
    default=False,
)
@input_artifact_option()
def main(host, port, debug, input_artifact):
    graph = create_serve_app(
        debug=debug,
        extra_loader=load_each(
            load_default_runserver_config,
            input_artifact.load_config,
        ),
    )

    run_serve(
        graph=graph,
        root_input_artifact=input_artifact,
        host=host,
        port=port,
    )


def run_serve(
    graph: ObjectGraph,
    root_input_artifact: RootInputArtifact,
    host: str,
    port: int,
) -> None:
    graph.load_bundle_and_dependencies(
        bundle=graph.active_bundle,
        root_input_artifact=root_input_artifact,
    )

    graph.flask.run(
        host=host,
        port=port or graph.config.flask.port,
    )
