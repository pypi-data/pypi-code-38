"""Image crawler for ShopStyle on aws dynamodb.
"""

import datetime
import json
import os
import requests
import time
import urllib

import multiprocessing
from tqdm import tqdm

import objectpath

import owl
from owl.data import img_tools
from owl.third.aws import dynamodb, s3

# create logger.
logger_name = "crawler_logger"
if not os.path.exists("extra"):
  os.mkdir("extra")
logger = owl.data.common.get_logger(logger_name,
                                    os.path.join("extra",
                                                 logger_name + ".log"))


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
  # db or file.
  save_type = "db"

  def get_request_url(self):
    """Form url for request.
    """
    return self.base_url + self.product_url + '?pid=' + self.pid + \
        '&cat=' + self.cat + '&format=' + self.format + \
        '&offset=' + self.offset + '&limit=' + self.page_limit + "&fl=" + self.retailer_id


class ShopStyleCrawlerAWS(object):
  """Crawler for shopstyle.

  Metadata is saved to dynamodb.
  Images are saved to s3.
  """
  db_config = None
  dynamodb_man = None
  s3_man = None
  table_name = "eyestyle.eloquii.shopstyle"

  def init(self):
    """Initialize database.

    Load configuration and create/get table.
    """
    try:
      self.db_config = json.load(open("./configs/aws_db_config.json", "r"))
      self.dynamodb_man = dynamodb.DynamoDBIO(
          access_key=self.db_config["access_key"],
          secret_key=self.db_config["secret_access_key"],
          region=self.db_config["region"])
      self.s3_man = s3.S3IO(
          access_key=self.db_config["access_key"],
          secret_key=self.db_config["secret_access_key"],
          region=self.db_config["region"])
      self.s3_man.use_bucket(bucket_name=self.db_config["s3_bucket"])
      logger.info("using s3 bucket: {}".format(self.db_config["s3_bucket"]))
      self.dynamodb_man.create_table(self.table_name, "item_id", None, 10, 10)
    except Exception as ex:
      logger.error("init db error: {}".format(ex.message))
      raise

  def save_item_to_db(self, original_id, img_url, item_metadata, sparams):
    """Save item to dynamodb.

    Args:
      original_id: id from the data source.
      img_url: product img url.
      sparams: parameters.
      item_metadata: metadata for the item.
    """
    try:
      item_id = "{}___shopstyle".format(original_id)

      # check if already exists.
      res = self.dynamodb_man.get_item({"item_id": item_id})
      if res is not None:
        return

      # req_data = requests.get(product_img_url, headers=header)
      startt = time.time()
      img_bin, img_ext = img_tools.download_img_from_url(img_url)
      saved_img_url = self.s3_man.upload_img_bin_as_file(
          self.db_config["s3_bucket"], img_bin, img_ext)
      print("save image time: {}".format(time.time() - startt))

      # add to db.
      save_date = datetime.datetime.now().isoformat()
      target_item = {
          "item_id": item_id,
          "original_id": original_id,
          "data_source": "shopstyle",
          "date": save_date,
          "category": item_metadata["categories"][0]["id"],
          "img_url": saved_img_url,
          "img_width": -1,
          "img_height": -1,
          "img_format": img_ext,
          "in_stock": item_metadata["inStock"],
          "raw_metadata": json.dumps(item_metadata)
      }
      target_item["brand"] = objectpath.Tree(item_metadata).execute(
          "$.brand.name")

      startt = time.time()
      self.dynamodb_man.add_item(target_item)
      print("save dynamodb time: {}s".format(time.time() - startt))
    except Exception as ex:
      logger.error("error in saving to db: {}".format(ex.message))

  def retrieve_items(self, items, sparams):
    """Retrieve items from api response.

    Args:
      items: product items to save.
      sparams: request parameters.
    """
    # create db item.
    for item in tqdm(items):
      try:
        #print('processing {}th product'.format(cnt))
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
            self.save_item_to_db(original_id, product_img_url, item, sparams)
            use_color = True

        # just use one image.
        if not use_color:
          if "image" not in item:
            return
          product_img_id = item["image"]["id"]
          original_id = "{}__{}".format(product_id, product_img_id)
          product_img_url = item["image"]["sizes"]["Original"]["url"]
          self.save_item_to_db(original_id, product_img_url, item, sparams)

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
          self.retrieve_items(res_json["products"], params)

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
    crawler = ShopStyleCrawlerAWS()
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
    cate_fn = "./shopstyle_categories.json"
    cate_data = json.load(open(cate_fn, 'r'))
    cates = []
    for gender in cate_data:
      for cate in cate_data[gender]:
        for subcate in cate["sub"]:
          cates.append(subcate["id"])
    # start processing.
    num_cores = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=num_cores)
    pool.map(crawl_one_cate_per_process, cates)
    logger.info("completed crawl.")
  except Exception as ex:
    logger.error("error in main parallel crawler: {}".format(ex.message))


def run_crawler_single():
  """Run crawler in single process.
  """
  try:
    logger.info("crawler started...")
    crawler = ShopStyleCrawlerAWS()
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
    crawler = ShopStyleCrawlerAWS()
    crawler.init()
    sparams = ShopStyleParams()
    sparams.retailer_id = retailer
    crawler.crawl(sparams)
    logger.info("completed crawl.")
  except Exception as ex:
    logger.error("main exception: {}".format(ex.message))


if __name__ == "__main__":
  # while True:
  #   run_crawler_parallel()
  #   time.sleep(10)
  run_crawler_retailer("r2001")