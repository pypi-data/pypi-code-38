import json
from lura.attrs import ottr
from lura.formats.base import Format

class Json(Format):
  '''
  Thin wrapper for json. This class configures the json module to use
  ordered dictionaries for backing dicts, and indented json. This class
  supports dumping sets (as lists).
  '''

  class Encoder(json.JSONEncoder):
    'Custom json encoder which support sets.'

    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)

    def default(self, _):
      if isinstance(_, set):
        return list(_)
      return super().default(_)

  def __init__(self, indent=4, object_pairs_hook=ottr):
    super().__init__()
    self.indent = indent
    self.object_pairs_hook = object_pairs_hook

  def loads(self, data):
    'Load json from string ``data``.'

    return json.loads(data, object_pairs_hook=self.object_pairs_hook)

  def loadf(self, src, encoding=None):
    'Load json from file ``src``.'

    with open(src, encoding=encoding) as fd:
      return json.load(fd, object_pairs_hook=self.object_pairs_hook)

  def loadfd(self, fd):
    'Load json from file descriptor ``fd``.'

    return self.loads(fd.read()) # FIXME

  def dumps(self, data):
    'Return dict ``data`` as json.'

    return json.dumps(data, indent=self.indent, cls=self.Encoder)

  def dumpf(self, dst, data, encoding=None):
    'Write dict ``data`` as json to file ``dst``.'

    data = json.dumps(data, indent=self.indent, cls=self.Encoder)
    with open(dst, 'w', encoding=encoding) as fd:
      fd.write(data)

  def dumpfd(self, fd, data):
    'Write dict ``data`` as json to file descriptor ``fd``.'

    fd.write(self.dumps(data))
    if hasattr(fd, 'flush') and callable(fd.flush):
      fd.flush()
