import datetime
import argparse

parser = argparse.ArgumentParser(description = 'A program to hold and handle intermediate values in order to boost scientific experiments performance')
parser.add_argument('--debug', action = 'store', dest = 'debug_enabled', default = False, required = False, help = 'Enables cache action debugging')
arguments = parser.parse_args()

def _log(mode, message):
    print("[{2}][{0}]: {1}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message, mode))


def debug(message):
    if arguments.debug_enabled == 'True':
        _log("DEBUG", message)


def error(message):
    _log("ERROR", message)


def warn(message):
    _log("WARN ", message)
