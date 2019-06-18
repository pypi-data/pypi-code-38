import os
import sys
import subprocess as subp
import threading
from lura import logs
from lura.io import dump, mkfifo, slurp
from lura.shell import shell_path, shjoin
from lura.time import Timer
from tempfile import TemporaryDirectory
from time import sleep

log = logs.get_logger('lura.sudo')
shell = shell_path()
tls = threading.local()

class TimeoutExpired(RuntimeError):

  def __init__(self, sudo):
    self.sudo_argv = shjoin(sudo._sudo_argv())
    self.askpass_argv = sudo._askpass_argv()
    msg = f'Timed out waiting for sudo: {self.sudo_argv}'
    super().__init__(msg)

def _command_argv():
  log.noise('_command_argv()')
  argv = [shjoin(['touch', tls.ok_path]), '&&']
  if not tls.shell:
    argv.append('exec')
  if isinstance(tls.argv, str):
    argv.append(tls.argv)
  else:
    argv.append(shjoin(tls.argv))
  return ' '.join(argv)

def _sudo_argv():
  log.noise('_sudo_argv()')
  sudo_argv = ['sudo', '-A']
  if tls.user is not None:
    sudo_argv += ['-u', tls.user]
  if tls.group is not None:
    sudo_argv += ['-g', tls.group]
  if tls.login:
    sudo_argv.append('-i')
  sudo_argv += [shell, '-c', _command_argv()]
  return sudo_argv

def _askpass_argv():
  log.noise('_askpass_argv()')
  return shjoin([
    sys.executable,
    '-m',
    'lura.sudo', # FIXME
    'askpass',
    tls.fifo_path,
    str(float(tls.timeout)),
  ])

def _check_ok():
 return os.path.isfile(tls.ok_path)

def _make_fifo():
  log.noise('_make_fifo()')
  mkfifo(tls.fifo_path)

def _open_fifo():
  log.noise('_open_fifo()')
  try:
    tls.fifo = os.open(tls.fifo_path, os.O_NONBLOCK | os.O_WRONLY)
    return True
  except OSError:
    return False

def _write_fifo(timeout):
  log.noise('_write_fifo()')
  password = tls.password.encode()
  pos = 0
  end = len(password)
  timer = Timer(start=True)
  while True:
    try:
      n = os.write(tls.fifo, password[pos:])
      log.noise(f'_write_fifo() wrote {n} bytes')
      pos += n
      if pos == end:
        log.noise(f'_write_fifo() write complete')
        return
    except BlockingIOError:
      pass
    if _check_ok():
      log.noise(f'_write_fifo() check ok')
      return
    if tls.timeout < timer.time:
      log.noise(f'_write_fifo() timeout {timeout}s expired')
      raise TimeoutExpired()
    log.noise(f'_write_fifo() sleeps for {tls.sleep_interval}s')
    sleep(tls.sleep_interval)

def _close_fifo():
  log.noise('_close_fifo()')
  try:
    os.close(tls.fifo)
  except Exception:
    log.exception('Error while closing pipe to sudo askpass')
  tls.fifo = None

def _wait_for_sudo():
  log.noise('_wait_for_sudo()')
  timer = Timer(start=True)
  log.noise('_wait_for_sudo() fifo begin')
  while True:
    if _open_fifo():
      try:
        _write_fifo(tls.timeout - timer.time)
        break
      finally:
        _close_fifo()
    if _check_ok():
      log.noise('_wait_for_sudo() check ok 1')
      return
    if tls.timeout < timer.time:
      log.noise(f'_wait_for_sudo() timeout {timeout}s expired 1')
      raise TimeoutExpired()
    log.noise(f'_wait_for_sudo() sleeps for {tls.sleep_interval}s 1')
    sleep(tls.sleep_interval)
  log.noise('_wait_for_sudo() fifo end')
  log.noise('_wait_for_sudo() await ok')
  while not _check_ok():
    if tls.timeout < timer.time:
      log.noise(f'_wait_for_sudo() timeout {timeout}s expired 2')
      raise TimeoutExpired()
    log.noise(f'_wait_for_sudo() sleeps for {tls.sleep_interval}s 2')
    sleep(tls.sleep_interval)
  log.noise('_wait_for_sudo() check ok 2')

def _make_askpass():
  log.noise('_make_askpass()')
  contents = f'#!{shell}\nexec {_askpass_argv()}\n'
  dump(tls.askpass_path, contents)
  os.chmod(tls.askpass_path, 0o700)

def _reset():
  log.noise('_reset()')
  try:
    tls.state_dir_context.__exit__(None, None, None)
  except Exception:
    log.exception('Exception while deleting state directory')
  tls.__dict__.clear()

def _popen():
  log.noise('_popen()')
  _make_fifo()
  _make_askpass()
  tls.env['SUDO_ASKPASS'] = tls.askpass_path
  proc = subp.Popen(
    _sudo_argv(), env=tls.env, cwd=tls.cwd, stdin=tls.stdin,
    stdout=tls.stdout, stderr=tls.stderr, encoding=tls.encoding,
    text=tls.text)
  try:
    _wait_for_sudo()
  except Exception:
    proc.kill()
    raise
  return proc

def popen(
  argv,
  env = None,
  cwd = None,
  shell = None,
  stdin = None,
  stdout = None,
  stderr = None,
  encoding = None,
  text = None,
  sudo_user = None,
  sudo_group = None,
  sudo_login = None,
  sudo_password = None,
  sudo_timeout = None,
):
  try:
    log.noise('popen()')
    tls.state_dir_context = TemporaryDirectory()
    tls.state_dir = tls.state_dir_context.__enter__()
    tls.argv = argv
    tls.env = {} if env is None else env
    tls.cwd = cwd
    tls.shell = False if shell is None else shell
    tls.stdin = stdin
    tls.stdout = stdout
    tls.stderr = stderr
    tls.encoding = encoding
    tls.text = text
    tls.user = sudo_user
    tls.group = sudo_group
    tls.login = sudo_login
    tls.password = sudo_password
    tls.timeout = 5 if sudo_timeout is None else sudo_timeout
    tls.sleep_interval = 0.1
    tls.askpass_path = os.path.join(tls.state_dir, 'sudo_askpass')
    tls.fifo_path = os.path.join(tls.state_dir, 'sudo_askpass_pipe')
    tls.ok_path = os.path.join(tls.state_dir, 'sudo_ok')
    tls.sudo_ok = False
    tls.fifo = None
    return _popen()
  finally:
    _reset()

Popen = popen
