# Created by Q-ays.
# whosqays@gmail.com

from functools import wraps
from wisdoms.commons import revert, codes


def wrapper(f):
    @wraps(f)
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return revert(codes.ERROR, e)
