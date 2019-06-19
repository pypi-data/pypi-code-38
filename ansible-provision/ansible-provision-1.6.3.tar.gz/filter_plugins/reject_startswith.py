from ansible import errors
import pdb

def reject_startswith(map, prefix):
    val = {}
    for key in map.keys():
        if not key.startswith(prefix):
            val[key] = map[key]
    return val


class FilterModule(object):
    def filters(self):
        return {
            'reject_startswith' : reject_startswith
        }