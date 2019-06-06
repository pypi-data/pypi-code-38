"""
Create databases.

"""
from argparse import ArgumentParser
from warnings import warn

from microcosm_neo4j.context import SessionContext


def parse_args(graph):
    parser = ArgumentParser()
    parser.add_argument("--drop", "-D", action="store_true")
    return parser.parse_args()


def main(graph):
    """
    Create and drop databases.

    """
    args = parse_args(graph)

    with SessionContext(graph):
        if args.drop:
            warn(
                "Deleting all Neo4J nodes is not recommended for production systems. "
                "Delete Neo4J file system data instead."
            )
            graph.neo4j_schema_manager.drop_all(force=True)
        graph.neo4j_schema_manager.create_all()
