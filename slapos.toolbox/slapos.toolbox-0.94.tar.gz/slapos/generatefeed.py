# Command-line script to generate a RSS feed from a bunch of well-formated
# JSON items.
# This script tries to be the more generic possible. The items used to generate
# the feed must be JSON-formatted (because of simplicity to read/write them),
# and their keys must follow the names of elements of items as described
# in the RSS2 specification :
#   http://cyber.law.harvard.edu/rss/rss.html#hrelementsOfLtitemgt


import argparse
import collections
import datetime
import json
import os
import PyRSS2Gen as rss

def parseArguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('--output', dest='output', type=str, required=True,
                      help='Path where to save the file')
  parser.add_argument('--status-item-path', dest='status_item_path',
                      type=str, required=True,
                      help='Path where to find feed items')
  parser.add_argument('--max-item', dest='max_item', type=int,
                      default=50, required=False,
                      help='Maximum number of items in the feed')

  parser.add_argument('--title', dest='feed_title', type=str, required=True,
                      help='Title of the feed')
  parser.add_argument('--link', dest='feed_link', type=str, required=True,
                      help='Link of the feed')
  parser.add_argument('--description', dest='feed_description',
                      type=str, required=False,
                      help='Description of the feed')

  option = parser.parse_args()
  if not hasattr(option, 'feed_description'):
    option.feed_description = option.feed_title

  return option


def deleteFileList(file_list):
  for file in file_list:
    try:
      os.unlink(file)
    except OSError:
      pass


def getRSSItemListFromItemDict(item_dict):
  rss_item_list = []

  for item in item_dict:
    item_dict[item]['pubDate'] = datetime.datetime.fromtimestamp(item_dict[item]['pubDate'])
    rss_item_list.append(rss.RSSItem(**item_dict[item]))

  return rss_item_list


def generateFeed(option):
  item_dict = {} # {file: content}

  for filename in os.listdir(option.status_item_path):
    file_path = os.path.join(option.status_item_path, filename)
    with open(file_path, 'r') as fd:
      try:
        item_dict[file_path] = json.load(fd)
      except ValueError:
        # JSON couldn't be decoded, let's trash it as
        # no useful information can be extracted
        os.unlink(file_path)

  sorted_item_dict = collections.OrderedDict(
      sorted(item_dict.items(), key=lambda x: x[1]['pubDate']))

  # Reduces feed if number of items exceeds max_item
  if len(item_dict) > option.max_item:
    outdated_key_list = sorted_item_dict.keys()[:-option.max_item]
    for outdated_key in outdated_key_list:
      del sorted_item_dict[outdated_key]
    deleteFileList(outdated_key_list)

  # Generate feed
  feed = rss.RSS2(
    title=option.feed_title,
    link=option.feed_link,
    description=option.feed_description,
    lastBuildDate = datetime.datetime.now(),
    items = getRSSItemListFromItemDict(sorted_item_dict)
  )

  return feed.to_xml()


def main():
  option = parseArguments()
  feed = generateFeed(option)
  open(option.output, 'w').write(feed)


if __name__ == "__main__":
  main()
