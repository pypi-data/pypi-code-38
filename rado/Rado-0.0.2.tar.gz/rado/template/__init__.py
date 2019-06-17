import sys
import os

from datetime import datetime
from rado import BaseTest

from rado.core import exceptions, logger


sys.path.append('./')


class TestBaseTest(BaseTest):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }

    log_file = f'./logs/skyTest_\
{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.log'
    if not os.path.exists('logs'):
        os.mkdir('logs')
    log_level = "DEBUG"
    logger.setup_logger(log_level, log_file)
