import logging
import socket
import functools
import bernhard
import click
from tlwatch import util
import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)


def connect(dsn):
    return psycopg2.connect(dsn, cursor_factory=psycopg2.extras.RealDictCursor)


def build_event_from_row(row):
    return {
        "service": row["service"],
        "host": socket.gethostname(),
        "state": row.get("state", "ok"),
        "ttl": 30,
        "metric": row.get("metric", None),
    }


def watch_psql(query):
    try:
        with connect("") as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
        return [build_event_from_row(row) for row in rows] + [
            {
                "service": "watch.sqlquery.{}".format(query),
                "host": socket.gethostname(),
                "state": "ok",
                "ttl": 30,
            }
        ]
    except KeyboardInterrupt:
        raise

    except BaseException as e:
        logger.warning("error in watch_psql", e)
        return [
            {
                "service": "watch.sqlquery.{}".format(query),
                "host": socket.gethostname(),
                "state": "error",
                "description": str(e),
                "ttl": 30,
            }
        ]


@click.command()
@click.option("--riemann-host", default="localhost", envvar="RIEMANN_HOST")
@click.option("--riemann-port", default=5555, envvar="RIEMANN_PORT")
@click.option("--sqlquery", required=True)
def psql(riemann_host, riemann_port, sqlquery):
    """monitor query from a postgresql database"""
    logging.basicConfig(level=logging.INFO)
    logger.info("version %s starting", util.get_version())

    util.watch_report_loop(
        lambda: bernhard.Client(riemann_host, riemann_port),
        functools.partial(watch_psql, sqlquery),
        10,
    )
