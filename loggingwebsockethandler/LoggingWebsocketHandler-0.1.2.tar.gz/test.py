# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import time

import LoggingWebsocketHandler

url = 'ws://localhost:7788/channel/1'
hdl = LoggingWebsocketHandler.WebsocketHandler(url)
hdl.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
hdl.setLevel(logging.DEBUG)

LOGGER = logging.getLogger('test')
LOGGER.handlers.clear()
LOGGER.addHandler(hdl)
LOGGER.setLevel(logging.DEBUG)


while True:
    LOGGER.info(str(datetime.now()))
    time.sleep(1)
