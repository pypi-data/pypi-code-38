"""Base api class.
"""

import abc
import json


class StockContent(object):
  """Class for a single stock content object.

  Example content: image, video, 3d model.
  """
  img_id = ""
  title = ""
  description = ""
  owner = ""
  created_date = ""
  full_url = ""
  normal_url = ""
  link = ""


class StockImageAPIBase(object):
  """Base class for stock image apis.
  """
  __metaclass__ = abc.ABCMeta

  def save_json_data(self, json_data, save_fn):
    """Save json to file.
    """
    with open(save_fn, "w") as f:
      json.dump(json_data, f)

  @abc.abstractmethod
  def search_imgs(self, keywords):
    """Search images using keywords.

    Args:
      keywords: descriptions of the topic.
      num: number of images to return.

    Returns:
      generator for continuously fetching images until None.
    """
    pass

  @abc.abstractmethod
  def get_imgs(self, start_page=-1):
    """Fetch images from the whole collection.

    Ordered by latest.

    Args:
      start_page: page number to start.

    Returns:
       generator for continuously fetching images until None.
    """
    pass
