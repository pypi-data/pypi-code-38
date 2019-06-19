import atexit
import os
import subprocess

SLAPRUNNER_PROCESS_LIST = []

class Popen(subprocess.Popen):
  """
  Extension of Popen to launch and kill processes in a clean way
  """
  def __init__(self, *args, **kwargs):
    """
    Launch process and add object to process list for handler
    """
    self.name = kwargs.pop('name', None)
    kwargs['stdin'] = subprocess.PIPE
    kwargs['stderr'] = subprocess.STDOUT
    kwargs.setdefault('stdout', subprocess.PIPE)
    kwargs.setdefault('close_fds', True)
    subprocess.Popen.__init__(self, *args, **kwargs)
    global SLAPRUNNER_PROCESS_LIST
    SLAPRUNNER_PROCESS_LIST.append(self)
    self.stdin.flush()
    self.stdin.close()
    self.stdin = None

def isRunning(name):
  """
  Return True if a process with this name is running
  """
  for process in SLAPRUNNER_PROCESS_LIST:
    if process.name == name:
      if process.poll() is None:
        return True
  return False


def killRunningProcess(name, recursive=False):
  """
  Kill all processes with a given name
  """
  for process in SLAPRUNNER_PROCESS_LIST:
    if process.name == name:
      process.kill(recursive=recursive)


sigterm_handled = False
def handler(*args, **kwargs):
  """
  Signal handler to kill all processes
  """
  global sigterm_handled
  if sigterm_handled:
    return
  sigterm_handled = True

  for process in SLAPRUNNER_PROCESS_LIST:
    try:
      process.kill()
    except OSError:
      pass


def setHandler(sig_list=None):
  atexit.register(handler)


def isPidFileProcessRunning(pidfile):
  """
  Test if the pidfile exist and if the process is still active
  """
  if os.path.exists(pidfile):
    try:
      pid = int(open(pidfile, 'r').readline())
    except ValueError:
      pid = None
    # XXX This could use psutil library.
    if pid and os.path.exists("/proc/%s" % pid):
      return True
    return False
