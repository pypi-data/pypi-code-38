import time
import functools
from collections import abc


def retry(func):
    @functools.wraps(func)
    def wrapper(self, url, **kwargs):
        if isinstance(self.RETRY_INTERVAL_SECONDS, abc.Iterable):
            for i, sec in enumerate(self.RETRY_INTERVAL_SECONDS):
                try:
                    r = func(self, url, **kwargs)
                except Exception as e:
                    print('exception', e)
                    err = f"Request {url} Failed, retry after {sec}sec(trys: {i+1})"
                    print(err)
                    time.sleep(sec)
                else:
                    return r
            else:
                raise Exception(f'Request {url} Failed!')
        else:
            r = func(self, *args, **kwargs)
        return r
    return wrapper
