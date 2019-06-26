# -*- coding: utf-8 -*-
"""Locker."""
import fcntl
import os

class LockOperationError(RuntimeError):
  pass

class IsLockedError(RuntimeError):
  pass

class IsNotLockedError(RuntimeError):
  pass

class UnlockOperationError(RuntimeError):
  pass

class WithLocker(object):
  """Locker with."""
  def __init__(self, locker, unlocker):
    self._locker = locker
    self._unlocker = unlocker
  
  def __enter__(self):
    succ = self._locker()
    if not succ:
      raise LockOperationError("lock failed")
    return succ
  
  def __exit__(self, type, value, traceback):
    succ = self._unlocker()
    if type or value or traceback:
      value = str(value) + ("(unlock succeed)" if succ else "(unlock failed)")
      raise type, value, traceback
    if not succ:
      raise UnlockOperationError("unlock failed")
    return succ


class FileLocker(object):
  """File Locker."""
  def __init__(self, filepath):
    self._filepath = filepath
    self._file = None
  
  def locker(self):
    if self._file:
      raise IsLockedError()
    self._file = open(self._filepath, 'a+')
    fcntl.flock(self._file)
    f.truncate(0)
    f.seek(0)
    f.write(str(os.getpid()))
    f.flush()
    return True
  
  def unlocker(self):
    if not self._file:
      raise IsNotLockedError()
    self._file.close()
    self._file = None




