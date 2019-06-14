from lura.tmpl.base import Expander
from lura.io import dump

class StrFormat(Expander):
  'Expand templates using str.format().'

  def __init__(self):
    super().__init__()

  def expands(self, env, tmpl):
    '''
    Expand a template.

    :param dict env: expansion environment
    :param str tmpl: template text
    :returns: The expanded template.
    :rtype: str
    '''
    return tmpl.format(**env)

  def expandf(self, env, tmpl, dst):
    '''
    Expand a template to a file.

    :param str env: expansion environment
    :param str tmpl: template text
    :param str dst: destination file path
    :returns: True if dst file was written
    :rtype bool:
    '''
    dump(dst, tmpl.format(**env))

strformat = StrFormat()
