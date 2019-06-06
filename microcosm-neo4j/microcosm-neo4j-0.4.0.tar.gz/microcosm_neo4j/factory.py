"""
Neo4J driver factory.

"""
from logging import INFO, getLogger

from microcosm.api import defaults, typed
from microcosm.config.types import boolean
from neo4j import GraphDatabase


@defaults(
    # NB: some features are not available unless enabled
    enterprise=typed(boolean, default_value=False),
    password="password",
    uri=None,
    username="neo4j",
    max_connection_pool_size=typed(int, default_value=1),
    connection_acquisition_timeout=typed(int, default_value=2)  # in seconds
)
def configure_neo4j_driver(graph):
    if graph.metadata.testing:
        logger = getLogger("neobolt")
        logger.level = INFO

        default_uri = "bolt://localhost:17687"
    else:
        default_uri = "bolt://localhost:7687"

    def wrapper():
        return GraphDatabase.driver(
            graph.config.neo4j.uri or default_uri,
            auth=(
                graph.config.neo4j.username,
                graph.config.neo4j.password,
            ),
            max_connection_pool_size=graph.config.neo4j.max_connection_pool_size,
            connection_acquisition_timeout=graph.config.neo4j.connection_acquisition_timeout,
        )
    return wrapper
