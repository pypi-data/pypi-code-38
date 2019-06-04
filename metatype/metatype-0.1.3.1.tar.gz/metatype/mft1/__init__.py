KEYMAP = {
    '_id': '-',
    '_type': '*',
    '_auth': '+',
    '_intent': '^',
    '_drive': '@',
}

class Dict(dict):

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

        for key in KEYMAP:
            if KEYMAP[key] is not None:
                setattr(self, key, self.get(KEYMAP[key]))
