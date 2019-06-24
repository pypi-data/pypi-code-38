"""Tests for scraper.
"""

import json

from scraper import ShopStyleParams, ShopStyleScraper


class TestScraper(object):
  def __init__(self):
    with open("configs/config.json", "r") as f:
      configs = json.load(f)
    self.api_key = configs["api_key"]

  def test_cat(self):
    params = ShopStyleParams()
    my_scraper = ShopStyleScraper(self.api_key)
    cats = my_scraper.get_categories()
    print cats
    assert True