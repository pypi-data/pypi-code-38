"""
Read configuration from a location determined by the library.
"""
import logging
import logging.config
import os
from functools import lru_cache

import miniscule
import yaml

log = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def read_config(path=None):
    """Read configuration from a prespecified location: the contents of the
    CONFIG environment variable, or top-level config.yaml.  Wraps the `miniscule
    <https://pypi.org/project/miniscule/>`_ package, and uses its mechanism to
    resolve YAML tags.

    :param path: Override the default path specified in the environment
        variable.

    :returns: A Python dictionary with configuration information.  The path of
              the configuration file is under the key `__path`.
    """
    path = path or os.environ.get("CONFIG", "config.yaml")
    try:
        config = miniscule.read_config(path)
        config["__path"] = path
        return config
    except FileNotFoundError:
        print("No file at", path)
        return None


def init_logging(path):
    # Let the application take care of logging
    logging.getLogger("werkzeug").handlers = []
    if path is None:
        return

    with open(path, "r") as handle:
        log_config = yaml.load(handle.read(), Loader=yaml.SafeLoader)
        logging.config.dictConfig(log_config)
