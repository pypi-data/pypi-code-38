from abc import abstractmethod

class BoundExpander:
  'Bind an expander to an environment.'

  def __init__(self, expander, env):
    super().__init__()
    self.expander = expander
    self.env = env

  def expands(self, tmpl):
    return self.expander.expands(self.env, tmpl)

  def expandf(self, tmpl, dst):
    return self.expander.expandf(self.env, tmpl, dst)

  def expandfs(self, src):
    return self.expander.expandfs(self.env, src)

  def expandff(self, src, dst):
    return self.expander.expandff(self.env, src, dst)

class Expander:

  def __init__(self, *args, **kwargs):
    super().__init__()

  def bind(self, env):
    return BoundExpander(self, env)

  @abstractmethod
  def expands(self, env, tmpl):
    '''
    Expand a template.

    :param dict env: expansion environment
    :param str tmpl: template text
    :returns: The expanded template.
    :rtype: str
    '''
    pass

  @abstractmethod
  def expandf(self, env, tmpl, dst):
    '''
    Expand a template to a file.

    :param str env: expansion environment
    :param str tmpl: template text
    :param str dst: destination file path
    :returns: True if dst file was written
    :rtype bool:
    '''
    pass

  @abstractmethod
  def expandfs(self, env, src):
    '''
    Expand a template file to a string.

    :param dict env: expansion environment
    :param str src: template file path
    :returns: The expanded template.
    :rtype: str
    '''
    pass

  @abstractmethod
  def expandff(self, env, src, dst):
    '''
    Expand a template file to another file.

    :param str env: expansion environment
    :param str src: template source file path
    :param str dst: destination file path
    :returns: True if dst file was written
    :rtype bool:
    '''
    pass
