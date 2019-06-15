# coding=utf8
import sys
import json

from errorbuster.traceback_parser import TracebackParser


def formatError(e):
    exc_type, exc_value, exc_traceback_obj = sys.exc_info()
    error_data = {
        'error_type': str(exc_type),
        'error_message': str(exc_value),
        'traceback': TracebackParser(exc_traceback_obj).parse()
    }
    return 'BUSTER:%s' % json.dumps(error_data)
