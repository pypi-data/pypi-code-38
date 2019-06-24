import logging
import socket
import functools
import requests
import bernhard
import click
from tlwatch import util
import urllib.parse

logger = logging.getLogger(__name__)

# https://api.etherscan.io/api?module=proxy&action=eth_blockNumber&apikey=YourApiKeyToken

name2url = {
    "kovan": "http://api-kovan.etherscan.io/api",
    "main": "https://api.etherscan.io/api",
}


def eth_blockNumber(chain: str):
    urlparams = {"module": "proxy", "action": "eth_blockNumber"}
    url = name2url[chain] + "?" + urllib.parse.urlencode(urlparams)
    response = requests.get(url, timeout=10.0).json().get("result")
    blockNumber = util.decode_hex_encoded_number(response)
    logger.info("GET %s => %s %s", url, response, blockNumber)

    return blockNumber


def watch_etherscan(chain):
    try:
        blocknumber = eth_blockNumber(chain)
        return [
            {
                "service": "etherscan.{}.blocknumber".format(chain),
                "host": socket.gethostname(),
                "state": "ok",
                "ttl": 30,
                "metric": blocknumber,
            }
        ]
    except KeyboardInterrupt:
        raise

    except BaseException as e:
        logger.warning("error in watch_etherscan:%s", e)
        return [
            {
                "service": "etherscan.{}.blocknumber".format(chain),
                "host": socket.gethostname(),
                "state": "error",
                "ttl": 30,
            }
        ]


@click.command()
@click.option("--riemann-host", default="localhost", envvar="RIEMANN_HOST")
@click.option("--riemann-port", default=5555, envvar="RIEMANN_PORT")
@click.option("--chain", default="main", type=click.Choice(name2url.keys()))
def etherscan(riemann_host, riemann_port, chain):
    """monitor etherscan for latest blocknumber"""
    logging.basicConfig(level=logging.INFO)
    logger.info("version %s starting", util.get_version())
    logger.info("watching %s at %s", chain, name2url[chain])
    util.watch_report_loop(
        lambda: bernhard.Client(riemann_host, riemann_port),
        functools.partial(watch_etherscan, chain),
        10,
    )
