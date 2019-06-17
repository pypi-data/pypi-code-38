import os
import stat
from pathlib import Path

def isfifo(path):
  return stat.S_ISFIFO(os.stat(path).st_mode)

def mkfifo(path):
  try:
    os.mkfifo(path)
  except FileExistsError:
    if isfifo(path):
      return
    raise

def dump(path, data, mode='w', encoding=None):
  with open(path, mode=mode, encoding=encoding) as fd:
    fd.write(data)
    fd.flush()

def slurp(path, mode='r', encoding=None):
  with open(path, mode=mode, encoding=encoding) as fd:
    return fd.read()

def touch(path, mode=0o600):
  Path(path).touch(mode=mode)

def fext(path):
  if '.' in path:
    return path.rsplit('.', 1)[1]
  raise ValueError(f'File has no extension: {path}')

def flush(file):
  if hasattr(file, 'flush') and callable(file.flush):
    file.flush()

def _tee(source, targets, cond):
  while cond():
    data = source.read()
    if len(data) == 0:
      break
    for target in targets:
      target.write(data)

def tee(source, targets):
  _tee(source, targets, cond=lambda: True)

def Tee(source, targets, name=None):
  from lura.threads import Thread
  class _Tee(Thread):
    def __init__(self):
      super().__init__(target=self.work, name=name)
      self.start()
    def work(self):
      self.work = True
      _tee(source, targets, cond=lambda: self.work is True)
    def stop(self):
      self.work = False
  thread = _Tee()
  return thread

class LineCallbackWriter:

  def __init__(self):
    super().__init__()
    self.buf = []

  def callback(self, lines):
    for line in lines:
      print(line)

  def write(self, data):
    if '\n' not in data:
      buf.append(data)
      return
    line_end, extra = data.rsplit('\n', 1)
    self.buf.append(line_end)
    lines = ''.join(self.buf).split('\n')
    buf.clear()
    if extra:
      self.buf.append(extra)
    self.callback(lines)

  def writelines(self, lines):
    return self.write(''.join(lines))

class LogWriter(LineCallbackWriter):

  def __init__(self, log, level='DEBUG', tag=None):
    super().__init__()
    self.name = name
    self.log = getattr(log, level.lower())

  def callback(self, lines):
    for line in lines:
      if self.tag:
        line = f'{tag} {line}'
      self.log(line)
