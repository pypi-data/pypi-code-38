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
