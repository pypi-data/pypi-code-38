"""Common data structure shared across modules.
"""

import abc

import json


class DataObjectBase(object):
  """Base class for data object.
  """
  __metaclass__ = abc.ABCMeta

  def to_json(self):
    """Convert data members to json object.
    """
    return json.loads(json.dumps(self.__dict__))


if __name__ == "__main__":
  eg = DataObjectBase()
  print(eg.__dict__)
