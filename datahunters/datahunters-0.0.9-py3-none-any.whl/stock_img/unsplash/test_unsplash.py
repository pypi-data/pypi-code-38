"""Tests for unsplash api.
"""

import json

from datahunters.stock.unsplash.api import UnsplashAPI, UnsplashImage


class TestUnsplashAPI(object):
  """Class for testing api.
  """
  engine = None

  def init(self):
    with open("configs.json", "r") as f:
      configs = json.load(f)
    self.engine = UnsplashAPI(configs["api_key"])

  def test_get_imgs(self):
    self.init()
    imgs = self.engine.get_imgs(0, 30)
    assert len(imgs) == 30

  def test_search_imgs(self):
    self.init()
    imgs = self.engine.search_imgs("people")
    assert len(imgs) > 0

  def test_random_imgs(self):
    self.init()
    imgs = self.engine.get_random_imgs()
    assert len(imgs) > 0
