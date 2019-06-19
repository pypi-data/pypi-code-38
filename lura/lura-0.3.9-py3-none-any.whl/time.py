import time
from lura.iter import BufferedIterator, forever

class Timer:

  def __init__(self, start=False):
    super().__init__()
    self.begin = None
    self.end = None
    if start:
      self.start()

  def __enter__(self):
    self.start()
    return self

  def __exit__(self, *exc_info):
    self.stop()

  def start(self):
    self.begin = time.time()
    self.end = None

  def stop(self):
    end = time.time()
    if self.begin is None:
      raise Value('Timer not started')
    self.end = end

  @property
  def started(self):
    return self.start is not None and self.end is None

  @property
  def time(self):
    now = time.time()
    if self.begin is None:
      raise ValueError('Timer not started')
    return (now if self.end is None else self.end) - self.begin

  def format(self, precision=10):
    return f'%0.{precision}f' % self.time

  def print(self, **kwargs):
    print(self.format(), **kwargs)

def poll(test, timeout=-1, retries=-1, pause=0.0):
  '''
  Poll for a condition.

  :param callable test: test returning True for pass and False for fail
  :param float timeout: -1 or return False after this many seconds
  :param int retries: -1 or return False after this many retries
  :param float pause: -1 or number of seconds to wait between retries
  :returns: True if the test succeeded else False
  :rtype bool:
  '''
  timer = Timer(start=True) if timeout >= 0 else None
  tries = BufferedIterator(forever() if retries < 0 else range(-1, retries))
  for _ in tries:
    if test():
      return True
    if timer and timer.time >= timeout:
      break
    if pause > 0 and tries.has_next():
      time.sleep(pause)
  return False
