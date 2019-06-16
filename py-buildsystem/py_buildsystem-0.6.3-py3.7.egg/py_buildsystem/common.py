import logging

FORMAT = '[%(levelname)s]: %(message)s'
MAX_LOG_LEVEL = 3

logging.basicConfig(format=FORMAT)

logger = logging.getLogger('root')

levels = {
    0: 40,
    1: 30,
    2: 20,
    3: 10,
}


