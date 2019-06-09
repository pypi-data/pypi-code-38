from typing import Any, Callable


def check_input(arg: Any):
    if not (isinstance(arg, int) and arg >= 0):
        raise ValueError('This function domain is zero and positive integers')


def check_input_decorator(function: Callable[[Any], Callable[[Any], Any]]):
    def wrapper(*args: Any):
        _ = [check_input(arg) for arg in args]
        return function(*args)
    return wrapper
