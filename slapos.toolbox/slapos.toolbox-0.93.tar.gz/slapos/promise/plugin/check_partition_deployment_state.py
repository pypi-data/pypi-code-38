from zope import interface as zope_interface
from slapos.grid.promise import interface
from slapos.grid.promise.generic import GenericPromise
import os
from datetime import datetime

class RunPromise(GenericPromise):

  zope_interface.implements(interface.IPromise)

  def __init__(self, config):
    GenericPromise.__init__(self, config)
    self.setPeriodicity(minute=1)

  def sense(self):
    """
      Run the promise code and store the result
        raise error, log error message, ... for failure
    """

    partition_folder = self.getPartitionFolder()
    log_folder = os.path.join(partition_folder, 'var/log')
    log_name = 'slapgrid-%s-error.log' % self.getConfig('partition-id')
    slapgrid_error_log_file = os.path.join(partition_folder, '.%s' % log_name)
    link_file = os.path.join(log_folder, log_name)
    monitor_url = self.getConfig('monitor-url')
    message = ''
    if os.path.exists(slapgrid_error_log_file) and \
        os.stat(slapgrid_error_log_file).st_size:
      message = 'Buildout failed to process %s.' % self.getConfig('partition-id')
      if monitor_url:
        message += '\nSee %s/log/%s for more information.' % (monitor_url, log_name)
      if not os.path.exists(link_file):
        os.symlink(slapgrid_error_log_file, link_file)
    else:
      if os.path.exists(link_file):
        os.unlink(link_file)

    if message:
      self.logger.error(message)
    else:
      self.logger.info("buildout is OK")

  def test(self):
    """
      Test promise and say if problem is detected or not
      Return TestResult object
    """
    return self._test(result_count=1, failure_amount=1)

  def anomaly(self):
    return self._test(result_count=2, failure_amount=2)
