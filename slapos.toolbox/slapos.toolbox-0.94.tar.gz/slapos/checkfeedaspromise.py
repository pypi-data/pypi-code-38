# Command line script to test a RSS feed in a promise
# Checks that a given pattern can be found (or not) in the title or the
# description of the latest feed item.
# A time buffer option can be given, to determine if the emitter process is in
# a stalled state, in the case that no OK pattern has been found

import argparse
import datetime
import feedparser
import sys


def parseArguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('--feed-path', dest='feed_path',
                      help='Path or Url of the feed to search')
  parser.add_argument('--title', dest='title', action='store_true',
                      help='Patterns should be looked for in feed item\'s title')
  parser.add_argument('--description', dest='description', action='store_true',
                      help='Patterns should be looked for in feed item\'s description')
  parser.add_argument('--ok-pattern', dest='ok_pattern_list', action='append',
                      default=[],
                      help='If this pattern is found, then promise succeeds')
  parser.add_argument('--ko-pattern', dest='ko_pattern_list', action='append',
                      default=[],
                      help='If this pattern is found, then promise fails')
  parser.add_argument('--time-buffer', dest='time_buffer', type=int,
                      default=0,
                      help='Time delta in seconds before the promise really succeeds or fails')
  return parser.parse_args()


def containsPattern(string, pattern_list):
  for pattern in pattern_list:
    if string.find(pattern) >= 0:
      return True
  return False


def checkFeedAsPromise(feed, option):
  feed = feedparser.parse(feed)

  if feed.bozo:
    return 'Feed malformed : %s (at line %s)' % (
      feed.bozo_exception.getMessage(),
      feed.bozo_exception.getLineNumber(),
    )

  if len(feed.entries) == 0:
    return ''

  last_item = feed.entries[-1]
  if option.title:
    candidate_string = last_item.title
  elif option.description:
    candidate_string = last_item.description
  else:
    return 'At least one in [--title|--description] should be provided'

  publication_date = datetime.datetime(*last_item.published_parsed[:7])
  publication_age = datetime.datetime.now() - publication_date
  time_buffer = datetime.timedelta(seconds=option.time_buffer)

  ok_pattern_found = containsPattern(candidate_string, option.ok_pattern_list)
  ko_pattern_found = containsPattern(candidate_string, option.ko_pattern_list)

  if ok_pattern_found and ko_pattern_found:
    return 'Both OK and KO patterns found: please check arguments'

  # Expectations fulfilled
  if ok_pattern_found:
      return ''

  if ko_pattern_found:
    return ("At least one of the failure patterns (%s) "
            "has been found in the last status (%s)" % (option.ko_pattern_list, candidate_string))

  if not ok_pattern_found:
    if publication_age < time_buffer:
      # We have to wait for buffer to expire
      return ''
    else:
      # If time-buffer is out, we are in stalled state
      return 'Stalled situation : Last update (%s) happened on %s' % (candidate_string, publication_date)

  # If not ok, and not stalled, what can have possibly happen ?
  return 'Something went wrong, check promise code'


def main():
  option = parseArguments()
  result = checkFeedAsPromise(option.feed_path, option)

  if len(result) > 0:
    sys.exit(result)
  else:
    sys.exit(0)


if __name__ == '__main__':
  main()
