# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Timer utility classes."""

from threading import Timer


class TimerCallback(object):
    """Class for timer callback."""

    def __init__(self, interval=1, logger=None, callback=None, *args, **kwargs):
        """
        Initialize timer callback.

        :type logger: logger
        :param interval: callback interval
        :param callback:  function to be called
        :param args: args
        :param kwargs: kwargs
        """
        self.logger = logger
        self._timer = None
        self.callback = callback
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.stop_requested = False
        self.start()

    def _run(self):
        """
        Invoke the callback.

        :return: None
        """
        try:
            if self.callback is not None:
                self.callback(*self.args, **self.kwargs)
        except Exception:
            # aml logger may not be available at this time.
            pass
        finally:
            if not self.stop_requested:
                self.is_running = False
                self.start()

    def start(self):
        """
        Start the timer for callback.

        :return:
        """
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.daemon = True
            self._timer.start()
            self.is_running = True

    def stop(self):
        """
        Stop the timer.

        :return:
        """
        self.stop_requested = True
        self._timer.cancel()
        self.is_running = False
