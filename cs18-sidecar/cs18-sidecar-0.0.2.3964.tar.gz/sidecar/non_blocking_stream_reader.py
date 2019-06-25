from queue import Queue, Empty
from threading import Thread

import time


class NonBlockingStreamReader:

    def __init__(self, stream, interval=1):

        self._s = stream
        self._q = Queue()
        self.to_break = False
        self.interval = interval

        def populate_queue(stream_in, queue):

            while True:
                try:
                    line = stream_in.readline()
                    if line:
                        queue.put(line)
                    if self.to_break:
                        break
                    time.sleep(1)
                except:
                    pass

        self._t = Thread(target=populate_queue,
                         args=(self._s, self._q))
        self._t.daemon = True
        self._t.start()  # start collecting lines from the stream

    def stop(self):
        self.to_break = True

    def read_line(self, timeout=None):
        try:
            return self._q.get(block=timeout is not None,
                               timeout=timeout)
        except Empty:
            return None


class UnexpectedEndOfStream(Exception):
    pass
