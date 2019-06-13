from zope import interface as zope_interface
from slapos.grid.promise import interface
from slapos.grid.promise.generic import GenericPromise

import subprocess
import os

class RunPromise(GenericPromise):

  zope_interface.implements(interface.IPromise)

  def __init__(self, config):
    GenericPromise.__init__(self, config)
    # test load every 3 minutes
    self.setPeriodicity(minute=3)

  def checkCPULoad(self, tolerance=2.2):

    # tolerance=1.5 => accept CPU load up to 1.5 =150%
    uptime_result = subprocess.check_output(['uptime'])
    line = uptime_result.strip().split(' ')
    load, load5, long_load = line[-3:]
    long_load = float(long_load.replace(',', '.'))
    core_count = int(subprocess.check_output(['nproc']).strip())
    max_load = core_count * tolerance
    if long_load > max_load:
      # display top statistics
      top_result = subprocess.check_output(['top', '-n', '1', '-b'])
      message = "CPU load is high: %s %s %s\n\n" % (load, load5, long_load)
      i = 0
      result_list = top_result.split('\n')
      # display first 5 lines
      while i < len(result_list) and i < 5:
        message += "\n%s" % result_list[i]
        i += 1
      self.logger.error(message)
    else:
      self.logger.info("CPU load is OK")

  def sense(self):
    load_threshold = self.getConfig('cpu-load-threshold')
    threshold = 0

    if load_threshold is not None:
      try:
        threshold = float(load_threshold)
      except ValueError, e:
        self.logger.error("CPU load threshold %r is not valid: %s" % (load_threshold, e))
        return

    self.checkCPULoad(threshold or 2.2)

  def test(self):
    # fail if load is high than the threshold for more than 30 minutes
    return self._test(result_count=10, failure_amount=10)

  def anomaly(self):
    # fail if load is high than the threshold for more than 30 minutes
    return self._test(result_count=10, failure_amount=10)
