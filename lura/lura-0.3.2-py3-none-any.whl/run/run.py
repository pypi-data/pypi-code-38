import os
import shlex
import sys
import threading
from collections.abc import Sequence
from getpass import getpass
from io import StringIO
from lura import fmt, logs
from lura.attrs import attr, ottr, wttr
from lura.io import LogWriter, Tee, flush, tee
from lura.shell import shell_path, shjoin, whoami
from lura.sudo import popen as sudo_popen
from lura.utils import scrub
from ptyprocess import PtyProcessUnicode
from subprocess import PIPE, Popen as subp_popen

log = logs.get_logger('lura.run')

def is_non_str_sequence(obj):
  return not isinstance(obj, str) and isinstance(obj, Sequence)

def log_context(log):
  scrubbed = scrub(dict(run.context()))
  logs.lines(log, fmt.yaml.dumps(scrubbed), prefix='    ')

class Info:
  'Base class for Error and Result.'

  members = ('cmd', 'argv', 'code', 'stdout', 'stderr')

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
    logs.lines(log, self.format(fmt=fmt))

class Result(Info):
  'Returned by run().'

  def __init__(self, *args):
    super().__init__(*args)

class Error(Exception, Info):
  'Raised by run().'

  def __init__(self, *args):
    Info.__init__(self, *args)
    msg = f'Process exited with code {self.code}: {self.cmd})'
    Exception.__init__(self, msg)

def _run_stdio(proc, cmd, argv, stdout, stderr):
  log.noise('_run_stdio()')
  out, err = StringIO(), StringIO()
  stdout.append(out)
  stderr.append(err)
  try:
    for thread in (Tee(proc.stdout, stdout), Tee(proc.stderr, stderr)):
      thread.join()
    return run.result(cmd, argv, proc.wait(), out.getvalue(), err.getvalue())
  finally:
    proc.kill()
    out.close()
    err.close()

def _run_popen(cmd, argv, env, cwd, shell, stdout, stderr, **kwargs):
  log.noise('_run_popen()')
  proc = subp_popen(
    cmd if shell else argv, env=env, cwd=cwd, shell=shell, stdout=PIPE,
    stderr=PIPE, text=True)
  return _run_stdio(proc, cmd, argv, stdout, stderr)

def _run_pty(cmd, argv, env, cwd, shell, stdout, **kwargs):
  log.noise('_run_pty()')
  if shell:
    argv = [run.default_shell, '-c', cmd]
    cmd = shjoin(argv)
  proc = PtyProcessUnicode.spawn(argv, env=env, cwd=cwd)
  proc_reader = attr(read=lambda: f'{proc.readline()[:-2]}\n')
  out = StringIO()
  stdout.append(out)
  try:
    try:
      tee(proc_reader, stdout)
    except EOFError:
      pass
    return run.result(cmd, argv, proc.wait(), out.getvalue(), '')
  finally:
    try:
      proc.kill(9)
    except Exception:
      log.exception('Unhandled exception when finally killing pty process')
    out.close()

def _run_sudo(
  cmd, argv, env, cwd, shell, stdout, stderr, sudo_user, sudo_group,
  sudo_password, sudo_login, sudo_timeout, **kwargs
):
  log.noise('_run_sudo()')
  proc = sudo_popen(
    cmd if shell else argv, env=env, cwd=cwd, shell=shell, stdout=PIPE,
    stderr=PIPE, text=True, sudo_user=sudo_user, sudo_group=sudo_group,
    sudo_password=sudo_password, sudo_login=sudo_login,
    sudo_timeout=sudo_timeout)
  return _run_stdio(proc, cmd, argv, stdout, stderr)

def lookup(name):
  log.noise(f'lookup({name})')
  default_value = run.defaults[name]
  context_value = run.context().get(name)
  if is_non_str_sequence(default_value):
    if context_value:
      value = []
      value.extend(default_value)
      value.extend(context_value)
      return value
    else:
      return list(default_value)
  elif context_value is not None:
    return context_value
  else:
    return default_value

def merge_args(user_args):
  log.noise(f'merge_args()')
  stdio = ('stdout', 'stderr')
  for name in run.defaults:
    if name in stdio:
      continue
    if user_args.get(name) is None:
      user_args[name] = lookup(name)
  for name in stdio:
    user_value = user_args.get(name)
    default_value = lookup(name)
    if user_value:
      if not isinstance(user_value, Sequence):
        user_value = (user_value,)
      user_args[name] = []
      user_args[name].extend(user_value)
      user_args[name].extend(default_value)
    else:
      user_args[name] = default_value
  return attr(user_args)

def run(argv, **kwargs):
  log.noise('run() begins with context:')
  log_context(log.noise)
  kwargs = merge_args(kwargs)
  modes = ('popen', 'pty', 'sudo')
  if kwargs.mode not in modes:
    raise ValueError(f"Invalid mode '{kwargs.mode}'. Valid modes: {modes}")
  if isinstance(argv, str):
    cmd = argv
    argv = shlex.split(cmd)
  else:
    cmd = shjoin(argv)
  run_real = globals()[f'_run_{kwargs.mode}']
  result = run_real(cmd, argv, **kwargs)
  if kwargs.enforce is True and result.code != kwargs.enforce_code:
    raise run.error(result)
  log.noise('run() returns with context:')
  log_context(log.noise)
  return result

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
run.defaults.enforce_code = 0
run.defaults.enforce = True
run.defaults.sudo_user = None
run.defaults.sudo_group = None
run.defaults.sudo_password = None
run.defaults.sudo_login = None
run.defaults.sudo_timeout = 3

# context manager variable storage
run.context = lambda: wttr(run.context.tls.__dict__)
run.context.tls = threading.local()
