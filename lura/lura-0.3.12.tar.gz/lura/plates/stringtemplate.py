from string import Template
from lura.plates.base import Expander
from lura.io import dump

class StringTemplate(Expander):
  'Expand templates using string.Template().'

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
    return Template(tmpl).substitute(env)

  def expandf(self, env, tmpl, dst, encoding=None):
    '''
    Expand a template to a file. File will be written only when the expanded
    template differs from the existing file's contents, if any.

    :param str env: expansion environment
    :param str tmpl: template text
    :param str dst: destination file path
    :returns: True if dst file was written
    :rtype bool:
    '''
    with open(dst, 'w', encoding=encoding) as fd:
      fd.write(Template(tmpl).substitute(env))

stringtemplate = StringTemplate()
