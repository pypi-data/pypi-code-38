

def cached_property(func):
    attr_name = '__cached_property_' + func.__name__

    @property
    def _cached_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, func(self))
        return getattr(self, attr_name)

    return _cached_property
