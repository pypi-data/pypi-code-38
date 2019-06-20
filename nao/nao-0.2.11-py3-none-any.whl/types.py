import warnings
import collections

class naodict(collections.OrderedDict):
    """basic attribute access for ordered dict

    keys that collide with predefined attribute names
    could not be set or accessed in attribute-style

    trying to set a predefined attribute produce `UserWarning`
    """
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        for key in self:
            if hasattr(self, key):
                warnings.warn(f"existing attribute will shadow attribute-style access for {key}")


    def __getattr__(self, key):
        # not called if the attribute present!
        if key in self:
            return self[key]
        return super().__getattr__(key)


    def __setattr__(self, key, value):
        if hasattr(self, key):
            warnings.warn(f"updating existing attribute {key}")
            super().__setattr__(key, value)
        else:
            self[key] = value


    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if hasattr(self, key):
            warnings.warn(f"existing attribute will shadow attribute-style access for {key}")
