import collections
import datetime
import feedparser
import json
import os
import shutil
import tempfile
import time
import unittest

from slapos.generatefeed import generateFeed

class Option(dict):
    def __init__(self, **kw): 
        self.__dict__.update(kw)
    def __setitem__(i, y):
        self.__dict__[i] = y

class TestGenerateFeed(unittest.TestCase):
  def setUp(self):
    self.item_directory = tempfile.mkdtemp(dir='.')
    self.feed_path = os.path.join(self.item_directory, 'path')

  def tearDown(self):
    shutil.rmtree(self.item_directory)

  def getOptionObject(self, **kw):
    """
    Returns an object containing options as properties, to simulate a call
    to the tested script
    """
    option = {
      'output': self.feed_path,
      'status_item_path': self.item_directory,
      'max_item': 50,
      'feed_title': 'Feed title',
      'feed_link': 'http://example.com',
      'feed_description': 'Feed description',
    }
    option.update(kw)
    return Option(**option)

  def saveAsStatusItem(self, filename, content):
    """
    Save a JSON at filename in self.item_directory as a status item
    """
    path = os.path.join(self.item_directory, filename)
    with open(path, 'w') as status_file:
      status_file.write(json.dumps(content))

  def createItemSample(self):
    """
    Populate item_directory with a few sample items
    """
    item = [
      # Last in alphabet, first in pubDate
      ('zzz.item',
        {'description': 'description is OK too',
         'link': "http://example.com",
         'pubDate': time.mktime(datetime.datetime(2000, 1, 1).timetuple()),
         'title': 'everything is OK',
        }),
      # First in pubDate, last in alphabet 
      ('aaa.item',
        {'description': 'what went wrong ?',
         'link': "http://example.com",
         'pubDate': time.mktime(datetime.datetime(2000, 12, 31).timetuple()),
         'title': 'I guess we have an ERROR',
        }),
    ]
    for filename, content in item:
      self.saveAsStatusItem(filename, content)

  def test_feedItemsAreSortedByDate(self):
    self.createItemSample()
    option = self.getOptionObject()
    content_feed = generateFeed(option)
    feed = feedparser.parse(content_feed)

    self.assertFalse(feed.bozo)

    start_date = None
    for item in feed.entries:
      if start_date is None:
        start_date = item.published_parsed
      self.assertLessEqual(start_date, item.published_parsed)

  def test_generateFeedCleanStatusDirectoryIfTooManyItems(self):
    option = self.getOptionObject()
    option.max_item = 3

    # Creates items more than allowed
    item_dummy_content = {
      'description': 'dummy description',
      'link': "http://example.com",
      'pubDate': time.mktime(datetime.datetime.now().timetuple()),
      'title': 'dummy title',
    }
    for i in range(5):
      filename = '%s.item' % i
      self.saveAsStatusItem(filename, item_dummy_content)
      time.sleep(1)
      item_dummy_content['pubDate'] = time.mktime(datetime.datetime.now().timetuple())

    content_feed = generateFeed(option)
    feed = feedparser.parse(content_feed)

    self.assertFalse(feed.bozo)

    # Feed entries number should be limited
    self.assertEqual(len(feed.entries), option.max_item)

    # Status item directory should have been cleaned
    self.assertEqual(len(os.listdir(self.item_directory)), option.max_item)

    # Only "younger" items should still be there
    remaining_status_item_list = os.listdir(self.item_directory)
    expected_remaining_item_list = []

    for i in range(5-3, 5): # older items (from 1 to 2) have been deleted
      expected_remaining_item_list.append('%s.item' % i)

    self.assertItemsEqual(remaining_status_item_list,
                          expected_remaining_item_list)

if __name__ == '__main__':
  unittest.main()
