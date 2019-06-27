import json
from io import StringIO
from lura.attrs import ottr
from lura.formats.base import Format

class Encoder(json.JSONEncoder):
  'Custom json encoder which support sets.'

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def default(self, _):
    if isinstance(_, set):
      return list(_)
    return super().default(_)

class Json(Format):
  '''
  Thin wrapper for json. This class configures the json module to use
  ordered dictionaries for backing dicts, and indented json.
  '''

  def __init__(self):
    super().__init__()
    self.object_pairs_hook = ottr

  def loads(self, data, **kwargs):
    'Load json from string `data`.'

    kwargs.setdefault('object_pairs_hook', self.object_pairs_hook)
    return json.loads(data, **kwargs)

  def loadf(self, src, encoding=None, **kwargs):
    'Load json from file `src`.'

    with open(src, encoding=encoding) as fd:
      return self.loadfd(fd, **kwargs)

  def loadfd(self, fd, **kwargs):
    'Load json from file descriptor `fd`.'

    kwargs.setdefault('object_pairs_hook', self.object_pairs_hook)
    return json.load(fd, **kwargs)

  def dumps(self, data, **kwargs):
    'Return dict `data` as json.'

    kwargs.setdefault('cls', Encoder)
    return json.dumps(data, **kwargs)

  def dumpf(self, data, dst, encoding=None, **kwargs):
    'Write dict `data` as json to file `dst`.'

    with open(dst, 'w', encoding=encoding) as fd:
      self.dumpfd(data, fd, **kwargs)

  def dumpfd(self, data, fd, **kwargs):
    'Write dict `data` as json to file descriptor `fd`.'

    kwargs.setdefault('cls', Encoder)
    json.dump(data, fd, **kwargs)
    if hasattr(fd, 'flush') and callable(fd.flush):
      fd.flush()
