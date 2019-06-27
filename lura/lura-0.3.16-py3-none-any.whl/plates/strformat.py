from lura.plates.base import Expander

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

  def expandf(self, env, tmpl, dst, encoding=None):
    '''
    Expand a template to a file.

    :param str env: expansion environment
    :param str tmpl: template text
    :param str dst: destination file path
    :returns: True if dst file was written
    :rtype bool:
    '''
    with open(dst, 'w', encoding=encoding) as fd:
      fd.write(tmpl.format(**env))

strformat = StrFormat()
