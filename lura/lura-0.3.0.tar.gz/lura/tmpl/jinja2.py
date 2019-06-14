import jinja2 as jinja2_
import os
from lura.tmpl.base import Expander
from lura.io import dump

class Jinja2(Expander):
  '''
  Expand templates using Jinja2.

  The following extensions are enabled:

  - jinja2.ext.do
  - jinja2.ext.loopcontrols

  The following environment settings are used:

  - trim_blocks
  - lstrip_blocks
  - FileSystemLoader for cwd
  '''

  extensions = [
    'jinja2.ext.do',
    'jinja2.ext.loopcontrols',
  ]

  def __init__(self, cwd=None):
    super().__init__()
    cwd = os.getcwd() if cwd is None else cwd
    self.engine = jinja2_.Environment(
      trim_blocks=True,
      lstrip_blocks=True,
      loader=jinja2_.FileSystemLoader(cwd),
      extensions=self.extensions,
    )

  def expands(self, env, tmpl):
    '''
    Expand a template.

    :param dict env: expansion environment
    :param str tmpl: template text
    :returns: The expanded template.
    :rtype: str
    '''
    return self.engine.from_string(tmpl).render(env)

  def expandf(self, env, tmpl, dst):
    '''
    Expand a template to a file.

    :param str env: expansion environment
    :param str tmpl: template text
    :param str dst: destination file path
    :returns: True if dst file was written
    :rtype bool:
    '''
    dump(dst, self.engine.from_string(tmpl).render(env))

jinja2 = Jinja2()
