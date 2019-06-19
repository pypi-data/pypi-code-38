from ansible import errors

import sys

def debug_obj(obj):
    sys.stderr.write(str(obj) + "\n")
    return ''

class FilterModule(object):

    def filters(self):
        return {
            'debug_obj' : debug_obj
        }