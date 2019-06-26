import time

import sys
import signal


class RunnableThreadList(object):
    """
    List of :class:`~ievv_opensource.utils.ievvdevrun.runnables.base.AbstractRunnableThread`
    objects.

    You use this with the :setting:`IEVVTASKS_DEVRUN_RUNNABLES` setting
    to define what to run with ``ievv devrun``.
    """
    def __init__(self, *runnablethreads):
        """
        Parameters:
            runnablethreads: :class:`~ievv_opensource.utils.ievvdevrun.runnables.base.AbstractRunnableThread`
                objects to add to the list.
        """
        self._runnablethreads = []
        for runnablethread in runnablethreads:
            self.append(runnablethread)

    def append(self, runnablethread):
        """
        Append a :class:`~ievv_opensource.utils.ievvdevrun.runnables.base.AbstractRunnableThread`.

        Parameters:
            runnablethread: A :class:`~ievv_opensource.utils.ievvdevrun.runnables.base.AbstractRunnableThread`
                object.
        """
        self._runnablethreads.append(runnablethread)

    def start(self):
        """
        Start all the runnable threads and block until ``SIGTERM`` or
        ``KeyboardInterrupt``.
        """
        def start_all():
            for runnablethread in self._runnablethreads:
                runnablethread.start()

        def stop_all():
            for runnablethread in reversed(self._runnablethreads):
                runnablethread.stop()

        def join_all():
            for runnablethread in self._runnablethreads:
                runnablethread.join()

        def on_terminate(*args):
            print('')
            print('*' * 70)
            print('ievvdevrun terminated')
            print('*' * 70)
            stop_all()
            join_all()
            sys.exit(0)

        start_all()
        signal.signal(signal.SIGTERM, on_terminate)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            stop_all()
        join_all()
