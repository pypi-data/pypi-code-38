from ansible import errors

def map_to_entries(_map,key, value):
    _list = []
    for k in _map:
        _list.append({
            key: k,
            value: _map[k]
        })
    return _list


class FilterModule(object):
    ''' A filter to convert a map into a list of entries'''
    def filters(self):
        return {
            'map_to_entries' : map_to_entries
        }

if __name__ == "__main__":
    print(map_to_entries({
        "key1": "value1",
        "key2": "value2"
        }, "k", "v"))
