import sys
import logging
import logging.handlers


RESET = '\033[0m'
BOLD = '\033[1m'
GREEN = '\033[92m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RED = '\033[38;5;197m'


def _setup_user_logger():
    logger = logging.getLogger('user_logger')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('{1}%(asctime)s{2} [{0}%(levelname)s{2}]\
 %(message)s'.format(CYAN, GREEN, RESET))
    sh_info = logging.StreamHandler(sys.stdout)
    sh_info.setFormatter(formatter)
    logger.addHandler(sh_info)


def _setup_global_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('{1}%(asctime)s{2} [{0}%(levelname)s{2}]\
        %(message)s'.format(CYAN, GREEN, RESET))
    sh_info = logging.StreamHandler(sys.stdout)
    sh_info.setFormatter(formatter)
    logger.addHandler(sh_info)


def setup_logging(args):

    logging.VERBOSE = 5

    logging.getLogger().handlers = []

    if args.verbose:
        _setup_user_logger()

    if args.very_verbose:
        _setup_global_logger()


def debug(msg, *args):
    logging.getLogger('user_logger').debug(msg, *args)


def debug_cyan(msg, *args):
    logging.getLogger('user_logger').debug(CYAN + msg + RESET, *args)


def debug_red(msg, *args):
    logging.getLogger('user_logger').debug(RED + msg + RESET, *args)
