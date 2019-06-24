"""Shopstyle scraper.
"""

import datetime
import json
import os
import requests
import time
import urllib

import objectpath


class ShopStyleParams(object):
  """Parameters for shopstyle api.
  """
  api_name = "ShopStyle"
  base_url = "http://api.shopstyle.com/"
  product_url = "api/v2/products"
  pid = "uid5625-32673475-18"
  format = "json"
  # keywords
  fts = ""
  cat = "category"
  offset = "0"
  page_limit = "50"
  results_num = 100000
  retailer_id = ""
  img_save_dir = ""
  meta_save_dir = ""
  source_name = ""

  def get_request_url(self):
    """Form url for request.
    """
    url = self.base_url + self.product_url + '?pid=' + self.pid + \
        '&cat=' + self.cat + '&format=' + self.format + \
        '&offset=' + self.offset + '&limit=' + self.page_limit
    if self.retailer_id != "":
      url += "&fl=" + self.retailer_id
    return url


class ShopStyleScraper(object):
  """Class for scraping shopstyle.
  """
  api_key = ""
  logger = None

  def __init__(self, api_key, logger=None):
    self.api_key = api_key
    self.logger = logger
    print("shopstyle scraper initiated.")

  def get_total_product_num(self, params):
    """Get total number of products under params.
    """
    try:
      params.api_key = self.api_key
      url = params.get_request_url()
      res_data = requests.get(url)
      res_json = json.loads(res_data.content)
      total_num = int(res_json["metadata"]["total"])
      total_num = min(params.results_num, total_num)
      return total_num
    except Exception as ex:
      print("error in getting product num: {}".format(ex.message))

  def get_categories(self):
    """Fetch all categories.
    """
    try:
      cat_url = "http://api.shopstyle.com/api/v2/categories?pid={}".format(
          self.api_key)
      res_data = requests.get(cat_url)
      res_json = json.loads(res_data.content)
      cats = res_json["categories"]
      return cats
    except Exception as ex:
      if self.logger:
        self.logger.error(ex.message)

  def get_brands(self):
    """Fetch all brands.
    """
    try:
      brand_url = "http://api.shopstyle.com/api/v2/brands?pid={}".format(
          self.api_key)
      res_data = requests.get(brand_url)
      res_json = json.loads(res_data.content)
      return res_json["brands"]
    except Exception as ex:
      if self.logger:
        self.logger.error(ex.message)

  def get_retailers(self):
    """Fetch all retailers.
    """
    try:
      retailer_url = "http://api.shopstyle.com/api/v2/retailers?pid={}".format(
          self.api_key)
      res_data = requests.get(retailer_url)
      res_json = json.loads(res_data.content)
      return res_json["retailers"]
    except Exception as ex:
      if self.logger:
        self.logger.error(ex.message)

  def create_item(self, original_id, img_url, item_metadata):
    """Create item with essential info.

    No item_id is specified.
    """
    save_date = datetime.datetime.now().isoformat()
    target_item = {
        "original_id": original_id,
        "data_source": "shopstyle",
        "scrape_date": save_date,
        "name": item_metadata["name"],
        "img_urls": [img_url],
        "product_link": item_metadata["clickUrl"],
        "in_stock": item_metadata["inStock"],
        "price": item_metadata["price"],
        "currency": item_metadata["currency"]
    }
    target_item["brand"] = objectpath.Tree(item_metadata).execute(
        "$.brand.name")
    target_item["retailer"] = objectpath.Tree(item_metadata).execute(
        "$.retailer.name")
    target_item["category"] = objectpath.Tree(item_metadata).execute(
        "$.categories[0].id")
    target_item["last_modified"] = objectpath.Tree(item_metadata).execute(
        "$.lastModified")
    # clean and remove none.
    for key, val in target_item.iteritems():
      if val is None:
        target_item[key] = "unknown"
    return target_item

  def retrieve_items(self, items, sparams):
    """Retrieve items from api response.

    Args:
      items: product items to save.
      sparams: request parameters.
    """
    new_items = []
    for item in items:
      try:
        product_id = str(item["id"])
        use_color = False
        if "color" in item:
          # save all color versions.
          for color_item in item["colors"]:
            if "image" not in color_item:
              continue
            product_img_id = color_item["image"]["id"]
            original_id = "{}__{}".format(product_id, product_img_id)
            product_img_url = color_item["image"]["sizes"]["Original"]["url"]
            new_item = self.create_item(original_id, product_img_url, item)
            new_items.append(new_item)
            use_color = True
        # just use one image.
        if not use_color:
          if "image" not in item:
            return
          product_img_id = item["image"]["id"]
          original_id = "{}__{}".format(product_id, product_img_id)
          product_img_url = item["image"]["sizes"]["Original"]["url"]
          new_item = self.create_item(original_id, product_img_url, item)
          new_items.append(new_item)
      except Exception as e:
        if self.logger:
          self.logger.error("error in shopstyle crawler: {}".format(e.message))

    return new_items

  def scrape_products(self, params):
    """Start scraping.

    Returns:
      scraped items for a page determined by offset.
    """
    all_items = []
    try:
      print("making api call for {} at page offset {}".format(
          params.cat, params.offset))
      url = params.get_request_url()
      res_data = requests.get(url)
      res_json = json.loads(res_data.content)
      # parse results.
      if len(res_json["products"]) == 0:
        print("empty response")
      else:
        items = self.retrieve_items(res_json["products"], params)
        all_items.extend(items)
    except Exception as ex:
      print(ex)

    return all_items


if __name__ == "__main__":
  with open("configs/config.json", "r") as f:
    configs = json.load(f)
  scraper = ShopStyleScraper(configs["api_key"])
  params = ShopStyleParams()
  print(scraper.get_brands())
