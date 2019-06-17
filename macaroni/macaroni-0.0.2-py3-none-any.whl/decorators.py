from functools import wraps

from .consts import ERROR_TYPE, EXCEPTION_TYPE, FUNC_TYPE, IGNORE_TYPE
from .types import Error


def ignore(func):
    func._type = IGNORE_TYPE
    return func


def functional(func):
    @wraps(func)
    def runner(self, *args, **kwargs):
        if not self._magic:
            return func(self, *args, **kwargs)

        if self.error:
            return self
        if self.exception:
            return self

        try:
            resp = func(self, self.data, *args, **kwargs)
            if isinstance(resp, Error):
                self.error = resp
            else:
                self.data = resp
        except Exception as exc:
            self.exception = exc

        return self

    runner._type = FUNC_TYPE
    return runner


def error(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self._magic:
            resp = func(self, *args, **kwargs)
            if isinstance(resp, Error):
                self.error = resp.data
                return self.error

        if not self.error:
            return self

        resp = func(self, self.error, self.data, *args, **kwargs)
        if isinstance(resp, Error):
            self.error = resp.data
            return self

        if resp is not None:
            self.data = resp

        self.error = None
        return self

    wrapper._type = ERROR_TYPE
    return wrapper


def exception(exc_cls):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self._magic:
                resp = func(self, *args, **kwargs)
                if isinstance(resp, Error):
                    self.error = resp.data
                    return self.error
            if not self.exception:
                return self
            if not isinstance(self.exception, exc_cls):
                return self

            resp = func(self, self.exception, self.data, *args, **kwargs)
            if isinstance(resp, Exception):
                self.exception = resp
                return self

            if isinstance(resp, Error):
                self.error = resp.data
            elif resp is not None:
                self.data = resp

            self.exception = None
            return self

        wrapper._type = EXCEPTION_TYPE
        return wrapper

    return decorator
