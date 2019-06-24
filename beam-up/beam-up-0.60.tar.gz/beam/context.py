
class Context(object):

    def __init__(self, site):
        self.site = site
        self._d = {}

    def __getitem__(self, item):
        return self._d[item]

    def __setitem__(self, item, value):
        self._d[item] = value

    def __delitem__(self, item):
        del self.d_[item]
