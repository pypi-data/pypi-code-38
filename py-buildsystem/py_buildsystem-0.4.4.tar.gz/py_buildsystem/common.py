import logging

FORMAT = '[%(levelname)s]: %(message)s'

logging.basicConfig(format=FORMAT)

logger = logging.getLogger('root')

levels = {
    "CRITICAL": 50,
    "ERROR": 40,
    "WARNING": 30,
    "INFO": 20,
    "DEBUG": 10,
    "NOTSET": 0,
}
