import argparse
import json
import logging
import os
import sys

import humanfriendly

from qmenta.sdk import __version__
from qmenta.sdk.client import ExecClient
from qmenta.sdk.communication import CommunicationObject
from qmenta.sdk.context import AnalysisContext

log_levels = {
    'info': logging.INFO,
    'debug': logging.DEBUG,
}

default_chunk_size = '512KiB'


def setup_logging(log_level, log_path=os.path.abspath('exec.log')):
    # Logging settings
    root_logger = logging.getLogger()
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s %(name)s:%(lineno)d :: %(message)s')
    root_logger.setLevel(log_level)

    # File handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # get urlib3 to stop spamming the logs
    logging.getLogger(
        'requests.packages.urllib3.connectionpool').setLevel(logging.WARN)

    return log_path


def parse_args():
    metadata = json.dumps({'version': __version__},
                          sort_keys=True, indent=4) + '\n'

    argp = argparse.ArgumentParser(
        description="Executor for external developers (SDK version {})".format(__version__))
    argp.add_argument('--project', type=int, required=True, help='Project ID')
    argp.add_argument('--analysis', type=int,
                      required=True, help='Analysis ID')
    argp.add_argument('--url', required=True, help='Platform URL')
    argp.add_argument('--token', required=True,
                      help='Access token for the API')
    argp.add_argument('--tool-path', required=True,
                      help='Path to the Python tool (package.module:function) to be executed')

    # verbosity
    argp.add_argument('--log-level', choices=log_levels,
                      default='info', help='Logging level')

    # chunk size of downloads / uploads
    argp.add_argument('--chunk-size', type=str, default=default_chunk_size,
                      help='Size of each chunk in download/upload operations, expressed in a human readable data size. '
                           '(e.g. 256 --> 256 bytes ; 512B --> 512 bytes ; 1MiB --> 1048576 bytes; 1MB --> 1000000')

    # only for testing purposes
    argp.add_argument('--allow-insecure', type=bool, nargs='?', const=True, default=False,
                      help='Avoid checking certificates for HTTPS requests')
    argp.add_argument('--no-retry', type=bool, nargs='?', const=True, default=False,
                      help='Ignore requests total_retry number and fail after each first errror')

    # metadata
    argp.add_argument('--version', action='version', version=__version__)
    argp.add_argument('--metadata', action='version', version=metadata)

    return argp.parse_args()


def main():
    arguments = parse_args()
    log_path = setup_logging(log_levels[arguments.log_level])

    # Prepare client to run analysis
    chunk_size = humanfriendly.parse_size(arguments.chunk_size, binary=True)
    with CommunicationObject(arguments.url, arguments.project, arguments.token,
                             verify=not arguments.allow_insecure, chunk_size=chunk_size,
                             critical=arguments.no_retry) as comm:

        context = AnalysisContext(arguments.analysis, comm)
        client = ExecClient(arguments.analysis, comm, context, log_path)

        logger = logging.getLogger(__name__)
        logger.info("Using SDK version: {}".format(__version__))

        # Run it
        try:
            client(arguments.tool_path)
        except Exception as e:
            logger.exception(e)
            raise SystemExit(1)


if __name__ == '__main__':
    main()
