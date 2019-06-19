from ansible import errors

import re

def jsonpath(obj, expr):
    try:
        from jsonpath_rw import jsonpath, parse
    except:
        raise ModuleNotFoundError("Install jsonpath_rw using pip install jsonpath_rw first")
    return  parse(expr).find(obj)

class FilterModule(object):
    ''' A filter to transform data structures using jsonpath'''
    def filters(self):
        return {
            'jsonpath' : jsonpath
        }