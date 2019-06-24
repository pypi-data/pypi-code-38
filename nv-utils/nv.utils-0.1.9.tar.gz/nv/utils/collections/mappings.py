__all__ = ['DictionaryObject']


class DictionaryObject(dict):
    """
    Creates a mew dictionary that exposes its keys as object properties.
    """
    def __init__(self, d=None, *args, **kwargs):
        if d:
            self.update(d)
        super(DictionaryObject, self).__init__(*args, **kwargs)

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError(f"Missing attribute: {name}")

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError(f"Missing attribute: {name}")
