# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from contextlib import ContextDecorator
import os
import sys

IS_OSX = sys.platform == 'darwin'
IS_WINDOWS = os.name == 'nt'

if IS_OSX:
    from . import macos as c
else:
    from . import dummy_os as c


class ActivityContext(ContextDecorator):
    """Context disabling idle sleep and App Nap"""
    def __init__(self, options, message):
        self.n_processes = 0
        self.options = options
        self.message = message

    def __enter__(self):
        if self.n_processes == 0 and IS_OSX:
            self._activity = c.begin_activity(self.options, self.message)
        self.n_processes += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.n_processes -= 1
        if self.n_processes == 0 and IS_OSX:
            c.end_activity(self._activity)


user_activity = ActivityContext(c.NSActivityUserInitiated, 'Eelbrain user activity')


def restore_main_spec():
    """On windows, running a multiprocessing job seems to sometimes remove this attribute"""
    if IS_WINDOWS:
        main_module = sys.modules['__main__']
        if not hasattr(main_module, '__spec__'):
            main_module.__spec__ = None
