import logging
import functools
import requests
import bernhard
import click
import urllib.parse
from tlwatch import util

logger = logging.getLogger(__name__)


def watch_relay(url):
    host = urllib.parse.urlparse(url).netloc
    networks_url = urllib.parse.urljoin(url, "/api/v1/networks")
    description = ""
    try:
        if len(requests.get(networks_url, timeout=10).json()) == 0:
            state = "error"
            description = "no networks"
        else:
            state = "ok"
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logger.warning("error in watch_relay:%s", e)
        state = "error"
        description = str(e)

    return [
        {
            "service": "relay.basic-operation",
            "host": host,
            "state": state,
            "ttl": 60,
            "description": description,
        }
    ]


@click.command()
@click.option("--riemann-host", default="localhost", envvar="RIEMANN_HOST")
@click.option("--riemann-port", default=5555, envvar="RIEMANN_PORT")
@click.option("--url", default="http://localhost:5000")
def relay(riemann_host, riemann_port, url):
    """monitor relay server"""
    logging.basicConfig(level=logging.INFO)
    logger.info("version %s starting", util.get_version())
    logger.info("watching %s", url)
    util.watch_report_loop(
        lambda: bernhard.Client(riemann_host, riemann_port),
        functools.partial(watch_relay, url),
        10,
    )
