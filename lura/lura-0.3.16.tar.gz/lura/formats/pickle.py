import pickle
from lura.attrs import ottr
from lura.formats.base import Format

class Pickle(Format):

  def __init__(self):
    super().__init__()

  def loads(self, data):
    'Load pickle from string ``data``.'

    return pickle.loads(data)

  def loadf(self, src, encoding=None):
    'Load pickle from file ``src``.'

    with open(src, mode='rb', encoding=encoding) as fd:
      return self.loadfd(fd)

  def loadfd(self, fd):
    'Load pickle from file descriptor ``fd``.'

    return pickle.load(fd)

  def dumps(self, data):
    'Return dict ``data`` as pickle.'

    return pickle.dumps(data)

  def dumpf(self, data, dst, encoding=None):
    'Write dict ``data`` as pickle to file ``dst``.'

    with open(dst, mode='wb', encoding=encoding) as fd:
      self.dumpfd(data, fd)

  def dumpfd(self, data, fd):
    'Write dict ``data`` as pickle to file descriptor ``fd``.'

    pickle.dump(data, fd)
    if hasattr(fd, 'flush') and callable(fd.flush):
      fd.flush()
