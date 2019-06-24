import os
import sys
from abc import abstractmethod
from lura.hash import hashs
from lura.utils import merge

class Format:
  'Serialize or deserialize data.'

  def __init__(self, *args, **kwargs):
    super().__init__()

  @abstractmethod
  def loads(self, data):
    pass

  @abstractmethod
  def loadf(self, src, encoding=None):
    pass

  @abstractmethod
  def loadfd(self, fd):
    pass

  @abstractmethod
  def dumps(self, data):
    pass

  @abstractmethod
  def dumpf(self, data, dst, encoding=None):
    pass

  @abstractmethod
  def dumpfd(self, data, fd):
    pass

  def mergef(self, path, patch, encoding=None):
    '''
    Merge data into an existing file.

    :param dict patch: data to merge
    :param str path: path to file containing data to load and merge with patch

    1. Read ``path`` file contents into data dict
    2. Merge ``patch`` into data dict
    3. Write write merged data dict back to ``path``, if needed

    If ``path`` doesn't exist, then ``patch`` is dumped to ``path``.
    '''
    if not os.path.isfile(path):
      return self.dumpf(patch, path, encoding=encoding)
    data = self.loadf(path)
    data_hash = hashs(self.dumps(data))
    merged = merge(data, patch)
    merged_str = self.dumps(merged)
    merged_hash = hashs(merged_str)
    if data_hash == merged_hash:
      return False
    with open(path, 'w', encoding=encoding) as fd:
      write(merged_str)

  def mergeff(self, path, patch, encoding=None):
    'Merge data from file patch into data at file path.'

    return self.mergef(self.loads(patch), path, encoding=encoding)

  def print(self, data, *args, **kwargs):
    print(self.dumps(data).rstrip(), *args, **kwargs)
