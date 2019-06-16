import os
import shlex
import sys
import threading
from collections.abc import Sequence
from getpass import getpass
from io import StringIO
from lura import fmt
from lura import logs
from lura.attrs import attr, ottr, wttr
from lura.io import LogWriter, Tee, flush, tee
from lura.shell import shell_path, shjoin, whoami
from lura.sudo import popen as sudo_popen
from ptyprocess import PtyProcessUnicode
from subprocess import PIPE, Popen as subp_popen

log = logs.get_logger('lura.run')
NONE = object()

class Info:
  'Base class for Error and Result.'

  members = ('args', 'argv', 'code', 'stdout', 'stderr')

  def __init__(self, *args):
    super().__init__()
    if len(args) == 1 and isinstance(args[0], Info):
      for _ in self.members:
        setattr(self, _, getattr(args[0], _))
    elif len(args) == len(self.members):
      for i in range(len(self.members)):
        setattr(self, self.members[i], args[i])
    else:
      msg = f'Invalid arguments, expected {self.members}, got {args}'
      raise ValueError(msg)

  def as_dict(self, type=ottr):
    return type(((name, getattr(self, name)) for name in self.members))

  def format(self, fmt='yaml'):
    from lura.fmt import formats
    tag = 'run.{}'.format(type(self).__name__.lower())
    return formats[fmt].dumps({tag: self.as_dict()})

  def print(self, fmt='yaml', file=None):
    file = sys.stdout if file is None else file
    file.write(self.format(fmt=fmt))
    flush(file)

  def log(self, logger, level='DEBUG', fmt='yaml'):
    log = getattr(logger, level.lower())
    for line in self.format(fmt=fmt).split('\n'):
      log(line)

class Result(Info):
  'Returned by run().'

  def __init__(self, *args):
    super().__init__(*args)

class Error(RuntimeError, Info):
  'Raised by run().'

  def __init__(self, *args):
    Info.__init__(self, *args)
    msg = f'Process exited with code {self.code}: {shjoin(self.argv)})'
    RuntimeError.__init__(self, msg)

def _run_stdio(proc, argv, args, stdout, stderr):
  log.noise('_run_stdio()')
  out, err = StringIO(), StringIO()
  stdout.append(out)
  stderr.append(err)
  try:
    for thread in (Tee(proc.stdout, stdout), Tee(proc.stderr, stderr)):
      thread.join()
    return run.result(args, argv, proc.wait(), out.getvalue(), err.getvalue())
  finally:
    proc.kill()
    out.close()
    err.close()

def _run_popen(argv, args, env, cwd, shell, stdout, stderr, **kwargs):
  log.noise('_run_popen()')
  proc = subp_popen(
    args if shell else argv, env=env, cwd=cwd, shell=shell, stdout=PIPE,
    stderr=PIPE, text=True)
  return _run_stdio(proc, argv, args, stdout, stderr)

def _run_pty(argv, args, env, cwd, shell, stdout, **kwargs):
  log.noise('_run_pty()')
  if shell:
    argv = [run.default_shell, '-c', args]
    args = shjoin(argv)
  proc = PtyProcessUnicode.spawn(argv, env=env, cwd=cwd)
  proc_reader = attr(read=lambda: f'{proc.readline()[:-2]}\n')
  out = StringIO()
  stdout.append(out)
  try:
    try:
      tee(proc_reader, stdout)
    except EOFError:
      pass
    return run.result(args, argv, proc.wait(), out.getvalue(), '')
  finally:
    try:
      proc.kill(9)
    except Exception:
      msg = 'runpty(): unhandled exception while killing pty process'
      log.debug(msg, exc_info=True)
    out.close()

def _run_sudo(
  argv, args, env, cwd, shell, stdout, stderr, sudo_user, sudo_group,
  sudo_password, sudo_login, sudo_timeout, **kwargs
):
  log.noise('_run_sudo()')
  proc = sudo_popen(
    args if shell else argv, env=env, cwd=cwd, shell=shell, stdout=PIPE,
    stderr=PIPE, text=True, sudo_user=sudo_user, sudo_group=sudo_group,
    sudo_password=sudo_password, sudo_login=sudo_login,
    sudo_timeout=sudo_timeout)
  return _run_stdio(proc, argv, args, stdout, stderr)

def lookup(name):
  log.noise(f'lookup({name})')
  default_value = run.defaults[name]
  context_value = run.context().get(name)
  is_str = isinstance(default_value, str)
  is_seq = isinstance(default_value, Sequence)
  if is_seq and not is_str:
    if context_value:
      return list(default_value) + context_value
    return list(default_value)
  elif context_value:
    return context_value
  else:
    return default_value

def merge_args(user_args):
  log.noise(f'merge_args({user_args})')
  stdio = ('stdout', 'stderr')
  for name in run.defaults.keys():
    if name in stdio:
      continue
    if user_args.get(name) is None:
      user_args[name] = lookup(name)
  for name in stdio:
    user_value = user_args.get(name)
    default_value = lookup(name)
    if not user_value:
      user_args[name] = default_value
      continue
    if not isinstance(user_value, Sequence):
      user_value = (user_value,)
    user_args[name] = []
    user_args[name].extend(user_value)
    user_args[name].extend(default_value)
  return attr(user_args)

