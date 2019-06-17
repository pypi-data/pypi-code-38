# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

'''
This module is basically a verbose convenience around concurrent.Futures
It should be removed - it is a compatibility layer for older patterns
that were used with requests_futures
'''


# These handlers are module-global for pickling reasons
def basic_handler(task, _):
    '''Returns task's result directly with no error handling'''
    return task.result()


def noraise_handler(task, logger):
    ''' Swallows (but logs) all Exceptions'''
    try:
        return task.result()
    except Exception as error:
        logger.error("Ignoring error from request: {0}".format(error))


class AsyncTask(object):
    '''
    An awaitable task.
    handler accepts (task, logger) and should return task.result() or raise
    '''

    def __init__(self, ident, task, logger, handler=None):
        self._id = ident
        self._logger = logger.getChild(ident)
        self._task = task
        if not handler:
            self._logger.debug("Using basic handler - no exception handling")
            self._handler = basic_handler
        else:
            self._handler = handler

    def ident(self):
        return self._id

    def wait(self):
        '''Wait until the task is done'''
        self._logger.debug("Waiting on Task {0}".format(self._id))
        return self._handler(self._task, self._logger)

    def cancel(self):
        '''
        https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.Future.cancel
        '''
        cancelled = self._task.cancel()
        self._logger.debug("Canceled Task {0}: {1}".format(self._id, cancelled))
        return cancelled

    def __repr__(self):
        ss = "AsyncTask({})".format(self._id)
        return ss

    def __lt__(self, other):
        return self._id < other._id
