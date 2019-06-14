import time
from lura.iter import BufferedIterator, forever

class Timer:
  'Timer object and context manager.'

  def __init__(self, start=False):
    'Create instance.'

    super().__init__()
    self.started = None
    self.stopped = None
    if start:
      self.start()

  def reset(self):
    'Reset timer (even if started).'

    self.started = None
    self.stopped = None

  def __enter__(self):
    if not self.running:
      self.start()
    return self

  def __exit__(self, *exc):
    if self.running:
      self.stop()

  def get_running(self):
    'Return True if this timer is running, else False.'

    return self.started is not None and self.stopped is None

  def get_time(self):
    '''
    - If the timer has never been started, return 0.0.
    - If the timer is running, return the number of seconds since the timer was
      started.
    - If the timer is stopped, return the number of seconds the timer had been
      started before stopping.
    '''
    if self.running:
      return time.time() - self.started
    if self.started == None:
      return 0.0
    return self.stopped - self.started

  def start(self):
    'Start the timer.'

    if self.running:
      raise ValueError('Timer already started')
    self.reset()
    self.started = time.time()

  def stop(self):
    'Stop the timer.'

    if not self.running:
      raise ValueError('Timer not started')
    self.stopped = time.time()
    return self.time

  time = property(get_time)
  running = property(get_running)

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
