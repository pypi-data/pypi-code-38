"""Tests for Adobe Stock API.
"""

import json

from datahunters.stock.adobe.api import AdobeStockAPI


class TestAdobeStockAPI(object):
  """Class for tests.
  """

  def init(self):
    with open("configs.json", "r") as f:
      configs = json.load(f)
    self.api = AdobeStockAPI(configs["api_key"])

  def test_get_imgs(self):
    self.init()
    img_gen2 = self.api.get_imgs()
    assert next(img_gen2).img_id != ""

  def test_search_imgs(self):
    self.init()
    img_gen = self.api.search_imgs("cats in hat")
    assert next(img_gen).img_id != ""
