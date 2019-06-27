import ast
import csv
import os
import sys
from collections.abc import MutableMapping
from io import StringIO
from lura import logs
from lura.attrs import attr, ottr
from lura.formats.base import Format

# FIXME support restkey/restval

log = logs.get_logger(__name__)

class Csv(Format):
  '''
  Serialize or deserialize CSV data with optional type inference on load.

  Dump support is currently not implemented, but will be eventually.

  Load support is implemented by `csv.DictReader`.

  Load-time type inference is implemented by `ast.literal_eval()` and can be
  disabled...

  1. for all fields by passing `infer=False` to the load function.
  2. for a particualr field by passing a type conversion callable for the
     field via `typemap`. (e.g. `lambda _: _` to return the naked value.)
  '''

  def __init__(self):
    super().__init__()

  def loads(
    self, data, infer=True, typemap=None, fieldnames=None, dialect='excel',
    **fmtparams
  ):
    with StringIO(data) as fd:
      return self.loadfd(fd, infer, typemap, fieldnames, dialect, **fmtparams)

  def loadf(
    self, src, encoding=None, infer=True, typemap=None, fieldnames=None,
    dialect='excel', **fmtparams
  ):
    with open(src, 'r', encoding=encoding) as fd:
      return self.loadfd(fd, infer, typemap, fieldnames, dialect, **fmtparams)

  def loadfd(
    self, fd, infer=True, typemap=None, fieldnames=None, dialect='excel',
    **fmtparams
  ):
    msg = 'loadfd({}, infer={}, typemap={}, fieldnames={}, dialect={}'
    log.noise(msg.format(fd, infer, typemap, fieldnames, dialect))
    res = []
    reader = csv.DictReader(fd, fieldnames=fieldnames, dialect=dialect)
    for row in reader:
      for field in row:
        row[field] = self._value(field, row[field], infer, typemap)
      res.append(ottr(row))
    return res

  def dumps(self, data):
    raise NotImplementedError()

  def dumpf(self, data, dst, encoding=None):
    raise NotImplementedError()

  def dumpfd(self, data, fd):
    raise NotImplementedError()

  def _value(self, name, value, infer, typemap):
    if typemap and name in typemap:
      # always use the mapped type if present
      res = typemap[name](value)
      log.noise("_value() typemap: {}: {}('{}') -> {}".format(
        name, typemap[name].__name__, value, res))
      return res
    if not infer:
      # return the naked value if not inferring
      log.noise(f"_value() noinfer: {name}: '{value}'")
      return value
    try:
      # evaluate the value as a literal value
      res = ast.literal_eval(value)
      log.noise("_value() eval: {}: {}('{}') -> {}".format(
        name, res.__class__.__name__, value, res))
      # convert dict to attr for convenience
      if isinstance(res, MutableMapping):
        res = attr(res)
        log.noise(f'_value() {name}: MutableMapping -> attr')
      return res
    except (ValueError, SyntaxError):
      # return the naked value if the value can't be evaluated
      log.noise(f"_value() inferexc: {name}: '{value}'")
      return value
