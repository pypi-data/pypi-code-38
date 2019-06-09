import threading
import traceback
from . import log


class Runnable:
    """
    Base class for all objects that contain threads or processes.

    The way to use a Runnable is like a context manager:

    with some_runnable() as runnable:
         add_some_callbacks(runnable)
         more_stuff_that_runs_on_start()

         # Depending on the thread category, the `Runnable` isn't guaranteed to
         # actually "go off" until the end of this block.

    """

    Event = None
    Runner = None
    timeout = 0.1

    def __init__(self, run_once, **kwds):
        self.run_once = run_once
        self.runner = self.Runner(target=self.target, **kwds)
        self.start_event = self.Event()
        self.stop_event = self.Event()

    def start(self):
        if self.start_event.set():
            raise ValueError('Runnable has already been started')
        self.runner.start()

    def stop(self):
        self.stop_event.set()

    def target(self):
        self.start_event.set()
        try:
            while not self.stop_event.is_set():
                self.run_once()
        except Exception:
            self.stop_event.set()
            log.error('Exception at %s: \n%s', self, traceback.format_exc())

    def __enter__(self):
        self.start()
        self.start_event.wait(self.timeout)
        return self

    def __exit__(self, *args):
        self.stop()


class ThreadRunnable(Runnable):
    Event = threading.Event
    Runner = threading.Thread

    def __init__(self, run_once, daemon=True, **kwds):
        super().__init__(run_once, daemon=daemon, **kwds)


def queue_reader(receive, queue, timeout=0.1):
    def run_once():
        try:
            msg = queue.get(timeout=timeout)
        except queue.Empty:
            pass
        else:
            receive(msg)

    return run_once
