# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010-2014 Vifib SARL and Contributors.
# All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import sqlite3
import os
import pwd
import time
import json
import argparse
import psutil
from time import strftime
from datetime import datetime, timedelta

from slapos.collect.db import Database
from slapos.collect.reporter import ConsumptionReportBase

def parseArguments():
  """
  Parse arguments for monitor collector instance.
  """
  parser = argparse.ArgumentParser()
  parser.add_argument('--output_folder',
                      help='Path of the folder where output files should be written.')
  parser.add_argument('--pid_file',
                      help='Path where should be written the pid of process.')
  parser.add_argument('--partition_id',
                      help='ID of the computer partition to collect data from.')
  parser.add_argument('--collector_db',
                      help='The path of slapos collect database.')

  return parser.parse_args()

# XXX The code on the class below should be dropped and prefer to use
# the slapos.collect.db.Database directly:
#  - https://lab.nexedi.com/nexedi/slapos.core/blob/master/slapos/collect/db.py
# the code duplication here is huge so be carefull to not reimplemnt what is 
# already implement.

class ResourceCollect:

  def __init__(self, db_path = None):
    # XXX this code is duplicated with slapos.collect.db.Database.__init__
    assert os.path.exists(db_path)
    if db_path.endswith("collector.db"):
      db_path = db_path[:-len("collector.db")]
    # If the database is locked, wait until 15 seconds
    # Do not try to created or update tables, access will be refused
    self.db = Database(db_path, create=False, timeout=15)
    self.consumption_utils = ConsumptionReportBase(self.db)

  def has_table(self, name):
    self.db.connect()
    check_result_cursor = self.db.select(
      table="sqlite_master",
      columns='name',
      where="type='table' AND name='%s'" % name)
    table_exists_result = zip(*check_result_cursor)
    if not len(table_exists_result) or table_exists_result[0][0] is None:
      return False
    return True

  def getPartitionCPULoadAverage(self, partition_id, date_scope):
    return self.consumption_utils.getPartitionCPULoadAverage(partition_id, date_scope)

  def getPartitionUsedMemoryAverage(self, partition_id, date_scope):
    return self.consumption_utils.getPartitionUsedMemoryAverage(partition_id, date_scope)/(1024*1024.0)

  def getPartitionDiskUsedAverage(self, partition_id, date_scope):
    return self.consumption_utils.getPartitionDiskUsedAverage(partition_id, date_scope)/1024.0

  def getPartitionConsumption(self, partition_id, where="", date_scope=None, min_time=None, max_time=None):
    """
      Query collector db to get consumed resource for last minute
    """
    self.db.connect()
    comsumption_list = []
    if where != "":
      where = "and %s" % where
    if not date_scope:
      date_scope = datetime.now().strftime('%Y-%m-%d')
    if not min_time:
      min_time = (datetime.now() - timedelta(minutes=1)).strftime('%H:%M:00')
    if not max_time:
      max_time = (datetime.now() - timedelta(minutes=1)).strftime('%H:%M:59')

    columns = """count(pid), SUM(cpu_percent) as cpu_result, SUM(cpu_time),
                MAX(cpu_num_threads), SUM(memory_percent), SUM(memory_rss), pid, SUM(io_rw_counter),
                SUM(io_cycles_counter)"""
    query_result = self.db.select("user", date_scope, columns,
                   where="partition = '%s'  and (time between '%s' and '%s') %s" % 
                   (partition_id, min_time, max_time, where),
                   group="pid", order="cpu_result desc")
    for result in query_result:
      count = int(result[0])
      if not count > 0:
        continue
      resource_dict = {
        'pid': result[6],
        'cpu_percent': round(result[1]/count, 2),
        'cpu_time': round((result[2] or 0)/(60.0), 2),
        'cpu_num_threads': round(result[3]/count, 2),
        'memory_percent': round(result[4]/count, 2),
        'memory_rss': round((result[5] or 0)/(1024*1024.0), 2),
        'io_rw_counter': round(result[7]/count, 2),
        'io_cycles_counter': round(result[8]/count, 2)
      }
      try:
        pprocess = psutil.Process(int(result[6]))
      except psutil.NoSuchProcess:
        pass
      else:
        resource_dict['name'] = pprocess.name()
        resource_dict['command'] = pprocess.cmdline()
        resource_dict['user'] = pprocess.username()
        resource_dict['date'] = datetime.fromtimestamp(pprocess.create_time()).strftime("%Y-%m-%d %H:%M:%S")
      comsumption_list.append(resource_dict)
    self.db.close()
    return comsumption_list
  
  def getPartitionComsumptionStatus(self, partition_id, where="", date_scope=None, min_time=None, max_time=None):
    self.db.connect()
    if where != "":
      where = " and %s" % where
    if not date_scope:
      date_scope = datetime.now().strftime('%Y-%m-%d')
    if not min_time:
      min_time = (datetime.now() - timedelta(minutes=1)).strftime('%H:%M:00')
    if not max_time:
      max_time = (datetime.now() - timedelta(minutes=1)).strftime('%H:%M:59') 

    colums = """count(pid), SUM(cpu_percent), SUM(cpu_time), SUM(cpu_num_threads), SUM(memory_percent), 
                SUM(memory_rss), SUM(io_rw_counter), SUM(io_cycles_counter)"""  
    query_result = self.db.select('user', date_scope, colums, 
                                  where="partition='%s' and (time between '%s' and '%s') %s" % 
                                  (partition_id, min_time, max_time, where))
    result_list = zip(*query_result)

    process_dict = memory_dict = io_dict = {}
    if len(result_list):
      result = result_list
      process_dict = {'total_process': result[0][0],
        'cpu_percent': round((result[1][0] or 0), 2),
        'cpu_time': round((result[2][0] or 0)/(60.0), 2),
        'cpu_num_threads': round((result[3][0] or 0), 2),
        'date': '%s %s' % (date_scope, min_time)
      }
      memory_dict = {'memory_percent': round((result[4][0] or 0), 2),
        'memory_rss': round((result[5][0] or 0)/(1024*1024.0), 2),
        'date': '%s %s' % (date_scope, min_time)
      }
      io_dict = {'io_rw_counter': round((result[6][0] or 0), 2),
        'io_cycles_counter': round((result[7][0] or 0), 2),
        'disk_used': 0,
        'date': '%s %s' % (date_scope, min_time)
      }
      if self.has_table('folder'):
        disk_result_cursor = self.db.select(
          "folder", date_scope,
          columns="SUM(disk_used)", 
          where="partition='%s' and (time between '%s' and '%s') %s" % (
            partition_id, min_time, max_time, where
          )
        )
    
        disk_used_sum = zip(*disk_result_cursor)
        if len(disk_used_sum) and disk_used_sum[0][0] is not None:
          io_dict['disk_used'] = round(disk_used_sum[0][0]/1024.0, 2)
    self.db.close()
    return (process_dict, memory_dict, io_dict)

