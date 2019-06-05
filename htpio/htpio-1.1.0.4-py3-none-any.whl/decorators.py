# Copyright (c) Hilscher GmbH. All Rights Reserved.
#
# $Author: bgeorgiev $
# $Date: 2019-05-16 11:34:02 +0300 (Thu, 16 May 2019) $
# $Revision: 654 $

"""
This module implement various decorators such as function calls and exception
logging. Decorators are used to implement additional functionality to a method
or function without changing its name.

Currently the following decorators are implemented :

 + @countcalls                - Counts the number of function calls
 + @logger(filename)          - Logs function exceptions to a give file

*** Example: ***

```python

    from htpio.decorators import Countcalls, Logger

    @Countcalls
    def f():
        pass

    count = 0
    for i in range(100):
        count = i + 1
        f()

    print(f.count(), count)
```

```python
    @Countcalls
    @Logger(LOGFILE)
    def f():
        return 1 / 0

    # Function under test
    raised = False
    try:
        f()
    except:
        raised = True
        logger.log.info("Number of calls==[{0}]".format(f.count()))
```
"""

# Compatibility imports
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

# System imports
import logging
import functools


"""
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  DECORATORS
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""


class Countcalls(object):
    """
    Decorator that keeps track of the number of times a function is called.
    https://wiki.python.org/moin/PythonDecoratorLibrary

    ***Example***:

    ```python
    from htpio.decorators import Countcalls

    @Countcalls
    def f():
        pass

    @Countcalls
    def g():
        pass

    count = 0
    for i in range(100):
        count = i + 1
        f()
        g()

    print(f.count())  # Number of calls for funciton f
    print(g.count())  # Number of calls for function g
    print(Countcalls.counts()) # Dump number of calls for f and g
    ```
    """

    # ----------------------------------------------------------------------

    instances = {}
    """ Stores the function names and number of calls"""

    # ----------------------------------------------------------------------
    def __init__(self, f):
        self.f = f
        self.numcalls = 0
        Countcalls.instances[f] = self
        functools.update_wrapper(self, f)

    # ----------------------------------------------------------------------
    def __call__(self, *args, **kwargs):
        """
        Wrapping call to original funciton.
        """

        self.numcalls += 1
        return self.f(*args, **kwargs)

    # ----------------------------------------------------------------------
    def count(self):
        """
        Return the number of times the function was called.
        """

        return Countcalls.instances[self.f].numcalls

    # ----------------------------------------------------------------------
    @staticmethod
    def counts():
        """
        Return a dictionary for all registered functions is keys and the
        number of function calls as values.
        """

        result = []
        for f in Countcalls.instances:
            result.append((f.__name__, Countcalls.instances[f].numcalls))

        return dict(result)


class Logger(object):
    """
    Decorator that logs exceptions into a given file.

    *** Example: ***

    ```python
    from htpio.decorators import Logger

    @Logger('c:\\test.log')
    def f():
        return 1 / 0

    # Function under test
    raised = False
    try:
        f()
    except:
        raised = True
        logger.log.info("Number of calls==[{0}]".format(f.count()))
    ```
    """

    # ----------------------------------------------------------------------

    log = logging.getLogger()
    """ Instance of a logging object"""

    logfile = ""
    """ Log file use to store the logs"""

    # ----------------------------------------------------------------------
    def __init__(self, logfile):

        Logger.logfile = logfile

        # logger instantiation
        Logger.log = logging.getLogger()
        Logger.log.setLevel(logging.INFO)

        # format output
        fmt = '%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s'
        formatter = logging.Formatter(fmt)

        # create the logging file handler
        fh = logging.FileHandler(Logger.logfile)
        fh.setFormatter(formatter)

        # add handler to logger object
        Logger.log.addHandler(fh)

    # ----------------------------------------------------------------------
    def __call__(self, function):
        """
        Wrapping call to original function.
        """

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)

            except Exception:

                # log the exception
                err = "Exception in  "
                err += function.__name__
                Logger.log.exception(err)

                # re-raise the exception
                raise

        return wrapper
