"""Tests for bing image search.
"""

from datahunters.search.bing.api import BingImageAPI


class TestBingAPI(object):
  """Test class.
  """

  def test_simple_scrape(self):
    """Test scraping default page.
    """
    engine = BingImageAPI()
    all_imgs = engine.scrape("cats", False)
    assert len(all_imgs) > 0

  def test_inf_scroll_scrape(self):
    """Test full scrape with infinite scrolling.
    """
    engine = BingImageAPI()
    all_imgs = engine.scrape("cats", True)
    assert len(all_imgs) > 0
