from .pluck import pluck


__all__ = [
  'Pluckable',
  'PluckableList',
  'PluckableDict',
  'PluckableSet',
  'PluckableTuple',
]


class Pluckable():
    def pluck(self, handle):
        return pluck(self, handle)


class PluckableList(list, Pluckable): pass
class PluckableDict(dict, Pluckable): pass
class PluckableSet(set, Pluckable): pass
class PluckableTuple(tuple, Pluckable): pass
