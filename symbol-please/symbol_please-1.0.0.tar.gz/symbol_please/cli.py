"""Console script for symbol_please."""
import logging
import os
import sys

import click

import symbol_please
from symbol_please.config import load_config
import symbol_please.ui


_LOGGER = logging.getLogger(__name__)


def setup_logging():
    """Set up logging format.

    Copped from home assistant:
    https://github.com/home-assistant/home-assistant/blob/dc186841e2f387efecd3746c755ccb6b8ed51b0b/homeassistant/bootstrap.py#L226-L265
    """
    fmt = ("%(asctime)s %(levelname)s (%(threadName)s) "
           "[%(name)s] %(message)s")
    datefmt = '%Y-%m-%d %H:%M:%S'

    loglevel = os.environ.get("LOGLEVEL", "INFO")

    try:
        from colorlog import ColoredFormatter
        # basicConfig must be called after importing colorlog in order to
        # ensure that the handlers it sets up wraps the correct streams.
        logging.basicConfig(level=loglevel)

        colorfmt = "%(log_color)s{}%(reset)s".format(fmt)
        logging.getLogger().handlers[0].setFormatter(ColoredFormatter(
            colorfmt,
            datefmt=datefmt,
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red',
            }
        ))
    except ImportError:
        pass

    # If the above initialization failed for any reason, setup the default
    # formatting.  If the above succeeds, this wil result in a no-op.
    logging.basicConfig(format=fmt, datefmt=datefmt, level=loglevel)


@click.command()
def main(args=None):
    """Console script for symbol_please."""
    setup_logging()
    config = load_config()
    return symbol_please.ui.main(config)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
