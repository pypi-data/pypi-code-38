#!/usr/bin/env python
"""
Check if a process is running with an old version of the modules
found in the running python paths + optional additional python paths.

It parses all folders containing an `__init__.py` file and checks if
a file modification date is greater than the start date of the
process.
"""

import sys
import os
import errno
import argparse
import time
import psutil

ignored_extension_set = set([".pyc"])

def moduleIsModifiedSince(top, since, followlinks=False):
  for root, dir_list, file_list in os.walk(top, followlinks=followlinks):
    if root == top:
      continue
    if "__init__.py" not in file_list:
      del dir_list[:]
      continue
    for name in file_list:
      _, ext = os.path.splitext(name)
      if ext in ignored_extension_set:
        continue
      if since < os.stat(os.path.join(root, name)).st_mtime:
        print "%s was modified since the process started." % \
                                                       os.path.join(root, name)
        print "Process Time %s < Last modidified file %s" % (time.ctime(since),
                        time.ctime(os.stat(os.path.join(root, name)).st_mtime))
        return True
  return False

def isProcessOlderThanDependencySet(pid, python_path_list, kill=False):
  process = psutil.Process(pid)
  start_time = process.create_time()
  if any(moduleIsModifiedSince(product_path, start_time) for product_path in python_path_list):
    if kill:
      print "Terminating process %s with pid %s" % (process.name(), pid)
      process.terminate()
    return True
  return False

def isProcessFromPidFileOlderThanDependencySet(pid_file_path, python_path_list, kill=False):
  with open(pid_file_path, "r") as f:
    pid = int(f.readline())
  return isProcessOlderThanDependencySet(pid, python_path_list, kill=kill)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-k", "--kill", action="store_true")
  parser.add_argument("pid_file_path", metavar="PID_FILE")
  parser.add_argument("python_path_list", nargs="*", metavar="ADDITIONAL_PYTHON_PATH", default=[])
  args = parser.parse_args()

  try:
    if isProcessFromPidFileOlderThanDependencySet(args.pid_file_path, sys.path + args.python_path_list, kill=args.kill):
      return 1
    return 0
  except (OSError, IOError) as err:
    if err.errno == errno.ENOENT:
      return 0
    raise
  except psutil.NoSuchProcess:
    return 0

if __name__ == "__main__":
  sys.exit(main())
