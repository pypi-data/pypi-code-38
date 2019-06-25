class OpenStruct(object):
    def __init__(self, adict={}):
        self.update_with(adict)

    def update_with(self, adict):
        self.__dict__.update(adict)

    def __getattr__(self, name):
        return self.__dict__.get(name)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, val):
        return setattr(self, key, val)

    def __iter__(self):
        return self.__dict__.iteritems()

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return repr(self.__dict__)
