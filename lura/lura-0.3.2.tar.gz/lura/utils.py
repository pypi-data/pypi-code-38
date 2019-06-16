import types
from lura.attrs import attr
from collections import MutableMapping, MutableSequence
from copy import deepcopy
from distutils.util import strtobool

def isexc(o):
  '''
  ``True`` if ``o`` is a tuple as returned by ``sys.exc_info()``, else
  ``False``.
  '''

  return isinstance(o, tuple) and len(o) == 3 and (
    isinstance(o[0], type) and
    isinstance(o[1], o[0]) and
    isinstance(o[2], types.TracebackType)
  )

def asbool(val):
  'Turn something (including strings via ``strtobool``) into a ``bool``.'

  if val == '':
    return False
  return bool(strtobool(val)) if isinstance(val, str) else bool(val)

def remap(src, cls=attr):
  '''
  Recursively convert all MutableMappings found in src to type cls. If
  src is a MutableMapping, then src will also be converted to type cls. This
  is used for mass-converting the mapping type used in a deeply-nested data
  structure, such as converting all dicts to attrs.

  :param [MutableSequence, MutableMapping] src: source collection
  :param type cls: target MutableMapping type
  :returns: a new collection
  :rtype MutableMapping:
  '''
  types = (MutableSequence, MutableMapping)
  if isinstance(src, MutableMapping):
    return cls((
      (k, remap(v, cls)) if isinstance(v, types) else (k, v)
      for (k, v) in src.items()
    ))
  elif isinstance(src, MutableSequence):
    return src.__class__(
      remap(_, cls) if isinstance(_, types) else _
      for _ in src
    )
  else:
    raise ValueError(f'src must be MutableSequence or MutableMapping: {src}')

def merge(a, b):
  'Merge two MutableMappings.'

  assert(isinstance(a, MutableMapping))
  assert(isinstance(b, MutableMapping))
  if not (a or b):
    return type(b)()
  if not a:
    return deepcopy(b)
  if not b:
    return deepcopy(a)
  a = a.copy()
  b = b.copy()
  for k, v in a.items():
    if (
      isinstance(v, MutableMapping) and
      k in b and
      isinstance(b[k], MutableMapping)
    ):
      b[k] = merge(v, b[k])
  a.update(b)
  return a

def import_object(spec):
  mod, type = spec.rsplit('.', 1)
  return getattr(__import__(mod), type)

class ObjectProxy:

  def __init__(self, target):
    super().__init__()
    self._proxied_object = target

  def __getattr__(self, name):
    if hasattr(self._proxied_object, name):
      return getattr(self._proxied_object, name)
    err = f"'{type(self).__name__}' object has no attribute '{k}'"
    raise AttributeError(err)

def scrub(obj, tag='[scrubbed]'):
  from collections.abc import MutableMapping, Sequence
  for name, value in obj.items():
    if isinstance(value, str) and 'pass' in name.lower():
      obj[name] = tag
    elif isinstance(value, bytes) and 'pass' in name.lower():
      obj[name] = tag.encode()
    elif isinstance(value, MutableMapping):
      scrub(value)
    elif isinstance(value, Sequence):
      for item in value:
        if isinstance(value, MutableMapping):
          scrub(value)
  return obj
