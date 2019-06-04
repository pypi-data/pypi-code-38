KEYMAP = {
    '_id': '@id',
    '_type': '@type',
    '_auth': None,
    '_intent': None,
    '_drive': None,
}

class Dict(dict):

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

        for key in KEYMAP:
            if KEYMAP[key] is not None:
                setattr(self, key, self.get(KEYMAP[key]))
