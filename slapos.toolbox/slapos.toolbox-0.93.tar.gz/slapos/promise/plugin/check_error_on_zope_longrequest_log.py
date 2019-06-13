from zope import interface as zope_interface
from slapos.grid.promise import interface
from slapos.grid.promise.generic import GenericPromise
import time

import os
import sys
import re

r = re.compile("^([0-9]+\-[0-9]+\-[0-9]+ [0-9]+\:[0-9]+\:[0-9]+)(\,[0-9]+) - ([A-z]+) (.*)$")

class RunPromise(GenericPromise):

  zope_interface.implements(interface.IPromise)

  def __init__(self, config):
    GenericPromise.__init__(self, config)
    self.setPeriodicity(minute=10)

  def sense(self):
    log_file = self.getConfig('log-file')
    error_threshold = self.getConfig('error-threshold')
    maximum_delay = self.getConfig('maximum-delay')
    error_amount = 0
    if not os.path.exists(log_file):
      # file don't exist, nothing to check
      self.logger.info("log file does not exist: log check skipped")
      return 0
    
    with open(log_file) as f:
      f.seek(0, 2)
      block_end_byte = f.tell()
      f.seek(-min(block_end_byte, 4096*10), 1)
      data = f.read()
      for line in reversed(data.splitlines()):
        m = r.match(line)
        if m is None:
          continue
        dt, _, level, msg = m.groups()
        try:
          t = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
        except ValueError:
          continue
        if maximum_delay and (time.time()-time.mktime(t)) > maximum_delay:
          # no result in the latest hour
          break
        error_amount += 1
    if error_amount > error_threshold:
      self.logger.error('ERROR: Site has %s long request' % error_amount)
    else:
      self.logger.info('INFO: Site has %s long request' % error_amount)

  def test(self):
    return self._test(result_count=1, failure_amount=1)

  def anomaly(self):
    return self._test(result_count=3, failure_amount=3)
