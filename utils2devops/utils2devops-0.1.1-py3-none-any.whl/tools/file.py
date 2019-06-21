#!/usr/bin/env python
from contextlib import contextmanager
from typing import Optional


@contextmanager
def opened_w_error(filename: str, mode: Optional[str] = 'r'):
    """
    Open and or give str error
    :param filename:
    :param mode:
    :return: file, err
    """
    try:
        f = open(filename, mode)
    except IOError as err:
        yield None, err
    else:
        try:
            yield f, None
        finally:
            f.close()