def run(argv, **kwargs):
  log.noise('run()')
  kwargs = merge_args(kwargs)
  modes = ('popen', 'pty', 'sudo')
  if kwargs.mode not in modes:
    raise ValueError(f"Invalid mode '{kwargs.mode}'. Valid modes: {modes}")
  if isinstance(argv, str):
    args = argv
    argv = shlex.split(args)
  else:
    args = shjoin(argv)
  run_real = globals()[f'_run_{kwargs.mode}']
  result = run_real(argv, args, **kwargs)
  if kwargs.enforce is not None and result.code != kwargs.enforce:
    raise run.error(result)
  return result

class Context:

  def __init__(self):
    super().__init__()

  def __enter__(self):
    log.noise(f'{type(self).__name__}.__enter__()')
    context = run.context()
    context.count = context.setdefault('count', 0) + 1

  def __exit__(self, *exc_info):
    log.noise(f'{type(self).__name__}.__exit__()')
    context = run.context()
    context.count -= 1
    if context.count == 0:
      if not all(_ is None for _ in context.values()):
        log.warn('run.context is not empty at last context exit:')
        if 'become_password' in context:
          context.become_password = '(scrubbed)'
        for line in fmt.yaml.dumps(context).split('\n'):
          log.debug(f'  {line}')
      log.noise('Last context exited, clearing tls')
      del context[:]

class Enforce(Context):

  def __init__(self, code):
    super().__init__()
    self.code = code
    self.previous = NONE

  def __enter__(self):
    super().__enter__()
    context = run.context()
    self.previous = context.get('enforce', NONE)
    context.enforce = self.code

  def __exit__(self, *exc_info):
    context = run.context()
    if self.previous == NONE:
      del context['enforce']
    else:
      run.context = self.previous
    return super().__exit(*exc_info)

class Quash(Enforce):

  def __init__(self):
    super().__init__(None)

class Stdio(Context):

  def __init__(self, stdout, stderr=()):
    super().__init__()
    self.stdout = stdout if isinstance(stdout, Sequence) else (stdout,)
    self.stderr = stderr if isinstance(stderr, Sequence) else (stderr,)

  def __enter__(self):
    super().__enter__()
    context = run.context()
    context.setdefault('stdout', []).extend(self.stdout)
    if self.stderr:
      context.setdefault('stderr', []).extend(self.stderr)

  def __exit__(self, *exc_info):
    context = run.context()
    pairs = [(context.stdout, self.stdout)]
    if self.stderr:
      pairs.append((context.stderr, self.stderr))
    for all, expel in pairs:
      all.reverse()
      for _ in reversed(expel):
        all.remove(_)
      all.reverse()
    return super().__exit__(*exc_info)

class Log(Stdio):

  def __init__(self, log, level='DEBUG'):
    super().__init__(
      LogWriter(log, level, '[stdout]'), LogWriter(log, level, '[stderr]'))

class Sudo:

  def __init__(
    self, password=None, user=None, group=None, login=None, timeout=None
  ):
    super().__init__()
    self.sudo_user = user
    self.sudo_password = password
    self.sudo_group = group
    self.sudo_login = login
    self.sudo_timeout = timeout
    self.mode = 'sudo'
    self.previous = None

  def vars(self, obj):
    return {
      k: obj.get(k)
      for k in self.__dict__.keys()
      if k not in ('previous',)
    }

  def __enter__(self):
    log.noise(f'{type(self).__name__}.__enter__()')
    context = run.context()
    self.previous = self.vars(context)
    context.update(self.vars(self.__dict__))

  def __exit__(self, *exc_info):
    log.noise(f'{type(self).__name__}.__exit__()')
    run.context().update(self.previous)

def getsudopass(prompt=None):
  log.noise('getsudopass()')
  return getpass(getsudopass.prompt if prompt is None else prompt)

getsudopass.prompt = f'[sudo] password for {whoami()}: '

def run_popen(argv, **kwargs):
  log.noise('run_popen()')
  kwargs['mode'] = 'popen'
  return run(argv, **kwargs)

def run_pty(argv, **kwargs):
  log.noise('run_pty()')
  kwargs['mode'] = 'pty'
  return run(argv, **kwargs)

def run_sudo(argv, **kwargs):
  log.noise('run_sudo()')
  kwargs['mode'] = 'sudo'
  return run(argv, **kwargs)

# modes
run.popen = run_popen
run.pty = run_pty
run.sudo = run_sudo

# results
run.result = Result
run.error = Error

# context managers
run.Enforce = Enforce
run.Quash = Quash
run.Stdio = Stdio
run.Log = Log
run.Sudo = Sudo

# misc
run.getsudopass = getsudopass
run.default_shell = shell_path()

# defaults
run.defaults = attr()
run.defaults.mode = 'popen'
run.defaults.env = None
run.defaults.cwd = None
run.defaults.shell = None
run.defaults.stdout = []
run.defaults.stderr = []
run.defaults.sudo_user = None
run.defaults.sudo_group = None
run.defaults.sudo_password = None
run.defaults.sudo_login = None
run.defaults.sudo_timeout = 3
run.defaults.enforce = 0

# context manager variable storage
run.context = lambda: wttr(run.context.tls.__dict__)
run.context.tls = threading.local()
