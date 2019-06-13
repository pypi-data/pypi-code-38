import argparse
import datetime
import os
import re
import time
import PyRSS2Gen as RSS2

from collections import OrderedDict

def parseArguments():
  """
  Parse arguments for rdiff-backup statistics Rss Generator.
  """
  parser = argparse.ArgumentParser()
  parser.add_argument('--rdiff_backup_data_folder',
                      help='Path where to find rdiff-backup statistical files')
  parser.add_argument('--output',
                      help='Path where to save the feed')
  parser.add_argument('--feed_url',
                      help='Url of this feed file.')

  return parser.parse_args()

def makeDictFromStatFile(text_content):
  m = re.search("([a-zA-Z]*) ([0-9 :.]*) \(([a-zA-Z0-9 :.]*)\)", text_content)
  if m:
    return {'metric': m.group(1),
            'value': m.group(2),
            'human_readable_value': m.group(3)}
  m = re.search("([a-zA-Z]*) ([0-9]*)", text_content)
  if m:
    return {'metric': m.group(1),
            'value': m.group(2),
            'human_readable_value': m.group(2)}

def getRSSItemFromDict(item, option):
  description = "Metric;Value;Human Readable Value\n"
  for entry in item:
    description += "%s;%s;%s\n" % (entry['metric'], entry['value'], entry['human_readable_value'])
    if entry['metric'] == "EndTime":
      pubDate = datetime.datetime.fromtimestamp(float(entry['value']))
  return RSS2.RSSItem(
    title="Rdiff-Backup Transfer Statistics",
    link=option.feed_url,
    pubDate=pubDate,
    description=description)

def genRSS(option):
  """
  Read statistics file from rdiff-backup and generate a RSS feed entry from it
  """
  stat_file_list = sorted([file for file in os.listdir(option.rdiff_backup_data_folder)
                           if file.startswith('session_statistics')])

  item_dict = OrderedDict()
  for stat_file in stat_file_list:
    with open(os.path.join(option.rdiff_backup_data_folder, stat_file), 'r') as file:
      item_dict[stat_file] = [makeDictFromStatFile(line.strip()) for line in file.readlines()]
  title="Rdiff-Backup Statistics"
  rss_feed = RSS2.RSS2(
    title=title,
    link=option.feed_url,
    description=title,
    items = [getRSSItemFromDict(item_dict[item], option) for item in item_dict])

  return rss_feed.to_xml()

def main():
  option = parseArguments()
  feed = genRSS(option)

  with open(option.output, 'w') as rss_file:
    rss_file.write(feed)

  exit(0)
