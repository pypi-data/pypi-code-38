import shlex
import subprocess as subp
from subprocess import PIPE

def sh(argv):
  proc = subp.Popen(argv, stdout=PIPE, stderr=PIPE, shell=True, text=True)
  try:
    return proc.communicate()
  finally:
    proc.kill()

def shell_path():
  return sh('echo $0')[0].strip()

def whoami():
  return sh('whoami')[0].strip()

shjoin = subp.list2cmdline
