import click
import os
import sys
import threading
import traceback
from lura import sudo
from lura.crypto import decrypt
from lura.io import mkfifo, slurp, touch
from lura.utils import asbool

@click.group()
def cli():
  pass

@cli.command()
@click.option('-u', '--user', help='Target user.')
@click.option('-g', '--group', help='Target group.')
@click.option('-i', '--login', is_flag=True, help='Run as login shell.')
@click.argument('argv', nargs=-1)
def run(user, group, login, argv):
  timeout = float(os.environ.get('LURA_SUDO_TIMEOUT', '5.0'))
  file = os.environ['LURA_SUDO_FILE']
  key = os.environ['LURA_SUDO_KEY']
  ok = os.environ.get('LURA_SUDO_OK')
  keep = asbool(os.environ.get('LURA_SUDO_KEEP', '0'))
  for _ in (
    'LURA_SUDO_FILE', 'LURA_SUDO_KEY', 'LURA_SUDO_OK', 'LURA_SUDO_KEEP',
    'LURA_SUDO_TIMEOUT',
  ):
    if _ in os.environ:
      del os.environ[_]
  password = decrypt(slurp(file).encode(), key.encode()).decode()
  key = None
  if not keep:
    os.unlink(file)
  file = None
  process = sudo.popen(
    argv,
    stdin = sys.stdin,
    stdout = sys.stdout,
    stderr = sys.stderr,
    become_login = login,
    become_user = user,
    become_group = group,
    become_password = password,
    become_timeout = timeout,
  )
  password = None
  try:
    if ok:
      touch(ok)
    code = process.wait()
    sys.exit(code)
  finally:
    process.kill()

@cli.command()
@click.argument('fifo')
@click.argument('timeout', type=float)
def askpass(fifo, timeout):
  def on_timeout():
    try:
      raise RuntimeError(f'Timed out reading become password from fifo: {fifo}')
    except RuntimeError:
      traceback.print_exc()
    os._exit(1)
  mkfifo(fifo)
  threading.Timer(timeout, on_timeout).start()
  password = slurp(fifo)
  sys.stdout.write(password)
  sys.stdout.flush()
  os._exit(0)

if __name__ == '__main__':
  from lura.sudo.__main__ import cli
  cli()
