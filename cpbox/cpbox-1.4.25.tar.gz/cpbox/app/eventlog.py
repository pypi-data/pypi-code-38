import json
import logging
import time
from cpbox.tool import timeutil

from cpbox.app.appconfig import appconfig

event_logger = logging.getLogger('event-log')


def add_event_log(event_key, payload):
    payload['env'] = appconfig.get_env()
    msg = 'cp %s %s' % (event_key, json.dumps(payload))
    event_logger.info(msg)

def add_app_monitor_log(key, value, time=None):
    time = time if time else timeutil.local_now_ios8061_str()
    data = {
            'event_key': key,
            'event_value': value,
            'time': time,
            }
    payload = {}
    payload['env'] = appconfig.get_env()
    payload['log'] = json.dumps(data)
    msg = 'app-monitor monitor-log %s' % (json.dumps(payload))
    event_logger.info(msg)


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
