from zope import interface as zope_interface
from slapos.grid.promise import interface
from slapos.grid.promise.generic import GenericPromise
try:
  import subprocess32 as subprocess
except ImportError:
  import subprocess

class RunPromise(GenericPromise):

  zope_interface.implements(interface.IPromise)

  def __init__(self, config):
    GenericPromise.__init__(self, config)
    # check configuration every 5 minutes (only for anomaly)
    self.setPeriodicity(minute=int(self.getConfig('frequency', 5)))

  def sense(self):
    """
      Run frontend validatation script
    """

    validate_script = self.getConfig('verification-script')
    if not validate_script:
      raise ValueError("'verification-script' was not set in promise parameters.")
    process = subprocess.Popen(
        [validate_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    message = process.communicate()[0]
    if process.returncode == 0:
      self.logger.info("OK")
    else:
      self.logger.error("%s" % message)

  def anomaly(self):
    return self._anomaly(result_count=1, failure_amount=1)
