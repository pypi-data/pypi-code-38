import shlex
import subprocess as subp

def shell_path():
  with subp.Popen('echo $0', shell=True, stdout=subp.PIPE) as process:
    return process.stdout.readline().decode().strip()

def shjoin(argv):
  'Join a list of command-line arguments using ``shlex.quote()``.'

  if isinstance(argv, str):
    raise ValueError("'argv' cannot be a 'str' instance")
  return ' '.join(shlex.quote(a) for a in argv)
