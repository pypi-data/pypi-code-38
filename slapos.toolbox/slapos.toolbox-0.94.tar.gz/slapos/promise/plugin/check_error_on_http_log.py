from zope import interface as zope_interface
from slapos.grid.promise import interface
from slapos.grid.promise.generic import GenericPromise, TestResult
import re
import time
import os

class RunPromise(GenericPromise):

  zope_interface.implements(interface.IPromise)

  def __init__(self, config):
    GenericPromise.__init__(self, config)
    # set periodicity to run the promise twice per day
    self.custom_frequency = int(self.getConfig('frequency', 720))
    self.setPeriodicity(self.custom_frequency)
    # Skip test check on this promise
    self.setTestLess()

  def sense(self):
    """
      Check if http log file contain errors
    """
    log_file = self.getConfig('log-file')
    maximum_delay = int(self.getConfig('maximum-delay', 0))
    if not log_file:
      raise ValueError("log file was not set in promise parameters.")

    regex = re.compile("^(\[[^\]]+\]) (\[[^\]]+\]) (.*)$")
    error_amount = 0
    no_route_error = 0
    network_is_unreachable = 0
    timeout = 0
    parsing_failure = 0

    if not os.path.exists(log_file):
      # file don't exist, nothing to check
      self.logger.info("OK")
      return

    with open(log_file) as f:
      f.seek(0, 2)
      block_end_byte = f.tell()
      f.seek(-min(block_end_byte, 4096), 1)
      data = f.read()
      for line in reversed(data.splitlines()):
        m = regex.match(line)
        if m is None:
          continue
        dt, level, msg = m.groups()
        try:
          try:
            t = time.strptime(dt[1:-1], "%a %b %d %H:%M:%S %Y")
          except ValueError:
            # Fail to parser for the first time, try a different output.
            t = time.strptime(dt[1:-1], "%a %b %d %H:%M:%S.%f %Y")
        except ValueError:
            # Probably it fail to parse
            if parsing_failure < 3:
              # Accept failure 2 times, as the line can be actually
              # cut on the middle.
              parsing_failure += 1
              continue
            raise
        if maximum_delay and (time.time()-time.mktime(t)) > maximum_delay:
          # no result in the latest hour
          break
        if level != "[error]":
          continue
        # Classify the types of errors
        if "(113)No route to host" in msg:
          no_route_error += 1
        elif "(101)Network is unreachable" in msg:
          network_is_unreachable += 1
        elif "(110)Connection timed out" in msg:
          timeout += 1
        error_amount += 1
    if error_amount:
      self.logger.error("ERROR=%s (NOROUTE=%s, UNREACHABLENET=%s, TIMEOUT=%s)" % (
        error_amount, no_route_error, network_is_unreachable, timeout))
    else:
      self.logger.info("OK")

  def anomaly(self):
    # only check the result of the two latest sense call
    return self._test(result_count=2, failure_amount=2, latest_minute=self.custom_frequency*3)
