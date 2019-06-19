from zope import interface as zope_interface
from slapos.grid.promise import interface
from slapos.grid.promise.generic import GenericPromise
from slapos.grid.promise.generic import TestResult

import re
import sys
import pytz
from os.path import isfile, getmtime
from datetime import datetime
from croniter import croniter
from dateutil.parser import parse
from tzlocal import get_localzone

class RunPromise(GenericPromise):

  zope_interface.implements(interface.IPromise)

  def __init__(self, config):
    GenericPromise.__init__(self, config)
    # check backup ran OK every 5 minutes
    self.setPeriodicity(minute=5)

  def sense(self):
    """
      backupserver run rdiff-backup and log everything in a text file.
      At the beginning of the backup, we have "backup running" printed in the text file.
      At the end of the backup, we can have one of the following printed in the text file:
         * "backup failed" -> backup failed
         * "backup success" -> backup succeeded
      A backup is valid only if we have the 2 conditions:
         * we can grep "backup running" in the text file
         * we can't grep "backup failed" in the text file
    """

    script = self.getConfig('script_fullpath')
    status = self.getConfig('status_fullpath')
    local_tz = get_localzone()
    prev_cron = croniter(self.getConfig('cron_frequency'), datetime.now()).get_prev(datetime) # date of the previous time cron launched
    prev_cron = local_tz.localize(prev_cron)
    status_url = "{}/private/{}/{}".format(self.getConfig("monitor_url"), self.getConfig("status_dirbasename"), self.getConfig("status_name"))
    statistic_url = "{}/private/{}/{}".format(self.getConfig("monitor_url"), self.getConfig("statistic_dirbasename"), self.getConfig("statistic_name"))

    # If log file is not present, it can be OK if we launched the instance after the last cron due date
    if not isfile(status):
      if pytz.utc.localize(datetime.utcfromtimestamp(getmtime(script))) < prev_cron:
        self.logger.error("Backup status file is not present")
      else:
        self.logger.info("Backup was never launched")
      return

    # First, parse the log file
    backup_started = False
    backup_ended = False
    for line in open(status, 'r'):
      m = re.match(r"(.*), (.*), (.*), backup (.*)$", line)
      if m:
        if m.group(4) == "running":
          backup_started = True
          backup_start = parse(m.group(1))
        elif m.group(4) == "failed":
          backup_ended = True
          backup_failed = True
          backup_end = parse(m.group(1))
        elif m.group(4) == "success":
          backup_ended = True
          backup_failed = False
          backup_end = parse(m.group(1))

    # Then check result
    if backup_ended and backup_failed:
      self.logger.error("Backup FAILED at {} (see {} ).".format(backup_end, status_url))
    elif not backup_started:
      self.logger.error("Can't find backup start date. Is there a problem with status file? (see {} ).".format(status_url))
    elif backup_start < prev_cron:
      self.logger.error("Backup didn't start at correct time: it started at {} but should have started after {}. (see {} ).".format(backup_start, prev_cron, status_url))
    elif not backup_ended:
      self.logger.info("Backup currently running, started at {} (see {} ).".format(backup_start, status_url))
    else:
      self.logger.info("Backup OK, started at {} and lasted {} (see full stats at {} and status at {} ).".format(
        backup_start,
        backup_end - backup_start,
        statistic_url,
        status_url
      ))

  def test(self):
    """
      This is the default test function. Could be commented.
    """
    return self._test(result_count=1, failure_amount=1)

  def anomaly(self):
    """
      Anomaly returns a TestResult instead of AnomalyResult because we don't
      want to call bang when there is a problem. Usually the problem won't be
      in the deployment of this instance but rather in the instance we are
      backuping. This will need a human intervention.
    """
    return self._test(result_count=1, failure_amount=1)
