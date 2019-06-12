#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import traceback

def traceback_str():
    exc_info = sys.exc_info()
    return "".join(traceback.format_exception(exc_info[0], exc_info[1], exc_info[2]))

def exception_str():
    exc_info = sys.exc_info()
    return "".join(traceback.format_exception_only(exc_info[0], exc_info[1]))

def error_to_str(e):
    """Tries to convert error message to string, handling unicode errors along the way and logging them"""
    try:
        return str(e)
    except UnicodeError as ue:
        logging.warning("Error converting error %r to str: %s", e, ue)
        try:
            return str(e).encode("UTF-8")
        except UnicodeError as ue2:
            logging.warning("Error converting error %r to unicode: %s", e, ue2)
            return "Error %r, args %r" % (e, e.args)
