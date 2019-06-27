def always(value=None):
  'Return a generator that always returns ``value``.'

  while True:
    yield value

forever = always

class BufferedIterator:
  '''
  Iterator wrapper that buffers next() and provides the methods:

  - has_next()
  - peek(default=None)
  '''

  def __init__(self, it):
    super().__init__()
    self._it = iter(it)
    self._buffered = False
    self._next = None

  def __iter__(self):
    return self

  def __next__(self):
    if self._buffered:
      _ = self._next
      self._next = None
      self._buffered = False
      return _
    else:
      return next(self._it)

  def has_next(self):
    'Return False if there are no more items, else True.'

    if self._buffered:
      return True
    try:
      self._next = next(self._it)
      self._buffered = True
    except StopIteration:
      pass
    return self._buffered

  def peek(self, default=None):
    '''
    Return the next item without advancing the iterator, or default if there
    are no more items.
    '''
    return self._next if self.has_next() else default
