"""
Command line program for running the worker: lando_worker.
Reads the worker config file for all it's settings.
"""

import os
from lando.worker.config import WorkerConfig
from lando.worker.worker import CONFIG_FILE_NAME, LandoWorker
from lando.server.lando import LANDO_QUEUE_NAME
import logging

ROOT_LOGFILE_NAME = '/tmp/lando-worker.log'


def main():
    config_filename = os.environ.get("LANDO_WORKER_CONFIG")
    if not config_filename:
        config_filename = CONFIG_FILE_NAME
    config = WorkerConfig(config_filename)
    logging.basicConfig(filename=ROOT_LOGFILE_NAME, level=config.log_level)
    worker = LandoWorker(config, outgoing_queue_name=LANDO_QUEUE_NAME)
    worker.listen_for_messages()

if __name__ == "__main__":
    main()