def appendToJsonFile(file_path, content, stepback=2):
  with open (file_path, mode="r+") as jfile:
    jfile.seek(0, 2)
    position = jfile.tell() - stepback
    jfile.seek(position)
    jfile.write('%s}' % ',"{}"]'.format(content))

def initProcessDataFile(process_file):
  with open(process_file, 'w') as fprocess:
    data_dict = {
      "date": time.time(),
      "data": ["date, total process, CPU percent, CPU time, CPU threads"]
    }
    fprocess.write(json.dumps(data_dict))

def initMemoryDataFile(mem_file):
  with open(mem_file, 'w') as fmem:
    data_dict = {
      "date": time.time(),
      "data": ["date, memory used percent, memory used"]
    }
    fmem.write(json.dumps(data_dict))

def initIODataFile(io_file):
  with open(io_file, 'w') as fio:
    data_dict = {
      "date": time.time(),
      "data": ["date, io rw counter, io cycles counter, disk used"]
    }
    fio.write(json.dumps(data_dict))

def main():
  parser = parseArguments()
  if not os.path.exists(parser.output_folder) and os.path.isdir(parser.output_folder):
    raise Exception("Invalid ouput folder: %s" % parser.output_folder)

  if parser.pid_file:
    # Check that this process is not running
    if os.path.exists(parser.pid_file):
      with open(parser.pid_file, "r") as pidfile:
        try:
          pid = int(pidfile.read(6))
        except ValueError:
          pid = None
        if pid and os.path.exists("/proc/" + str(pid)):
          print("A process is already running with pid " + str(pid))
          exit(1)
    with open(parser.pid_file, "w") as pidfile:
      pidfile.write('%s' % os.getpid())

  # Consumption global status
  process_file = os.path.join(parser.output_folder, 'monitor_resource_process.data.json')
  mem_file = os.path.join(parser.output_folder, 'monitor_resource_memory.data.json')
  io_file = os.path.join(parser.output_folder, 'monitor_resource_io.data.json')
  resource_file = os.path.join(parser.output_folder, 'monitor_process_resource.status.json')
  status_file = os.path.join(parser.output_folder, 'monitor_resource.status.json')

  if not os.path.exists(parser.collector_db):
    print "Collector database not found..."
    initProcessDataFile(process_file)
    initMemoryDataFile(mem_file)
    initIODataFile(io_file)
    with open(status_file, "w") as status_file:
      status_file.write(json.dumps({
        "cpu_time": 0,
        "cpu_percent": 0,
        "memory_rss": 0,
        "memory_percent": 0,
        "io_rw_counter": 0,
        "date": "",
        "total_process": 0,
        "disk_used": 0,
        "io_cycles_counter": 0,
        "cpu_num_threads": 0
      }))
    with open(resource_file, "w") as resource_file:
      resource_file.write('[]')
    exit(1)

  collector = ResourceCollect(parser.collector_db)

  date_scope = datetime.now().strftime('%Y-%m-%d')
  stat_info = os.stat(parser.output_folder)
  partition_user = pwd.getpwuid(stat_info.st_uid)[0]

  process_result, memory_result, io_result = collector.getPartitionComsumptionStatus(partition_user)

  label_list = ['date', 'total_process', 'cpu_percent', 'cpu_time', 'cpu_num_threads',
                  'memory_percent', 'memory_rss', 'io_rw_counter', 'io_cycles_counter',
                  'disk_used']
  resource_status_dict = {}
  if not os.path.exists(process_file) or os.stat(process_file).st_size == 0:
    initProcessDataFile(process_file)

  if not os.path.exists(mem_file) or os.stat(mem_file).st_size == 0:
    initMemoryDataFile(mem_file)

  if not os.path.exists(io_file) or os.stat(io_file).st_size == 0:
    initIODataFile(io_file)

  if process_result and process_result['total_process'] != 0.0:
    appendToJsonFile(process_file, ", ".join(
      [str(process_result[key]) for key in label_list if process_result.has_key(key)])
    )
    resource_status_dict.update(process_result)
  if memory_result and memory_result['memory_rss'] != 0.0:
    appendToJsonFile(mem_file, ", ".join(
      [str(memory_result[key]) for key in label_list if memory_result.has_key(key)])
    )
    resource_status_dict.update(memory_result)
  if io_result and io_result['io_rw_counter'] != 0.0:
    appendToJsonFile(io_file, ", ".join(
      [str(io_result[key]) for key in label_list if io_result.has_key(key)])
    )
    resource_status_dict.update(io_result)

  with open(status_file, 'w') as fp:
    fp.write(json.dumps(resource_status_dict))

  # Consumption Resource
  resource_process_status_list = collector.getPartitionConsumption(partition_user)
  if resource_process_status_list:
    with open(resource_file, 'w') as rf:
      rf.write(json.dumps(resource_process_status_list))

  if os.path.exists(parser.pid_file):
    os.unlink(parser.pid_file)
