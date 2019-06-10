"""
Server that listens for request to run/cancel jobs.
Starts VMs and has them run various job stages.
"""

import os
import sys
import logging
from lando.server.config import ServerConfig
from lando.server.lando import Lando, CONFIG_FILE_NAME


def main():
    config_filename = os.environ.get("LANDO_CONFIG")
    if not config_filename:
        config_filename = CONFIG_FILE_NAME
    config = ServerConfig(config_filename)
    logging.basicConfig(stream=sys.stdout, level=config.log_level)
    lando = Lando(config)
    lando.listen_for_messages()

if __name__ == "__main__":
    main()
