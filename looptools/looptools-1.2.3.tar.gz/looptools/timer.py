from time import time
from decimal import Decimal


_TIMES = []


def now():
    """Capture the current time."""
    return time()


def rounder(exact, decimals=2):
    """Round a float to a certain number of decimal places."""
    return round(Decimal(exact), decimals)


def human_time(runtime, decimals=2):
    """Display runtime in a human friendly format."""
    if runtime < 1:
        return str('mms: ' + str('{:f}'.format(rounder(runtime * 1000, decimals))))
    elif runtime < 60:
        return str('sec: ' + str('{:f}'.format(rounder(runtime, decimals))))
    else:
        return str('min: ' + str('{:f}'.format(rounder(runtime / 60, decimals))))


class Timer:
    def __init__(self, msg=None, decimal_places=2):
        self.msg = msg
        self._decimal_places = decimal_places

        self.start = now()
        self.elapsed_str = None
        self.elapsed_float = None

    def __str__(self):
        return str(self.end)

    def __float__(self):
        return float(self.elapsed_float)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.msg:
            print(self.msg, self.end)
        else:
            print(self.end)

    @property
    def end(self):
        # Calculate run time
        return human_time(now() - self.start, self._decimal_places)

    @staticmethod
    def decorator(func):
        """A function timer decorator."""

        def function_timer(*args, **kwargs):
            """A nested function for timing other functions."""
            # Capture start time
            start = now()

            # Execute function with arguments
            value = func(*args, **kwargs)

            # Calculate run time
            runtime = human_time(now() - start)
            print('{func:50} --> {time}'.format(func=func.__qualname__, time=runtime))
            _TIMES.append((func.__qualname__, runtime))
            return value

        return function_timer

    @staticmethod
    def decorator_noprint(func):
        """A function timer decorator."""

        def function_timer(*args, **kwargs):
            """A nested function for timing other functions."""
            # Capture start time
            start = now()

            # Execute function with arguments
            value = func(*args, **kwargs)

            # Calculate run time
            runtime = human_time(now() - start)
            _TIMES.append((func.__qualname__, runtime))
            return value

        return function_timer

    @property
    def times(self):
        return _TIMES

    @staticmethod
    def print_times(class_name=None):
        for index, ft in enumerate(sorted([(func, t) for func, t in Timer().times
                                           if class_name and func.startswith(class_name)],
                                          key=lambda e: e[1])):
            func, t = ft
            print('{0}.) {1:35} --> {2}'.format(index, func, t))
