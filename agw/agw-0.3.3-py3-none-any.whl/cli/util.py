import sys
from functools import wraps


def ctrl_exit(func):
    @wraps(func)
    def _ctrl_exit(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print("")
            print("\nexiting...\n")
            sys.exit()

    return _ctrl_exit
