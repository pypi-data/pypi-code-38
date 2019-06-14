# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import errno
from six import PY3

__author__ = "Daniel Scheffler"


def makedirs(name, exist_ok=False, **kwargs):
    if PY3:
        os.makedirs(name, exist_ok=exist_ok, **kwargs)
    else:
        try:
            os.makedirs(name)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
