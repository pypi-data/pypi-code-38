# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging

import esgf_scraper.ext.dblite as dblite
from esgf_scraper.items import DatasetDetailItem, DatasetSearchItem
from esgf_scraper.sqlite import get_queue
from esgf_scraper.utils import print_items

logger = logging.getLogger(__name__)


class StoreItemsPipeline(object):
    def __init__(self):
        self.ds = None
        self.queue = None
        self.items = []

    def open_spider(self, spider):
        self.ds = dblite.open(DatasetSearchItem, autocommit=True)
        self.queue = get_queue("download_queue")

    def close_spider(self, spider):
        self.ds.close()
        if len(self.items):
            if "filename" in self.items[0]:
                cols = ["instance_id", "filename", "status"]
            else:
                cols = ["instance_id", "status"]
            print_items(self.items, cols=cols)

    def process_item(self, item, spider):
        if isinstance(item, DatasetSearchItem):
            res = self.process_search(item, spider)
            self.items.append(res)
        elif isinstance(item, DatasetDetailItem):
            self.process_esgf(item, spider)
        return item

    def process_esgf(self, item, spider):
        if spider.add:
            db_item = self.ds.get(
                criteria={"instance_id": item["instance_id"]}, limit=1
            )
            if db_item["verified_at"] is None:
                logger.info("Queuing {} for download".format(item["instance_id"]))
                d = dict(item)
                d["files"] = [dict(f) for f in d["files"]]
                self.queue.append(d)
        return dict(item)

    def process_search(self, item, spider):
        res = dict(item)
        res["status"] = "New"
        # Check to see if the file is already downloaded
        db_item = self.ds.get(criteria={"instance_id": res["instance_id"]}, limit=1)

        if db_item:
            if db_item["verified_at"] is None:
                res["status"] = "Added"
            else:
                res["status"] = "Downloaded"
        else:
            res["status"] = "New"

        if spider.add and res["status"] != "Downloaded":
            if not db_item:
                logger.info("Adding {} to database".format(item["instance_id"]))
                self.ds.put(item)
        return res
