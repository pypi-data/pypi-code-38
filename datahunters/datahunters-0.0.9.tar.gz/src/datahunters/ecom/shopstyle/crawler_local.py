"""Image crawler for ShopStyle api.
"""

import base64
import datetime
import json
import requests
import time
import urllib
import urllib2

import multiprocessing
from tqdm import tqdm

from owl.data import common
from owl.data import img_tools
from owl.data import mongo_manager

# create logger.
logger_name = "shopstyle_local_crawler_logger"
logger = common.get_logger(logger_name, logger_name + ".log")


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
  retailer_id = ""
  results_num = 100000
  img_save_dir = ""
  meta_save_dir = ""
  source_name = ""
  # db or file.
  save_type = "db"

  def get_request_url(self):
    """Form url for request.
    """
    return self.base_url + self.product_url + '?pid=' + self.pid + \
        '&cat=' + self.cat + '&format=' + self.format + \
        '&offset=' + self.offset + '&limit=' + self.page_limit + "&fl=" + self.retailer_id


class ShopStyleCrawlerLocal(object):
  """Crawler for shopstyle.

  Metadata is saved to mongodb.
  """
  db_name = "eloquii"  #"eyestyle_data"
  collection_name = "products"
  db_man = None
  index_exists = False

  def init(self):
    """Initialization.
    """
    try:
      # database.
      self.db_man = mongo_manager.MongoManager()
      self.db_man.connect(
          db_name=self.db_name, collection_name=self.collection_name)
      if self.db_man.collection.count() > 0:
        # check if index already exists.
        index_info = self.db_man.collection.index_information()
        if "item_id_1" in index_info:
          self.index_exists = True
          print("item_id index exists")
    except Exception as ex:
      logger.error("init error: {}".format(ex.message))
      raise

  def save_item_to_db(self, item_id, img_url, item_metadata, sparams):
    """Save item to mongodb.

    Args:
      item_id: item id.
      img_url: product img url.
      sparams: parameters.
      item_metadata: metadata for the item.
    """
    try:
      user_agent = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7"
      header = {'User-agent': user_agent}

      # check if already exists.
      res = self.db_man.query(attribute="item_id", value_list=[item_id])
      if len(res) > 0:
        return

      # req_data = requests.get(product_img_url, headers=header)
      startt = time.time()
      req_data = urllib2.Request(img_url, None, header)
      img_bin = urllib2.urlopen(req_data).read()
      img_base64 = base64.b64encode(img_bin)
      print("save image time: {}".format(time.time() - startt))
      now = datetime.datetime.now()
      save_date = "{}-{}-{}".format(now.year, now.month, now.day)
      new_item = {
          "item_id": item_id,
          "original_id": original_id,
          "date": save_date,
          "category": item_metadata["categories"][0]["id"],
          "img_data": img_base64,
          "in_stock": item_metadata["inStock"],
          "raw_metadata": json.dumps(item_metadata)
      }
      # add item to database.
      startt = time.time()
      self.db_man.add(new_item)
      # create index.
      if not self.index_exists:
        self.db_man.collection.create_index("item_id")
        logger.info("item_id index created.")
        self.index_exists = True
      print("save mongodb time: {}s".format(time.time() - startt))
    except Exception as ex:
      logger.error("error in saving to db: {}".format(ex.message))

  def par_retrieve_db(self, items, sparams):
    """Parallel retreive to save to database.

    Form item_id as productid__imgid___datasource

    Args:
      items: product items to save.
      sparams: request parameters.
    """
    to_debug = False

    # create db item.
    for item in tqdm(items):
      try:
        #print('processing {}th product'.format(cnt))
        product_id = str(item["id"])
        use_color = False
        if "colors" in item:
          # save all color versions.
          if to_debug:
            logger.info("{} colors found".format(len(item["colors"])))
          for color_item in item["colors"]:
            if "image" not in color_item:
              continue
            product_img_id = color_item["image"]["id"]
            item_id = "{}__{}___shopstyle".format(product_id, product_img_id)
            product_img_url = color_item["image"]["sizes"]["Original"]["url"]
            self.save_item_to_db(item_id, product_img_url, item, sparams)
            use_color = True

        # just use one image.
        if not use_color:
          if "image" not in item:
            return
          if to_debug:
            logger.info("not using color")
          product_img_id = item["image"]["id"]
          item_id = "{}__{}___shopstyle".format(product_id, product_img_id)
          product_img_url = item["image"]["sizes"]["Original"]["url"]
          self.save_item_to_db(item_id, product_img_url, item, sparams)

      except Exception as e:
        logger.error("error in shopstyle crawler: {}".format(e.message))

  def crawl(self, params):
    """Crawl products from api.

    Args:
      params: params for crawling.
    """
    try:
      # get total number.
      params.offset = "0"
      url = params.get_request_url()
      res_data = requests.get(url)
      res_json = json.loads(res_data.content)
      total_num = int(res_json["metadata"]["total"])
      total_num = min(params.results_num, total_num)
      logger.info("category {} has total {} products.".format(
          params.cat, total_num))
      page_num = max(1, total_num / int(params.page_limit))
      logger.info("total page number to fetch: {}".format(page_num))

      # make request for each page.
      for pid in range(page_num):
        try:
          logger.info("making api call for {} at page {}:{}".format(
              params.cat, pid + 1, page_num))
          cur_offset = int(params.page_limit) * pid
          if cur_offset > total_num:
            break
          params.offset = str(cur_offset)
          url = params.get_request_url()
          # make request.
          res_data = requests.get(url)
          res_json = json.loads(res_data.content)
        except Exception as ex:
          logger.error("error in response: {}".format(ex.message))
          continue

        # parse results.
        if len(res_json["products"]) == 0:
          logger.warning("empty response")
        else:
          self.par_retrieve_db(res_json["products"], params)

        # parse for api call
        time.sleep(3)
    except Exception as ex:
      logger.error("error in crawl: {}".format(ex.message))


