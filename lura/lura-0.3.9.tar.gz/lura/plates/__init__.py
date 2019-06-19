from .fstring import FString
from .fstring import fstring
from .jinja2 import Jinja2
from .jinja2 import jinja2
from .strformat import StrFormat
from .strformat import strformat
from .stringtemplate import StringTemplate
from .stringtemplate import stringtemplate

from lura.attrs import attr

engines = attr(
  j2 = jinja2,
  jinja2 = jinja2,

  tmpl = stringtemplate,
  template = stringtemplate,
  stringtemplate = stringtemplate,

  fstr = fstring,
  fstring = fstring,

  fmt = strformat,
  format = strformat,
  strformat = strformat,
)

del attr
