# @Vendors
import os

# @Constants
from .packages.logger.assets.logTexts import (
    #TYPE_INFO,
    TYPE_ERR,
    TYPE_WRN,
    #TYPE_SUCCESS
)

CURRENT_BASE_PATH = os.path.dirname(os.path.realpath(__file__))
EXPORT_FORMAT = 'zip'
FILE_JOIN_OPERATOR = 'cat'
REMOTE_MODEL_SOURCE = {'path':'https://github.com/galias11', 'remote': True}
SPLIT_FILE_OPERATOR = 'split -a 1 -b'
DEBUG_MODE = False
LOG_LEVEL = [TYPE_WRN, TYPE_ERR]
LOG_PATH = CURRENT_BASE_PATH + '/logs/operation_log.log'
MAX_CONCURRENT_TASKS = 16
