"""Shared data structure for social data.
"""

import json


class SocialUser(object):
  """Class for user on social network.
  """

  def __init__(self):
    self.user_id = ""
    self.name = ""
    self.age = 0
    self.gender = ""
    # photo urls.
    self.photos = []
    self.custom = {}

  def to_json(self):
    return json.loads(json.dumps(self.__dict__))

  def __str__(self):
    return json.dumps(self.__dict__)


class SocialContent(object):
  """Basic piece of content.
  """

  def __init__(self):
    self.text = ""
    self.images = []
