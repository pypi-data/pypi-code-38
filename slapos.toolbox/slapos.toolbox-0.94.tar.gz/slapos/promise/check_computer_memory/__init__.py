#!/usr/bin/env python

"""
Check if memory usage is lower a given threshold.

Uses:
- /proc/meminfo
"""

import sys
import sqlite3
import argparse
import datetime

from slapos.collect.db import Database

def getMemoryInfo(database, time, date):

  memory_info = {}
  database = Database(database, create=False, timeout=5)
  try:
    database.connect()
    query_result = database.select("computer", date, "memory_size", limit=1) 
    result = zip(*query_result)
    if not result or not result[0][0]:
      return (None, "couldn't fetch total memory, collectordb is empty?")
    memory_info['total'] = int(result[0][0])  # in byte

    # fetch free and used memory 
    where_query = "time between '%s:00' and '%s:30' " % (time, time)
    query_result = database.select("system", date, "memory_free, memory_used", where=where_query)
    result = zip(*query_result)
    if not result or not result[0][0]: 
      return (None, "couldn't fetch free memory")
    memory_info['free'] = int(result[0][0])  # in byte
    if not result or not result[1][0]: 
      return (None, "couldn't fetch used memory")
    memory_info['used'] = int(result[1][0])  # in byte
  finally:
    database.close()

  memory_info["used_percent"] = memory_info["used"] * 100.0 / memory_info["total"]
  memory_info["free_percent"] = memory_info["free"] * 100.0 / memory_info["total"]
  return (memory_info, "")

def checkMemoryUsage(database_path, time, date, threshold, key="used", unit="byte"):
  if key not in ("used", "free"):
    raise ValueError("invalid key")
  if unit not in ("byte", "percent"):
    raise ValueError("invalid unit")
  memory_info, error = getMemoryInfo(database_path, time, date)
  if error:
    return (False, "error", error)
  if unit == "byte":
    if key == "used":
      if memory_info["used"] <= threshold:
        return (True, "OK - memory used: {used}B of {total}B ({used_percent:.1f}%)".format(**memory_info), "")
      return (False, "Low available memory - usage: {used}B of {total}B ({used_percent:.1f}%)".format(**memory_info), "")
    else:  # if key == "free":
      if memory_info["free"] > threshold:
        return (True, "OK - free memory: {free}B of {total}B ({free_percent:.1f}%)".format(**memory_info), "")
      return (False, "Low available memory - free: {free}B of {total}B ({free_percent:.1f}%)".format(**memory_info), "")
  else:  # if unit == "percent":
    if key == "used":
      if memory_info["used_percent"] <= threshold:
        return (True, "OK - memory used: {used_percent:.1f}% ({used}B of {total}B)".format(**memory_info), "")
      return (False, "Low available memory - usage: {used_percent:.1f}% ({used}B of {total}B)".format(**memory_info), "")
    else:  # if key == "free":
      if memory_info["free_percent"] > threshold:
        return (True, "OK - free memory: {free_percent:.1f}% ({free}B of {total}B)".format(**memory_info), "")
      return (False, "Low available memory - free: {free_percent:.1f}% ({free}B of {total}B)".format(**memory_info), "")

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-db", "--collectordb", required=True)
  parser.add_argument("--threshold", required=True, type=float)
  parser.add_argument("--key", default="used", choices=("used", "free"))
  parser.add_argument("--unit", default="byte", choices=("byte", "percent"))
  args = parser.parse_args()

  # get last minute
  now = datetime.datetime.now()
  currentdate = now.strftime('%Y-%m-%d')
  delta = datetime.timedelta(minutes=1)
  currenttime = now - delta
  currenttime = currenttime.time().strftime('%H:%M')
  db_path = args.collectordb

  if db_path.endswith("collector.db"):db_path=db_path[:-len("collector.db")]

  result, message, error = checkMemoryUsage(
    db_path, currenttime, currentdate,
    threshold=args.threshold,
    key=args.key,
    unit=args.unit,
  )
  if error:
    print error
    return 0
  print message
  return 0 if result else 1

if __name__ == "__main__":
  sys.exit(main())
