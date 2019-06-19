from ansible import errors

import re

def nested_element(object, path):

    obj = object
    for part in re.split("\\.|/", path):
        if part == "":
            continue
        if part not in obj:
            raise KeyError("Missing key %s in %s" % (part, obj))
        obj = obj[part]

    return obj

class FilterModule(object):
    '''Returns an nested element from an object tree by path (seperated by / or .)'''
    def filters(self):
        return {
            'nested_element' : nested_element
        }