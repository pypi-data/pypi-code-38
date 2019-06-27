import sys
from enum import Enum
from shutil import rmtree
from tempfile import mkdtemp

import six


class TemporaryDirectory(object):
  def __init__(self, *args, **kwargs):
    self.directory = mkdtemp(*args, **kwargs)

  def __enter__(self):
    return self.directory

  def __exit__(self, *args):
    rmtree(self.directory)

def safe_format(string, *args, **kwargs):
  return six.text_type(string).format(*args, **kwargs)

class Platform(Enum):
  MAC = 1
  LINUX = 2

def current_platform():
  if sys.platform.startswith('linux'):
    return Platform.LINUX
  elif sys.platform == "darwin":
    return Platform.MAC
  else:
    raise Exception(safe_format(
      "You are attempting to run SigOpt Orchestrate on the following platform: {}."
      " Currently, only Mac and Linux are supported.",
      sys.platform
    ))
