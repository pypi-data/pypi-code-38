""" provides AttributeDict """

from collections import OrderedDict
from hilde.helpers.warnings import warn


class AttributeDict(OrderedDict):
    """ Ordered dictionary with attribute access """

    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        warn(f"Attribute {attr} not in dictionary, return None.", level=1)
        return None

    def to_dict(self):
        """ (recursively) return plain python dictionary """
        rep = {}
        for key, val in self.items():
            if isinstance(val, AttributeDict):
                val = val.to_dict()
            rep.update({key: val})

        return rep

    def as_dict(self):
        """ return plain python dictionary (Fireworks compatibility) """
        return dict(self)
