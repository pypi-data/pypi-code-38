import argparse
import logging
import os
import sys

from qmenta.sdk import __version__
from qmenta.sdk.directory_utils import mkdirs
from qmenta.sdk.executor import log_levels
from qmenta.sdk.local.client import LocalExecClient
from qmenta.sdk.local.context import LocalAnalysisContext
from qmenta.sdk.local.parse_settings import parse_tool_settings


def parse_args():
    argp = argparse.ArgumentParser(
        description='Local executor for debugging and testing purposes (SDK version {})'.format(__version__)
    )
    argp.add_argument(
        'settings', help='JSON file that defines the settings of the tool to be run. Uses same syntax as in platform. '
                         'See qmenta_sdk/examples/'
    )
    argp.add_argument(
        'input_settings', help='JSON file that defines the input values for the settings.'
    )
    argp.add_argument(
        'src_folder', help='Source folder where the inputs of the analysis are stored.'
                           'That is you "get_files" from this folder, that represents an input container.'
    )
    argp.add_argument(
        'dst_folder', help='Destination folder where the outputs of the analysis will be stored.'
                           'That is, when you "upload_file", the file is stored in this folder.'
    )
    argp.add_argument(
        '--res-folder', help='Folder where the different template files required by the analysis are stored.',
        default=None
    )
    argp.add_argument(
        '--tool-path', required=True, help='Path to the Python tool (package.module:function) to be executed'
    )
    argp.add_argument('--log-path', help='Log file')
    argp.add_argument('--log-level', choices=log_levels, default='debug', help='Logging level')

    # version
    argp.add_argument('--version', action='version', version=__version__)

    return argp.parse_args()


def setup_logging(log_level, log_path=os.path.abspath('exec.log')):
    # Logging settings
    root_logger = logging.getLogger()
    formatter = logging.Formatter('[%(asctime)s] %(name)s:%(lineno)d %(levelname)s :: %(message)s')
    root_logger.setLevel(log_level)

    # File handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    return log_path


def main():
    arguments = parse_args()

    mkdirs(arguments.dst_folder)

    log_path = arguments.log_path if arguments.log_path is not None else os.path.join(arguments.dst_folder, 'exec.log')
    setup_logging(log_levels[arguments.log_level], log_path=log_path)

    # Parse settings
    settings = parse_tool_settings(arguments.settings, arguments.input_settings)

    # Instantiate client
    context = LocalAnalysisContext(settings, arguments.src_folder, arguments.dst_folder, arguments.res_folder)
    client = LocalExecClient(context, log_path)

    logger = logging.getLogger(__name__)
    logger.info("Using SDK version (local emulation): {}".format(__version__))

    # Run it
    try:
        client(arguments.tool_path)
    except Exception:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
