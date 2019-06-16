import os
import sys
import subprocess as subp
import time
import threading
from lura import logs
from lura.io import dump, mkfifo, slurp
from lura.shell import shell_path, shjoin
from tempfile import TemporaryDirectory

class TimeoutExpired(RuntimeError):

  def __init__(self, sudo):
    self.sudo_argv = shjoin(sudo._sudo_argv())
    self.askpass_argv = sudo._askpass_argv()
    msg = f'Timed out waiting for sudo: {self.sudo_argv}'
    super().__init__(msg)

class Sudo:

  log = logs.get_logger('lura.sudo.Sudo')
  shell = shell_path()

  TimeoutExpired = TimeoutExpired

  def __init__(self):
    self.tls = threading.local()

  def _command_argv(self):
    self.log.noise('Sudo._command_argv()')
    argv = [shjoin(['touch', self.tls.ok_path]), '&&']
    if isinstance(self.tls.argv, str):
      argv.append(self.tls.argv)
    else:
      argv.append(shjoin(self.tls.argv))
    return ' '.join(argv)

  def _sudo_argv(self):
    self.log.noise('Sudo._sudo_argv()')
    tls = self.tls
    sudo_argv = ['sudo', '-A']
    if tls.user is not None:
      sudo_argv += ['-u', tls.user]
    if tls.group is not None:
      sudo_argv += ['-g', tls.group]
    if tls.login:
      sudo_argv.append('-i')
    sudo_argv += [self.shell, '-c', self._command_argv()]
    return sudo_argv

  def _askpass_argv(self):
    self.log.noise('Sudo._askpass_argv()')
    return shjoin([
      sys.executable,
      '-m',
      'lura.sudo', # FIXME
      'askpass',
      self.tls.fifo_path,
      str(float(self.tls.timeout)),
    ])

  def _check_ok(self):
   return os.path.isfile(self.tls.ok_path)

  def _make_fifo(self):
    self.log.noise('Sudo._make_fifo()')
    mkfifo(self.tls.fifo_path)

  def _open_fifo(self):
    tls = self.tls
    try:
      tls.fifo = os.open(tls.fifo_path, os.O_NONBLOCK | os.O_WRONLY)
      return True
    except OSError:
      return False

  def _write_fifo(self, timeout):
    self.log.noise('Sudo._write_fifo()')
    tls = self.tls
    fifo = tls.fifo
    sleep_interval = tls.sleep_interval
    password = tls.password.encode()
    i = 0
    end = len(password)
    start = time.time()
    elapsed = lambda: time.time() - start
    while True:
      try:
        n = os.write(fifo, password[i:])
        self.log.noise(f'Sudo._write_fifo() wrote {n} bytes')
        i += n
        if i == end:
          self.log.noise(f'Sudo._write_fifo() write complete')
          return
      except BlockingIOError:
        pass
      if self._check_ok():
        self.log.noise(f'Sudo._write_fifo() check ok')
        return
      if timeout < elapsed():
        self.log.noise(f'Sudo._write_fifo() timeout expired')
        raise TimeoutExpired(self)
      time.sleep(sleep_interval)

  def _close_fifo(self):
    self.log.noise('Sudo._close_fifo()')
    try:
      os.close(self.tls.fifo)
    except Exception:
      self.log.exception('Error while closing pipe (write) to sudo askpass')
    self.tls.fifo = None

  def _wait_for_sudo(self):
    self.log.noise('Sudo._wait_for_sudo()')
    tls = self.tls
    timeout = tls.timeout
    sleep_interval = tls.sleep_interval
    ok_path = tls.ok_path
    start = time.time()
    elapsed = lambda: time.time() - start
    self.log.noise('Sudo._wait_for_sudo() begin fifo')
    while True:
      if self._open_fifo():
        try:
          self._write_fifo(timeout - elapsed())
          break
        finally:
          self._close_fifo()
      if self._check_ok():
        self.log.noise('Sudo._wait_for_sudo() check ok 1')
        return
      if timeout < elapsed():
        self.log.noise(f'_wait_for_sudo() timeout expired 1')
        raise TimeoutExpired(self)
      time.sleep(sleep_interval)
    self.log.noise('Sudo._wait_for_sudo() end fifo')
    self.log.noise('Sudo._wait_for_sudo() await ok')
    while not self._check_ok():
      if timeout < elapsed():
        self.log.noise(f'_wait_for_sudo() timeout expired 2')
        raise TimeoutExpired(self)
      time.sleep(sleep_interval)
    self.log.noise('Sudo._wait_for_sudo() check ok 2')

  def _make_askpass(self):
    self.log.noise('Sudo._make_askpass()')
    contents = f'#!{self.shell}\nexec {self._askpass_argv()}\n'
    dump(self.tls.askpass_path, contents)
    os.chmod(self.tls.askpass_path, 0o700)

  def _reset(self):
    self.log.noise('Sudo._reset()')
    tls = self.tls
    try:
      tls.state_dir_context.__exit__(None, None, None)
    except Exception:
      self.log.exception('Exception while deleting state directory')
    for _ in list(tls.__dict__.keys()):
      delattr(tls, _)

  def _popen(self):
    self.log.noise('Sudo._popen()')
    tls = self.tls
    self._make_fifo()
    self._make_askpass()
    tls.env['SUDO_ASKPASS'] = tls.askpass_path
    proc = subp.Popen(
      self._sudo_argv(), env=tls.env, cwd=tls.cwd, stdin=tls.stdin,
      stdout=tls.stdout, stderr=tls.stderr, encoding=tls.encoding,
      text=tls.text)
    try:
      self._wait_for_sudo()
    except Exception:
      proc.kill()
      raise
    return proc

  def popen(
    self,
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
      self.log.noise('Sudo.popen()')
      tls = self.tls
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
      return self._popen()
    finally:
      self._reset()

popen = Sudo().popen
Popen = popen
