import subprocess
import shlex
from .flatten import flatten

def run_shell(cmd, env=None):
  if not isinstance(cmd, list):
    cmd = [cmd]
  cmd = flatten(cmd)
  cmd = ' '.join(cmd)
  cmd = shlex.split(cmd)
  process = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env)
  while True:
      output = process.stdout.readline()
      if output.decode('utf-8').strip() == '' and process.poll() is not None:
        break
      if output:
          output = output.decode('utf-8')
          output = "\n".join(output.splitlines())
          print(output)
  return process