from datetime import datetime

from cpbox.app.appconfig import appconfig
from cpbox.tool import concurrent
from cpbox.tool import timeutil

import time
import os
import threading
import json
import logging
import socket

try:
    from threading import get_ident
except ImportError:
    from thread import get_ident

event_logger = logging.getLogger('event-log')

log_worker = concurrent.Worker(2)
def add_event_log(event_key, payload):
    payload['env'] = appconfig.get_env()
    msg = 'cp %s %s' % (event_key, json.dumps(payload))
    log_worker.submit(event_logger.info, msg)

def log_func_call(func, *args, **kwargs):
    def timed(*args, **kw):
        start = time.time() * 1000
        result = func(*args, **kw)
        payload = {}
        payload['name'] = func.__name__
        payload['rt'] = time.time() * 1000 - start
        add_event_log('func-call', payload)
        return result
    return timed
