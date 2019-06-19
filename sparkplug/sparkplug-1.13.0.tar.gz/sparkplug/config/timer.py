
import datetime, traceback
from sparkplug.logutils import LazyLogger
from sparkplug.config.timereporter import registry

_log = LazyLogger(__name__)

##################################################

class Timer(object):
    def __init__(self, callback, timers=[]):
        self._timers = tuple(registry[t] for t in timers if t in registry)
        self._callback = callback


    def __call__(self, msg):
        ret = None
        
        try:
            start_time = datetime.datetime.now()
            if hasattr(msg, "application_headers") and ("timestamp_in_ms" in msg.application_headers):
                began_at = datetime.datetime.fromtimestamp(float(msg.application_headers['timestamp_in_ms']) * (1.0/1000.0))
                wait_time = start_time - began_at
                try:
                    for t in self._timers:
                        t.append_wait(wait_time)
                except:
                    _log.error(traceback.format_exc())

            ret = self._callback(msg)

        except Exception as e:
            try:
                erro_time = datetime.datetime.now() - start_time
                for t in self._timers:
                    t.append_erro(erro_time)
            except:
                _log.error(traceback.format_exc())

            raise e

        else:
            try:
                exec_time = datetime.datetime.now() - start_time
                for t in self._timers:
                    t.append_exec(exec_time)
            except:
                _log.error(traceback.format_exc())


        return ret
