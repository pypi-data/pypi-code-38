import os
from functools import wraps

import rook


def on_lambda():
    return 'LAMBDA_TASK_ROOT' in os.environ


def serverless_rook(f):

    if on_lambda():
        @wraps(f)
        def handler(*args, **kwargs):
            rook.start(log_file="")

            ret = f(*args, **kwargs)

            rook.flush()
            return ret
    else:
        handler = f

    return handler


def setup_zappa_support():

    if on_lambda():
        try:
            from zappa.middleware import ZappaWSGIMiddleware

            original_handler = ZappaWSGIMiddleware.__call__

            @serverless_rook
            def zappa_hook(self, *args, **kwargs):
                return original_handler(self, *args, **kwargs)

            ZappaWSGIMiddleware.__call__ = zappa_hook

        except ImportError:
            # can happen if its not zappa
            pass
    else:
        pass


try:
    from chalice import Chalice

    class RookoutChalice(Chalice):
        @serverless_rook
        def __call__(self, *args, **kwargs):
            return super(RookoutChalice, self).__call__(*args, **kwargs)


except ImportError:
    pass
