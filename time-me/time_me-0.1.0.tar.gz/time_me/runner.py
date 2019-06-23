from typing import Callable

from abc import ABC, abstractmethod
from functools import update_wrapper


class Runner(ABC):
    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

    @abstractmethod
    def assign_result(self, key, result):
        pass


class FunctionRunner(Runner):
    def __init__(self, func: Callable):
        update_wrapper(self, func)
        self.__func__ = func

    def __call__(self, *args, **kwargs):
        return self.__func__(*args, **kwargs)

    def __str__(self):
        return self.__func__.__name__

    def assign_result(self, key, result):
        if not hasattr(self.__func__, '__results__'):
            self.__func__.__results__ = {}
        self.__func__.__results__[key] = result


def runner(x) -> Runner:
    if callable(x):
        return FunctionRunner(x)
    raise TypeError(x)
