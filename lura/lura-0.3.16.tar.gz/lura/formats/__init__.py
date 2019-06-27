from .json import Json
from .pickle import Pickle
from .yaml import Yaml
from .csv import Csv

json = Json()
pickle = Pickle()
yaml = Yaml()
csv = Csv()

from lura.attrs import attr

ext = attr(
  csv = csv,
  jsn = json,
  json = json,
  pickle = pickle,
  pckl = pickle,
  yaml = yaml,
  yml = yaml,
)

del attr

def loadf(src, encoding=None):
  from lura.io import fext
  format = fext(src).lower()
  if format in formats:
    return formats[format].loadf(src, encoding=encoding)
  msg = "Unsupported extension '.{}' for '{}'; supported: {}"
  raise ValueError(msg.format(format, src, formats))

def dumpf(dst, data, encoding=None):
  from lura.io import fext
  format = fext(dst).lower()
  if format in formats:
    return formats[format].dumpf(dst, data, encoding=encoding)
  msg = "Unsupported extension '.{}' for '{}', supported formats: {}"
  raise ValueError(msg.format(format, src, formats))
