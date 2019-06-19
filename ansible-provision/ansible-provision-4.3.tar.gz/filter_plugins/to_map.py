
def to_map(_map, key, value):
    ret = {}
    for row in _map:
        ret[row[key].lower()] = row[value]
    return ret


class FilterModule(object):
     def filters(self):
         return {'to_map': to_map}

