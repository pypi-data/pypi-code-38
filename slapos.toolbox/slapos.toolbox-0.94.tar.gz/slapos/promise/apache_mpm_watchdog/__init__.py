import requests
import re
import signal
import os
import psutil
import json
import time
import argparse

search_pid_regex = r"</td><td.*?>(.+?)</td><td>yes \(old gen\)</td>"

def loadJSONFile(db_path):
  if os.path.exists(db_path):
    with open(db_path) as json_file:
       try:
         return json.load(json_file)
       except ValueError:
         return {}
  else:
    return {}

def writeJSONFile(pid_dict, db_path):
  if db_path is None:
    # No place to save
    return 
  for pid in pid_dict.copy():
    try:
      process = psutil.Process(int(pid))
    except psutil.NoSuchProcess:
      del pid_dict[pid]

  with open(db_path, "w") as f:
    f.write(json.dumps(pid_dict))

def getServerStatus(url, user, password):
  try: 
    if user is not None:
      r = requests.get(url, auth=(user, password))
    else:
      r = requests.get(url)

    if r.status_code == 200:
      return r.text
  except requests.exceptions.ConnectionError:
    return 

def watchServerStatus(pid_dict, server_status, timeout):
  _pid_dict = pid_dict.copy()
  for i in re.findall(search_pid_regex, server_status):
    try:
      process = psutil.Process(int(i))
    except psutil.NoSuchProcess:
      continue

    # Ensure the process is actually an apache
    if process.cmdline()[0].endswith("/httpd"):
      _pid_dict.setdefault(i, time.time() + timeout)
      if _pid_dict[i] < time.time():
        print "Sending signal -%s to %s" % (signal.SIGKILL, i)
        try:
          process.kill()
        except psutil.NoSuchProcess:
          print "Process is not there anymore"
          continue

  return _pid_dict

def main():
  parser = argparse.ArgumentParser()
  # Address to ping to
  parser.add_argument("--url", required=True)
  # Force use ipv4 protocol
  parser.add_argument("-u", "--user")
  parser.add_argument("-p", "--password")
  parser.add_argument("-d", "--db")
  parser.add_argument("-t", "--timeout", default=600)
  args = parser.parse_args()

  pid_dict = loadJSONFile(args.db)

  server_status = getServerStatus(
    args.url, args.user, args.password)

  if server_status is None:
    raise ValueError("Couldn't connect to server status page")

  pid_dict = watchServerStatus(pid_dict, server_status, args.timeout)

  writeJSONFile(pid_dict, args.db)

