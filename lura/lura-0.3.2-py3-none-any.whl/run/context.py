from collections.abc import Sequence
from lura import fmt, logs
from lura.attrs import attr
from lura.utils import scrub
from .run import run, is_non_str_sequence, log_context

class Context:
  'Base class for run count.'

  log = logs.get_logger('lura.run.Context')

  def __init__(self, autosetvars=None):
    super().__init__()
    self.autosetvars = autosetvars
    self.context = run.context()
    self.previous = attr()
    self.name = type(self).__name__
    self._logcall(f'__init__(autosetvars={autosetvars})')

  def _logcall(self, msg, *args, **kwargs):
    self.log.noise(f'{self.name}.{msg}', *args, **kwargs)

  def set(self, name, value, merge=True):
    'Set a context variable and save its previous value for unset().'

    self._logcall(f'set({name}, merge={merge})')
    assert(name not in self.previous)
    if is_non_str_sequence(value) and merge:
      self.previous[name] = list(self.context.setdefault(name, []))
      self.context[name].extend(value)
    else:
      self.previous[name] = self.context.get(name)
      self.context[name] = value

  def unset(self, name):
    'Restore a context variable to its original value.'

    self._logcall(f'unset({name})')
    value = self.previous[name]
    if value in (None, []):
      del self.context[name]
    elif is_non_str_sequence(value):
      self.context[name].clear()
      self.context[name].extend(value)
    else:
      self.context[name] = value
    del self.previous[name]

  def autoset(self):
    'Automatically assign context variable values from instance attributes.'

    if not self.autosetvars:
      self._logcall('autoset() nothing to set')
      return
    self._logcall('autoset()')
    for name in self.autosetvars:
      merge = True
      if not isinstance(name, str):
        name, merge = name
      self.set(name, getattr(self, name), merge)

  def autounset(self):
    'Restore all previous context variables to their original values.'

    if not self.previous:
      self._logcall('autounset() nothing to autounset')
      return
    self._logcall('autounset()')
    for name in list(self.previous):
      self.unset(name)

  def cleanup(self):
    'Cleanup any lingering values in run.context.'

    self._logcall('cleanup()')
    if not all(_ in (None, []) for _ in self.context.values()):
      self.log.info('run.context is not empty at run.Context cleanup')
      scrubbed = scrub(dict(self.context))
      msg = fmt.yaml.dumps(scrubbed)
      logs.lines(self.log.debug, msg, prefix='  ')
    self.context.clear()

  def push(self):
    'Increment the thread-global context count.'

    self._logcall('push()')
    self.context.count = self.context.setdefault('count', 0) + 1

  def pop(self):
    'Decrement the thread-global context count.'

    self._logcall('pop()')
    self.context.count -= 1
    if self.context.count == 0:
      del self.context['count']
      self.cleanup()

  def __enter__(self):
    self._logcall('__enter__() begins with context:')
    log_context(self.log.noise)
    self.push()
    self.autoset()

  def __exit__(self, *exc_info):
    self._logcall('__exit__()')
    self.autounset()
    self.pop()
    self._logcall('__exit__() returns returns context:')
    log_context(self.log.noise)

class Quash(Context):

  def __init__(self):
    print('hello quash')
    autosetvars = ('enforce',)
    super().__init__(autosetvars)
    self.enforce = False

class Enforce(Context):

  def __init__(self, enforce_code):
    assert(isinstance(enforce_code, int))
    autosetvars = ('enforce_code', 'enforce')
    super().__init__(autosetvars)
    self.enforce_code = enforce_code
    self.enforce = True

class Cwd(Context):

  def __init__(self, cwd):
    print('hello cwd')
    autosetvars = ('cwd',)
    super().__init__(autosetvars)
    self.cwd = cwd

class Stdio(Context):

  def __init__(self, stdout, stderr=[], excl=False):
    autosetvars = [('stdio', not excl)]
    if stderr or excl:
      autosetvars.append(('stderr', not excl))
    super().__init__(autosetvars)
    self.stdout = stdout if isinstance(stdout, Sequence) else (stdout,)
    self.stderr = stderr if isinstance(stderr, Sequence) else (stderr,)

class Log(Stdio):

  def __init__(self, log, level='DEBUG'):
    super().__init__(
      LogWriter(log, level, '[stdout]'), LogWriter(log, level, '[stderr]'))

class Sudo(Context):

  def __init__(
    self, password=None, user=None, group=None, login=None, timeout=None
  ):
    autosetvars = (
      'sudo_user', 'sudo_password', 'sudo_group', 'sudo_login', 'sudo_timeout',
      'mode')
    super().__init__(autosetvars)
    self.sudo_user = user
    self.sudo_password = password
    self.sudo_group = group
    self.sudo_login = login
    self.sudo_timeout = timeout
    self.mode = 'sudo'

class New(Context):

  def __init__(self):
    super().__init__()
    self.old = None

  def __enter__(self):
    super().__enter__()
    filter = ('count',)
    self.old = {k: v for (k, v) in self.context.items() if k not in filter}
    for name in self.old:
      del self.context[name]
    self._logcall('__enter__() new context:')
    log_context(self.log.noise)

  def __exit__(self, *exc_info):
    super().__exit__()
    self.context.update(self.old)
