#!/usr/bin/env python

"""
Check if a mariadb result matches the desired threshold or raises an error.
"""

import json
import os
import re
import sys
import time
import datetime
import argparse

def checkMariadbDigestResult(mariadbdex_path, mariadbdex_report_status_file,
                             max_query_threshold, slowest_query_threshold):
  message = "No mariadbdex result for today or yesterday"
  today = datetime.date.today()
  today_or_yesterday = today, today - datetime.timedelta(1)

  try:
    mariadbdex_file = max(os.listdir(mariadbdex_path),
      key=lambda x: os.stat(os.path.join(mariadbdex_path, x)).st_mtime)
  except ValueError:
    if datetime.date.fromtimestamp(os.stat(mariadbdex_path).st_mtime) in today_or_yesterday: 
        return 0, "Instance has been just deployed. Skipping check.."
  else:
    for date in today_or_yesterday:
      if mariadbdex_file == date.strftime('slowquery_digest.txt-%Y-%m-%d'):
        with open(os.path.join(mariadbdex_path, mariadbdex_file)) as f:
          content = f.read()
        if content:
          # XXX: if not a lot of usage, skip this
          regex = r"Overall: (.*) total,[\S\s]*# Exec time( *([\d]+)m?s?){4}"
          m = re.findall(regex, content)
          if m:
            total_queries_exec=m[0][0].strip()
            slowest_query_time=int(m[0][2].strip())
            has_k=total_queries_exec[-1:]
            if has_k == "k":
              pre=total_queries_exec[:-1]
              total_queries_exec=float(pre)*1000
            else:
              total_queries_exec=int(total_queries_exec)
            if total_queries_exec < max_query_threshold and slowest_query_time < slowest_query_threshold:
              return 0,  "Thanks for keeping it all clean, total queries are : " + str(total_queries_exec) + \
                         " slowest query time is : " + str(slowest_query_time)
            else:
              return 1, "Threshold is lower than expected: \nExpected total queries : " + \
                       str(max_query_threshold) +" and current is: " + str(total_queries_exec) + "\n"+ \
                       "Expected slowest query : " + str(slowest_query_threshold) + " and current is: " + \
                       str(slowest_query_time)
        message = "No result found in the slow query digest file or the file is corrupted"
        break

  if not os.path.exists(mariadbdex_report_status_file):
    return 0, "No slow query result yet!"
  with open(mariadbdex_report_status_file) as f:
    try:
      json_content = json.load(f)
    except ValueError, e:
      json_content = ''
  if json_content:
    message += "\n" + json_content["message"]
  return 1, message

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--ptdigest_path", required=True)
  parser.add_argument("--status_file", required=True)
  parser.add_argument("--max_queries_threshold", required=True)
  parser.add_argument("--slowest_query_threshold", required=True)
  args = parser.parse_args()

  status, message = checkMariadbDigestResult(args.ptdigest_path, args.status_file,
                                    args.max_queries_threshold, args.slowest_query_threshold
                                    )

  print message
  sys.exit(status)
