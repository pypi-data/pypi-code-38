from zope import interface as zope_interface
from slapos.grid.promise import interface
from slapos.grid.promise.generic import GenericPromise

import os
import sys

import sqlite3
import argparse
import datetime
import psutil

from slapos.collect.db import Database

class RunPromise(GenericPromise):

  zope_interface.implements(interface.IPromise)

  def __init__(self, config):
    GenericPromise.__init__(self, config)
    # check disk space at least every 3 minutes
    self.setPeriodicity(minute=3)

  def getFreeSpace(self, disk_partition, database, date, time):

    database = Database(database, create=False, timeout=10)
    try:
      # fetch free disk space
      database.connect()
      where_query = "time between '%s:00' and '%s:30' and partition='%s'" % (time, time, disk_partition)
      query_result = database.select("disk", date, "free", where=where_query)
      result = zip(*query_result)
      if not result or not result[0][0]:
        self.logger.info("No result from collector database: disk check skipped")
        return 0
      disk_free = result[0][0]
    except sqlite3.OperationalError, e:
      # if database is still locked after timeout expiration (another process is using it)
      # we print warning message and try the promise at next run until max warn count
      locked_message = "database is locked"
      if locked_message in str(e) and \
          not self.raiseOnDatabaseLocked(locked_message):
        return 0
      raise
    finally:
      try:
        database.close()
      except Exception:
        pass
    return int(disk_free)

  def raiseOnDatabaseLocked(self, locked_message):
    max_warn = 10
    latest_result_list = self.getLastPromiseResultList(result_count=max_warn)
    warning_count = 0
    if len(latest_result_list) < max_warn:
      return False

    for result in latest_result_list[0]:
      if result['status'] == "ERROR" and locked_message in result["message"]:
        return True

    for result_list in latest_result_list:
      found = False
      for result in result_list:
        if result['status'] == "WARNING" and locked_message in result["message"]:
          found = True
          warning_count += 1
          break
      if not found:
        break
    if warning_count == max_warn:
      # too many warning on database locked, now fail.
      return True

    self.logger.warn("collector database is locked by another process")
    return False

  def getInodeUsage(self, path):
    max_inode_usage = 97.99 # < 98% usage
    stat = os.statvfs(path)
    usage_output = ""
    total_inode = stat.f_files
    free_inode = stat.f_ffree
    usage = round((float(total_inode - free_inode) / total_inode), 4) * 100
    if usage > max_inode_usage:
      return "Disk Inodes usages is really high: %s%%" % usage
    elif os.path.exists('/tmp'):
      # check if /tmp is mounted on another disk than path
      tmp_stat = os.statvfs('/tmp')
      if tmp_stat.f_blocks != stat.f_blocks:
        tmp_usage = round((float(tmp_stat.f_files - tmp_stat.f_ffree) / tmp_stat.f_files), 4) * 100
        if tmp_usage > max_inode_usage:
          return "Disk Inodes usage is high: %s%%" % tmp_usage
    return ""


  def sense(self):
    # find if a disk is mounted on the path
    disk_partition = ""
    disk_threshold_file = self.getConfig('threshold-file')
    db_path = self.getConfig('collectordb')
    check_date = self.getConfig('test-check-date')
    path = os.path.join(self.getPartitionFolder(), "") + "extrafolder"
    partitions = psutil.disk_partitions()
    while path is not '/':
      if not disk_partition:
        path = os.path.dirname(path)
      else:
        break
      for p in partitions:
        if p.mountpoint == path:
          disk_partition = p.device
          break
    if not disk_partition:
      self.logger.error("Couldn't find disk partition")
      return

    min_free_size = 1024*1024*1024*2 # 2G by default
    if disk_threshold_file is not None:
      if os.path.exists(disk_threshold_file):
        with open(disk_threshold_file) as f:
          min_size_str = f.read().strip()
          if min_size_str == '0':
            # disable check
            self.logger.info("Free disk space check is disabled\n set a number up to 0 to enable!")
            return
          if min_size_str.isdigit():
            value = int(min_size_str)
            if value >= 200:
              # Minimum value is 200Mb, it's already low
              min_free_size = int(min_size_str)*1024*1024
      else:
        with open(disk_threshold_file, 'w') as f:
          f.write(str(min_free_size/(1024*1024)))

    if check_date:
      # testing mode
      currentdate = check_date
      currenttime = self.getConfig('test-check-time', '09:17')
      disk_partition = self.getConfig('test-disk-partition', '/dev/sda1')
    else:
      # get last minute
      now = datetime.datetime.now()
      currentdate = now.strftime('%Y-%m-%d')
      currenttime = now - datetime.timedelta(minutes=1)
      currenttime = currenttime.time().strftime('%H:%M')

    if db_path.endswith("collector.db"):
      db_path=db_path[:-len("collector.db")]

    free_space = self.getFreeSpace(disk_partition, db_path, currentdate,
                                   currenttime)
    if free_space == 0:
      return
    elif free_space > min_free_size:
      inode_usage = self.getInodeUsage(self.getPartitionFolder())
      if inode_usage:
        self.logger.error(inode_usage)
      else:
        self.logger.info("Disk usage: OK")
      return

    free_space = round(free_space/(1024.0*1024*1024), 2)
    min_space = round(min_free_size/(1024.0*1024*1024), 2)
    self.logger.error('Free disk space low: remaining %s G (threshold: %s G)' % (
      free_space, min_space))

  def test(self):
    return self._test(result_count=1, failure_amount=1)

  def anomaly(self):
    return self._test(result_count=3, failure_amount=3)
