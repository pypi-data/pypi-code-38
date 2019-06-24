import msgpack
from lura.attrs import ottr
from lura.formats.base import Format
from lura.io import dump

class Msgpack(Format):

  def __init__(self):
    super().__init__()

  def loads(self, data):
    'Load msgpack from string ``data``.'

    return msgpack.unpackb(data)

  def loadf(self, src, encoding=None):
    'Load msgpack from file ``src``.'

    with open(src, mode='rb', encoding=encoding) as fd:
      return self.loadfd(fd)

    def loadfd(self, fd):
      'Load msgpack from file descriptor ``fd``.'

      return msgpack.unback(fd)

  def dumps(self, data):
    'Return dict ``data`` as msgpack.'

    return msgpack.packb(data)

  def dumpf(self,data, dst, encoding=None):
    'Write dict ``data`` as msgpack to file ``dst``.'

    with open(dst, mode='wb', encoding=encoding) as fd:
      self.dumpfd(fd, data)

  def dumpfd(self, data, fd):
    'Write dict ``data`` as msgpack to file descriptor ``fd``.'

    msgpack.pack(data, fd)
    if hasattr(fd, 'flush') and callable(fd.flush):
      fd.flush()
