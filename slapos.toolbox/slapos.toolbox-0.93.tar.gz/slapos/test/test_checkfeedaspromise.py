import datetime
import feedparser
import time
import unittest

import PyRSS2Gen as RSS2

from slapos.checkfeedaspromise import checkFeedAsPromise

class Option(dict):
    def __init__(self, **kw): 
        self.__dict__.update(kw)
    def __setitem__(i, y):
        self.__dict__[i] = y

class TestCheckFeedAsPromise(unittest.TestCase):
  def getOptionObject(self, **kw):
    """
    Returns an object containing options as properties, to simulate a call
    to the tested script
    """
    option = {
      'title': False,
      'description': False,
      'time_buffer': 0,
      'ok_pattern_list': [],
      'ko_pattern_list': [],
    }
    option.update(kw)
    return Option(**option)


  def generateFeed(self, item_list):
    return RSS2.RSS2(
      title="Feed Title",
      link="http://exemple.com",
      description="Feed Description",
      items=[RSS2.RSSItem(**item) for item in item_list]
    ).to_xml()


  def generateOKFeed(self, extra_item_list=None):
    item_list = [{
      'title': 'Doing Something',
      'description': 'work work work',
      'pubDate': datetime.datetime.now(),
      }, {
      'title': 'Something Finished: OK',
      'description': 'OK FINISHED DONE BASTA',
      'pubDate': datetime.datetime.now(),
    }]
    if isinstance(extra_item_list, list):
      item_list.append(extra_item_list)
    return self.generateFeed(item_list)


  def generateKOFeed(self, extra_item_list=None):
    item_list = [{
      'title': 'Doing Something',
      'description': 'work work work',
      'pubDate': datetime.datetime.now(),
      }, {
      'title': 'Something Finished: Error',
      'description': 'FAILURE oops Arghh',
      'pubDate': datetime.datetime.now(),
    }]
    if isinstance(extra_item_list, list):
      item_list.extend(extra_item_list)
    return self.generateFeed(item_list)


  def test_ifOKFoundNoErrorReturned(self):
    option = self.getOptionObject()
    option.title = True
    feed = self.generateOKFeed()

    option.ok_pattern_list = ['OK']
    self.assertEqual(checkFeedAsPromise(feed, option), "")
    option.title, option.description  = False, True
    option.ok_pattern_list = ['DONE', 'OK']
    self.assertEqual(checkFeedAsPromise(feed, option), "")


  def test_ifKOFoundErrorReturned(self):
    option = self.getOptionObject()
    option.title = True
    feed = self.generateKOFeed()

    option.ko_pattern_list = ['Error']
    self.assertNotEquals(checkFeedAsPromise(feed, option), "")
    option.title, option.description  = False, True
    option.ko_pattern_list = ['FAILURE', 'Error']
    self.assertNotEquals(checkFeedAsPromise(feed, option), "")


  def test_ifNoOKPatternFoundErrorIsRaised(self):
    option = self.getOptionObject()
    option.title = True
    feed = self.generateKOFeed()

    # If no time buffer, then not OK is always wrong
    option.ok_pattern_list = ['OK']
    self.assertNotEquals(len(checkFeedAsPromise(feed, option)), 0)

    # if time buffer, then not OK is wrong only after buffer expires
    extra_item = {
      'title': 'Something is Starting',
      'description': 'Very long operation, but should last less than 1h',
      'pubDate': datetime.datetime.now() - datetime.timedelta(seconds=3600),
    }
    feed = self.generateKOFeed([extra_item,])
    option.time_buffer = 4000
    # buffer longer than last item's age
    self.assertEqual(checkFeedAsPromise(feed, option), "")

    # shorter buffer, we want to raise an error
    option.time_buffer = 1800
    self.assertNotEquals(len(checkFeedAsPromise(feed, option)), 0)


  def test_noItemInTheFeedIsNotAnError(self):
    option = self.getOptionObject()
    option.title = True
    
    feed = self.generateFeed([])
    self.assertEqual(checkFeedAsPromise(feed, option), "")


if __name__ == '__main__':
  unittest.main()
