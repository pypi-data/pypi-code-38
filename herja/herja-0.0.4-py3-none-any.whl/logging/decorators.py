"""A logging decorator file for automagically logging things related to functions."""


import logging
from functools import wraps


class LogLevelContainer(object):
    """A class object to hold a logging level, for use when inherited."""

    def __init__(self, level=logging.NOTSET):
        """Store a log level."""
        self.level = level


class LogSteps(LogLevelContainer):
    """A class object to hold a logging level and report when a function is entered and exited."""

    def __call__(self, function):
        """Report when a function enters and exits."""
        @wraps(function)
        def wrapper(*args, **kwargs):
            logging.log(self.level, 'Function: %s, Enter', function.__name__)
            result = function(*args, **kwargs)
            logging.log(self.level, 'Function: %s, Exit', function.__name__)
            return result
        return wrapper


class LogArguments(LogLevelContainer):
    """A class object to hold a logging level and report the args and kwargs of a decorated function."""

    def __call__(self, function):
        """Log the args and kwargs of the decorated function."""
        @wraps(function)
        def wrapper(*args, **kwargs):
            for arg in args:
                logging.log(self.level, 'Function: %s, Arg: %r', function.__name__, arg)
            for k in kwargs:
                logging.log(self.level, 'Function: %s, Key: %r, Value: %r', function.__name__, k, kwargs[k])
            return function(*args, **kwargs)
        return wrapper


class LogExceptions(LogLevelContainer):
    """A class object to hold a logging level and report any exceptions that are raised."""

    def __call__(self, function):
        """Log any exceptions that are raised."""
        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except BaseException as e:
                logging.log(self.level, 'Exception: %r, %r', e, e.args)
                raise e
        return wrapper


class LogResult(LogLevelContainer):
    """A class object to hold a logging level and report the result of a function at that level."""

    def __call__(self, function):
        """Log the result of a decorated function."""
        @wraps(function)
        def wrapper(*args, **kwargs):
            result = function(*args, **kwargs)
            logging.log(self.level, 'Function: %s, Result: %r', function.__name__, result)
            return result
        return wrapper


class LogAll(LogLevelContainer):
    """A class object to log entry, args, kwargs, result, and exit of a function."""

    def __call__(self, function):
        """Wrap a bunch of decorators around the given function so information is logged."""
        @wraps(function)
        def wrapper(*args, **kwargs):

            # log enter
            logging.log(self.level, 'Function: %s, Enter', function.__name__)

            # log arguments
            for arg in args:
                logging.log(self.level, 'Function: %s, Arg: %r', function.__name__, arg)
            for k in kwargs:
                logging.log(self.level, 'Function: %s, Key: %r, Value: %r', function.__name__, k, kwargs[k])

            # log exceptions
            try:
                result = function(*args, **kwargs)
            except BaseException as e:
                logging.log(self.level, 'Exception: %r, %r', e, e.args)
                raise e

            # log result
            logging.log(self.level, 'Function: %s, Result: %r', function.__name__, result)

            # log exit
            logging.log(self.level, 'Function: %s, Exit', function.__name__)
            return result

        return wrapper


class LogDecoratorContainer(object):
    """An object to be created that houses decorator functions."""

    def __init__(self, level=logging.NOTSET):
        """Assign the decorations to self."""
        self.steps = LogSteps(level)
        self.args = LogArguments(level)
        self.exceptions = LogExceptions(level)
        self.result = LogResult(level)
        self.all = LogAll(level)


# define some convenient decorator containers
notset = LogDecoratorContainer(logging.NOTSET)
debug = LogDecoratorContainer(logging.DEBUG)
info = LogDecoratorContainer(logging.INFO)
warning = LogDecoratorContainer(logging.WARNING)
error = LogDecoratorContainer(logging.ERROR)
critical = LogDecoratorContainer(logging.CRITICAL)
