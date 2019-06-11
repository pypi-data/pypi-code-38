import os
import signal
import time
import multiprocessing


def direct(f, *args, **kwargs):
    """Runs a task in the current process. This is a very thin wrapper around
    a direct function call."""
    return f(*args, **kwargs)


class Subprocess(object):
    sleep = 3600

    """Runs a task in N subprocesses. The current process is suspended (using
    sleep) until an exception is raised on this process."""

    def __init__(self, process_count):
        self.process_count = process_count

    def __call__(self, f, *args, **kwargs):
        def add_worker_number(original_kwargs, index):
            return dict(original_kwargs, **dict(worker_number=index))

        processes = [
            multiprocessing.Process(target=f, args=args, kwargs=add_worker_number(kwargs, index))
            for index in range(self.process_count)
        ]

        try:
            for process in processes:
                process.start()

            while True:
                time.sleep(self.sleep)
        finally:
            # process.terminate() would send SIGTERM and abruptly terminate
            # all children. SIGINT is a little more graceful; it gives each
            # process a chance to finish what it's doing (or abort, more
            # likely) and hang up.
            for process in processes:
                os.kill(process.pid, signal.SIGINT)
            for process in processes:
                process.join()
