#!/usr/bin/env python

"""
Check user memory usage according to a given threshold.
"""

import sys
import os
import argparse
from datetime import datetime, timedelta

from slapos.collect.db import Database

def escapeSqlStringValue(string):
  return string.replace("'", "\\'")

def getMemoryInfo(database_path, moment, user):
  """
  Gives `user` memory info dict at `moment`.
  ex: for moment = 2017-08-13 01:02:03
      it searches the results from 01:00:02 to 01:02:03
      and take the latest one.
  """
  date_str = moment.strftime("%Y-%m-%d")
  # time is `(moment-1min) +/- 1min`
  time_from_str = (moment - timedelta(minutes=2) - timedelta(seconds=1)).strftime("%H:%M:%S")
  time_to_str = moment.strftime("%H:%M:%S")
  if time_from_str > time_to_str:
    #   "23:59:59" > "00:02:00"
    time_from_str = "00:00:00"
  escaped_user = escapeSqlStringValue(user)
  memory_info = {}
  database = Database(database_path, create=False, timeout=5)
  try:
    database.connect()
    result = list(database.select(
      table="user",
      date=date_str,
      columns="memory_percent, memory_rss",
      where="partition = '{}' AND time BETWEEN '{}' AND '{}'".format(escaped_user, time_from_str, time_to_str),
      order="time DESC",
      limit=1,
    ))
    if len(result) == 0:
      return (None, "No result found in collector.db.")
    memory_info["percent"] = result[0][0]
    memory_info["byte"] = int(result[0][1])  # in byte
  finally:
    database.close()

  return (memory_info, "")

def checkMemoryUsage(database_path, moment, user, threshold, unit="byte"):
  if unit not in ("byte", "percent"):
    raise ValueError("invalid unit")
  memory_info, error = getMemoryInfo(database_path, moment, user)
  if error:
    return (False, "error", error)
  if unit == "byte":
    if memory_info["byte"] <= threshold:
      return (True, "User memory usage: {byte}B ({percent:.1f}%)".format(**memory_info), "")
    return (False, "High user memory usage: {byte}B ({percent:.1f}%)".format(**memory_info), "")
  else:  # if unit == "percent":
    if memory_info["percent"] <= threshold:
      return (True, "User memory usage: {percent:.1f}% ({byte}B)".format(**memory_info), "")
    return (False, "High user memory usage: {percent:.1f}% ({byte}B)".format(**memory_info), "")

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--collectordb", required=True,
                      help="the directory path of the 'collector.db' file.")
  parser.add_argument("--user", required=True)
  parser.add_argument("--threshold", required=True, type=float)
  parser.add_argument("--unit", default="byte", choices=("byte", "percent"))
  args = parser.parse_args()

  database_path = args.collectordb
  # --collectordb : can also be the path of 'collector.db' itself
  if os.path.basename(database_path) == "collector.db":
    database_path = os.path.dirname(database_path)

  result, message, error = checkMemoryUsage(
    database_path,
    datetime.now(),
    user=args.user,
    threshold=args.threshold,
    unit=args.unit,
  )
  if error:
    print error
    return 0
  print message
  return 0 if result else 1

if __name__ == "__main__":
  sys.exit(main())
