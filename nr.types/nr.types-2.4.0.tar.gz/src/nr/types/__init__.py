
__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
__version__ = '2.4.0'


class NotSetType(object):

  def __new__(self):
    global NotSet
    if NotSet is not None:
      return NotSet
    NotSet = object.__new__(self)
    return NotSet

  def __repr__(self):
    return 'NotSet'

  def __bool__(self):
    return False

  def __nonzero__(self):
    return False


NotSet = None
NotSet = NotSetType()
