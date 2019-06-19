import json
import sys
import glob
import time
import os
import argparse

def parseArguments():
  """
  Parse arguments for monitor statistics.
  """
  parser = argparse.ArgumentParser()
  parser.add_argument('--history_folder',
                      help='Path where history files are located and where stats will be generated.')

  return parser


def buildStatistic(history_folder):
  now = time.time()
  for p in glob.glob("%s/*.history.json" % history_folder):
    result = {}
    stats_list = []
    promise_name = p.split("/")[-1].replace(".history.json", "")

    stat_file_path = p.replace(".history.json", ".stats.json")
    if os.path.exists(stat_file_path):
      with open(stat_file_path) as f:
        stats_dict = json.load(f)
        f.close()
    else:
      stats_dict = {"date": now, "data": []}

    last_date = None
    if stats_dict["data"]:
      if stats_dict["data"][-1].has_key("start-date"):
        last_date = stats_dict["data"][-1]["start-date"]
      else:
        last_date = stats_dict["data"][-1]["date"]

    with open(p) as f:
      j = json.load(f)

      j_last_date = j['data'][-1]["date"]
      if last_date == j_last_date:
        # This file was already loaded, so skip
        continue

      for entry in j['data']:
        day = entry["date"].split("T")[0]
        result.setdefault(day, {"ERROR": 0, "OK": 0})
        result[day][str(entry["status"])] += 1
      f.close()

    for date, stat in result.iteritems():
      stats_list.append(
        {"status": "ERROR" if stat["ERROR"] > 0 else "OK",
         "change-time": now,
         "date": j_last_date,
         "message": stat})


    stats_dict["data"].extend(stats_list)

    with open(stat_file_path, "w+") as f:
      f.write(json.dumps(stats_dict))
      f.truncate()
      f.close()

def main():
  arg_parser = parseArguments()
  config = arg_parser.parse_args()
  buildStatistic(config.history_folder)
  sys.exit(0)
