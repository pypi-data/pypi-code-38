
import logging
import sys

def initLogger(console_level=logging.DEBUG, descriptor=""):
    """
    Set log level and descriptor
    :param console_level: debug if not specified
    :param descriptor: description for the log output - platform name and version by default
    """

    format_string = "%(asctime)s " + descriptor + "  [%(name)-7.7s]  [%(levelname)-6.6s]  :::  %(message)s"
    formatter = logging.Formatter(format_string, "%Y-%m-%d %H:%M:%S")
    original_stdout = sys.stdout

    # Root logger - set to debug to capture all output
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)

    # File handler
    f_handler = logging.FileHandler('vboxmanage.log', 'a')
    f_handler.setFormatter(formatter)
    f_handler.setLevel(logging.DEBUG)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(console_level)
    ch.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(f_handler)

    # Redirect STDOUT and STDERR to the log stream
    #sys.stderr = sys.stdout = StreamLogger(logging.getLogger("main"), logging.INFO)

def getLogger(name):

    l = logging.getLogger(name)

    crit_default = l.critical

    def critical(msg, *args, **kwargs):
        crit_default(msg, *args, **kwargs)
        exit(2)
        print()

    l.critical = critical

    return l

# Streamhandler for STDOUT and STDERR output
class StreamLogger(object):
    def __init__(self, logger, log_level):
        self.logger = logger
        self.log_level = log_level

    def write(self, message):
        for line in message.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass
