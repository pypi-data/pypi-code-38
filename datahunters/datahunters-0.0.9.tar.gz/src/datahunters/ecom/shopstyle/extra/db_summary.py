"""Compute summary of data in database.
"""

import json
import pymongo


def run_summary():
  """Compute statistics of the database.
  """
  # parse config.
  configs = json.load(open("config.json", "r"))
  # make connection.
  db_client = pymongo.MongoClient("mongodb://localhost:27017")
  database = db_client[configs["db_name"]]
  collection = database[configs["collection_name"]]
  collection.create_index("category")
  # get a list of categories.
  categories = collection.distinct("category")
  print categories
  # compute product number for each category.
  product_stats = {}
  for cate in categories:
    cate_count = collection.find({"category": cate}).count()
    product_stats[cate] = cate_count
    print "{}: {}".format(cate, cate_count)


if __name__ == "__main__":
  run_summary()
