
def sub_map(map, prefix):
    ret = {}
    for key in map:
      if key.startswith(prefix):
        ret[key[len(prefix):]] = map[key]
    return ret


class FilterModule(object):
     def filters(self):
         """ Returns a new map/dict with only entries matching a prefix, and withthe prefix removed """
         return {'sub_map': sub_map}

if __name__ == "__main__":
    assert(sub_map({
        "elb.check": "/health",
        "elb.port": "100",
        "don.t": "match"
      }, "elb.") == {"check": "/health", "port": "100"})
