"""Tests for google image search.
"""

from datahunters.search.google.api import GoogleImageAPI


class TestGoogleAPI(object):
  """Test class.
  """

  def test_simple_scrape(self):
    """Test scraping default page.
    """
    engine = GoogleImageAPI()
    all_imgs = engine.scrape("cats", False)
    assert len(all_imgs) > 0

  def test_inf_scroll_scrape(self):
    """Test full scrape with infinite scrolling.
    """
    engine = GoogleImageAPI()
    all_imgs = engine.scrape("cats", True)
    assert len(all_imgs) > 0
