# coding:utf-8
from fluent import sender
import queue
import threading
import traceback
import time


class FluentPilot(object):

    def __init__(self, host, port, app, tag):
        self.__sender = sender.FluentSender(app, host=host, port=int(port))
        self.__msg_queue = queue.Queue()
        self.__tag = tag
        self._start = False
        self._child_thread = None
        self._to_fluent()

    def _to_fluent(self):
        def _flush():
            while True:
                if not self._start:
                    break
                try:
                    msg = self.__msg_queue.get()
                    msg = msg.strip()
                    if not msg:
                        continue
                    pet = {
                        "log": msg
                    }
                    r = self.__sender.emit_with_time(self.__tag, time.time(), pet)
                    if not r:
                        raise Exception("Fluent emit return False")
                except Exception as e:
                    traceback.print_exc()
                    continue
                finally:
                    self.__msg_queue.task_done()
        self._child_thread = threading.Thread(target=_flush)
        self._start = True
        self._child_thread.setDaemon(True)
        self._child_thread.start()

    def flush(self):
        return self.__msg_queue.join()

    def pub(self, msg):
        self.__msg_queue.put(msg)
