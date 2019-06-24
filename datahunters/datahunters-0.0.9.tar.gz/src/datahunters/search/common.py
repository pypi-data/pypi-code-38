"""Shared definition for search engine api.
"""

import abc
import json


class ImgSearchObject(object):
  """Result object from image search.
  """
  thumbnail_url = None
  img_url = None
  link_url = None

  def to_json(self):
    """Convert to json.
    """
    return json.loads(json.dumps(self.__dict__))


class SearchEngineAPIBase(object):
  """Base class for search engine api.
  """
  __metaclass__ = abc.ABCMeta

  def __init__(self):
    pass

  def text_search(self, keywords):
    pass

  def img_search(self, keywords):
    pass
