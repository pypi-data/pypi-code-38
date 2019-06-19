# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)

import errno, logging, os, shutil
import zc.buildout

logger = logging.getLogger(__name__)

def generatePassword(length=8):
  from random import SystemRandom
  from string import ascii_lowercase
  return ''.join(SystemRandom().sample(ascii_lowercase, length))

def rmtree(path):
  try:
    os.remove(path)
  except OSError as e:
    if e.errno != errno.EISDIR:
      raise
    shutil.rmtree(path)

class EnvironMixin:

  def __init__(self, allow_none=True):
    environment = self.options.get('environment', '').strip()
    if environment:
      from os import environ
      if '=' in environment:
        self._environ = env = {}
        for line in environment.splitlines():
          line = line.strip()
          if line:
            try:
              k, v = line.split('=', 1)
            except ValueError:
              raise zc.buildout.UserError('Line %r in environment is incorrect' %
                line)
            k = k.strip()
            if k in env:
              raise zc.buildout.UserError('Key %r is repeated' % k)
            env[k] = v.strip() % environ
      else:
        self._environ = dict((k, v.strip() % environ)
          for k, v in self.buildout[environment].items())
    else:
      self._environ = None if allow_none else {}

  @property
  def environ(self):
    if self._environ is not None:
      from os import environ
      env = self._environ.copy()
      for k, v in env.items():
        logger.info(
          'Environment %r set to %r' if k in environ else
          'Environment %r added with %r', k, v)
      for kw in environ.items():
        env.setdefault(*kw)
      return env
