import shlex
import subprocess as subp
from subprocess import PIPE
from shutil import which

def sh(argv, encoding='utf-8'):
  proc = subp.Popen(
    argv, stdout=PIPE, stderr=PIPE, shell=True, encoding=encoding)
  try:
    return proc.communicate()
  finally:
    proc.kill()

def shell_path():
  return sh('echo $0')[0].strip()

def whoami():
  return sh('whoami')[0].strip()

shjoin = subp.list2cmdline
