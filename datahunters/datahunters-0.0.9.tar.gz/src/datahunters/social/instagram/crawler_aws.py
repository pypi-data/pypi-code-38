"""Crawl instagram data and save to aws.
"""

import datetime
import json
import os
import time

from tqdm import tqdm
import concurrent.futures

import owl
from owl.data import img_tools
from owl.third.aws import aws

import instagram_scraper

logger_name = "instagram_crawler_logger"
logger = owl.data.common.get_logger(
    logger_name, os.path.join("extra", logger_name + ".log"))


class InstagramCrawlerAWS(instagram_scraper.InstagramScraper):
  """Class for crawling instagram data.
  """
  table_name = "data___instagram"

  def __init__(self):
    instagram_scraper.InstagramScraper.__init__(
        self,
        media_metadata=True,
        media_types=[],
        include_location=True,
        comments=False,
        destination="./",
        maximum=0)

  def init(self):
    """Init db.
    """
    try:
      self.db_config = json.load(open("./configs/aws_db_config.json", "r"))
      self.aws_man = aws.AWSIO(
          access_key=self.db_config["access_key"],
          secret_key=self.db_config["secret_access_key"],
          region=self.db_config["region"])
      self.aws_man.s3_man.use_bucket(bucket_name=self.db_config["s3_bucket"])
      logger.info("using s3 bucket: {}".format(self.db_config["s3_bucket"]))
      self.aws_man.dynamodb_man.create_table(self.table_name, "item_id", None,
                                             10, 10)
    except Exception as ex:
      logger.error("init db error: {}".format(ex.message))
      raise

  def crawl_user(self, username, last_time_stamp=None):
    """Scrape media for a user and return json results.
    """
    logger.info("start crawling {}".format(username))

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    if last_time_stamp is not None:
      self.last_scraped_filemtime = last_time_stamp
    self.posts = []
    self.last_scraped_filemtime = 0
    future_to_item = {}

    # Get the user metadata.
    user = self.fetch_user(username)
    logger.info("fetched user")

    if user:
      self.get_profile_pic(None, executor, future_to_item, user, username)
      self.get_stories(None, executor, future_to_item, user, username)
    logger.info("processed user.")

    # crawl metadata.
    if self.include_location:
      media_exec = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    iter_num = 0
    for item in tqdm(
        self.media_gen(username),
        desc='Searching {0} for posts'.format(username),
        unit=' media',
        disable=self.quiet):
      try:
        if self.include_location:
          media_exec.submit(self._InstagramScraper__get_location, item)

        if self.comments:
          item['comments']['data'] = list(
              self.query_comments_gen(item['code']))

        if self.media_metadata or self.comments or self.include_location:
          self.posts.append(item)

        # save item to aws.
        self.save_item(item)

        iter_num = iter_num + 1
        if self.maximum != 0 and iter_num >= self.maximum:
          break
      except Exception as ex:
        logger.error("error fetching item: {}".format(ex.message))

    self.logout()
    # self.save_json(self.posts, '{0}/{1}.json'.format(dst, username))
    logger.info("finish crawling {}".format(username))

  def save_item(self, item):
    """Save a given item to aws.
    """
    # check if already exists.
    res = self.aws_man.dynamodb_man.get_item({"item_id": item["id"]})
    if res is not None:
      return

    save_date = datetime.datetime.now().isoformat()
    if item["type"] != "image":
      return
    # construct object.
    es_item = {}
    es_item["item_id"] = item["id"]
    es_item["crawl_date"] = save_date
    es_item["account"] = item["user"]["username"]
    es_item["original_id"] = item["id"]
    es_item["link"] = item["link"]
    if item["location"] and "slug" in item["location"]:
      es_item["location"] = item["location"]["slug"]
    if "tags" in item:
      es_item["tags"] = item["tags"]
    es_item["likes"] = item["likes"]["count"]
    if item["caption"] and "text" in item["caption"]:
      es_item["caption"] = item["caption"]["text"]
    es_item["raw_metadata"] = json.dumps(item)
    img_info = item["images"]["standard_resolution"]
    es_item["img_url"] = img_info["url"]
    es_item["img_width"] = img_info["width"]
    es_item["img_height"] = img_info["height"]

    # upload the image data to aws.
    img_url = item["urls"][0]
    # download image.
    startt = time.time()
    img_bin, img_ext = img_tools.download_img_from_url(img_url)
    print "download image time: {}s".format(time.time() - startt)
    saved_img_url = self.aws_man.s3_man.upload_img_bin_as_file(
        self.db_config["s3_bucket"], img_bin, img_ext)
    print "save image time: {}s".format(time.time() - startt)
    es_item["raw_img_url"] = saved_img_url
    es_item["img_format"] = img_ext

    # add to db.
    startt = time.time()
    self.aws_man.dynamodb_man.add_item(es_item)
    print "save dynamodb time: {}s".format(time.time() - startt)


def run():
  crawler = InstagramCrawlerAWS()
  crawler.init()

  with open("./configs/targets.json", "r") as f:
    metadata = json.load(f)
  usernames = metadata["users"]
  for username in usernames:
    crawler.crawl_user(username)


if __name__ == "__main__":
  run()