def crawl_one_cate_per_process(cate):
  """Crawl one category in a standalone process.

    Args:
      cate: category name.
    """
  try:
    crawler = ShopStyleCrawlerLocal()
    crawler.init()
    sparams = ShopStyleParams()
    sparams.cat = cate
    crawler.crawl(sparams)
  except Exception as ex:
    logger.error("error crawl {}: ".format(cate, ex.messeage))


def run_crawler_parallel():
  """Run crawler in multiple processes.
  """
  try:
    logger.info("parallel crawler started...")
    # get category list.
    cate_fn = "shopstyle_categories.json"
    cate_data = json.load(open(cate_fn, 'r'))
    cates = []
    for gender in cate_data:
      for cate in cate_data[gender]:
        for subcate in cate["sub"]:
          cates.append(subcate["id"])
    # start processing.
    num_cores = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=num_cores / 2)
    pool.map(crawl_one_cate_per_process, cates[-4:])
    logger.info("completed crawl.")
  except Exception as ex:
    logger.error("error in main parallel crawler: {}".format(ex.message))


def run_crawler_single():
  """Run crawler in single process.
  """
  try:
    logger.info("crawler started...")
    crawler = ShopStyleCrawlerLocal()
    crawler.init()
    sparams = ShopStyleParams()
    cate_fn = "shopstyle_categories.json"
    cate_data = json.load(open(cate_fn, 'r'))
    cates = []
    for gender in cate_data:
      for cate in cate_data[gender]:
        for subcate in cate["sub"]:
          cates.append(subcate["id"])
    for cate in cates:
      sparams.cat = cate
      crawler.crawl(sparams)
    logger.info("completed crawl.")
  except Exception as ex:
    logger.error("main exception: {}".format(ex.message))


def run_crawler_retailer(retailer):
  """Run crawler in single process.
  """
  try:
    logger.info("crawler started...")
    crawler = ShopStyleCrawlerLocal()
    crawler.init()
    sparams = ShopStyleParams()
    sparams.retailer_id = retailer
    crawler.crawl(sparams)
    logger.info("completed crawl.")
  except Exception as ex:
    logger.error("main exception: {}".format(ex.message))


if __name__ == "__main__":
  run_crawler_retailer("r2001")
  # run_crawler_parallel()
  # while True:
  #   run_crawler_parallel()
  #   # wait for 10 seconds to start next.
  #   time.sleep(10)
