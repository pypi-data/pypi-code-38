"""Facebook graph api.
"""

import json
import requests

from datahunters.social.common import SocialUser
from datahunters.social.tools import gen_fb_token, gen_fb_token_nonexpired, unicode_normalize


class FBPost(object):
  """Class for facebook post.
  """

  def __init__(self):
    self.owner = ""

  def to_json(self):
    return json.loads(json.dumps(self.__dict__))


class FacebookAPI(object):
  """Class for Facebook graph api.
  """
  GRAPH_API_URL = "https://graph.facebook.com/"

  def __init__(self, fb_email=None, fb_pw=None, fb_token=None):
    if fb_token is None:
      assert fb_email is not None and fb_pw is not None
      self.fb_token = gen_fb_token(fb_email, fb_pw)
    else:
      self.fb_token = fb_token
    self.VERSION = "v2.12"
    self.test = None
    # subject specific property.
    self.page_fields = []
    self.post_fields = [
        "name", "id", "caption", "created_time", "description", "from",
        "full_picture", "link", "place", "type", "updated_time",
        "permalink_url", "shares",
        "reactions.type(LIKE).limit(0).summary(total_count).as(like)",
        "reactions.type(LOVE).limit(0).summary(total_count).as(love)",
        "reactions.type(WOW).limit(0).summary(total_count).as(wow)",
        "reactions.type(HAHA).limit(0).summary(total_count).as(haha)",
        "reactions.type(SAD).limit(0).summary(total_count).as(sad)",
        "reactions.type(ANGRY).limit(0).summary(total_count).as(angry)",
        "reactions.limit(0).summary(true)", "comments.limit(0).summary(true)"
    ]
    self.group_fields = ["cover", "email", "description"]
    self.user_fields = []

  """General graph api.
  """

  def get_object(self, obj_id, fields):
    """Retrieve graph object.
    """
    field_str = ""
    for field in fields:
      field_str += "{},".format(field)
    field_str = field_str.rstrip(",")
    url = "{}{}/{}?access_token={}&fields={}".format(
        self.GRAPH_API_URL, self.VERSION, obj_id, self.fb_token, field_str)
    res = requests.get(url).json()
    return res

  def get_edge(self, obj_id, edge, fields):
    """Retrieve edge related to an object.
    """
    field_str = ""
    for field in fields:
      field_str += "{},".format(field)
    field_str = field_str.rstrip(",")
    url = "{}{}/{}/{}?access_token={}&fields={}".format(
        self.GRAPH_API_URL, self.VERSION, obj_id, edge, self.fb_token,
        field_str)
    res = requests.get(url).json()
    return res

  def build_search_url(self, search_type, query):
    """Create a url for search request.
    """
    assert search_type in ["group", "user", "event", "place", "page"]
    url = "{}{}/search?access_token={}&q={}&type={}&limit=25".format(
        self.GRAPH_API_URL, self.VERSION, self.fb_token,
        query.replace(" ", "+"), search_type)
    return url

  """Group related code.
  """

  def search_groups(self, query):
    """Search groups and use as generator.
    """
    next_url = self.build_search_url("group", query)
    while next_url is not None:
      res = requests.get(next_url).json()
      if "next" in res["paging"]:
        next_url = res["paging"]["next"]
      else:
        next_url = None
      for group in res["data"]:
        # only public fields.
        group_obj = self.get_object(group["id"], self.group_fields)
        yield group_obj
    yield None

  def get_group(self, group_id):
    """Retrieve group object.
    """
    pass

  """User related code.
  """

  def search_users(self, query):
    """Search users.
    """
    next_url = self.build_search_url("user", query)
    while next_url is not None:
      res = requests.get(next_url).json()
      if "next" in res["paging"]:
        next_url = res["paging"]["next"]
      else:
        next_url = None
      for user in res["data"]:
        # only public fields.
        user_obj = self.get_object(user["id"], [])
        yield user_obj
    yield None

  def get_user(self, user_id):
    """Retrieve user information.
    """
    user = self.engine.get("/{}".format(user_id))
    return user

  def get_my_post(self, post_id):
    pass

  """Event related code.
  """

  def search_events(self, query):
    """Search events.
    """
    event_gen = self.engine.search(query, "event", True)

  """Page related code.
  """

  def search_pages(self, query):
    """Search pages.
    """
    next_url = self.build_search_url("page", query)
    while next_url is not None:
      res = requests.get(next_url).json()
      if "next" in res["paging"]:
        next_url = res["paging"]["next"]
      else:
        next_url = None
      for group in res["data"]:
        # only public fields.
        group_obj = self.get_object(group["id"],
                                    ["cover", "email", "description"])
        yield group_obj
    yield None

  def get_page_info(self, page_id):
    """Retrieve basic info about page.
    """
    pass

  def get_page_posts(self, page_id):
    """Retrieve all posts from a page.

    Args:
      page_id: name of the page from url.
    """
    res = self.get_edge(page_id, "posts", self.post_fields)
    next_url = "start"
    while next_url is not None:
      # get next url.
      if "paging" in res.keys():
        next_url = res["paging"]["next"]
      else:
        next_url = None
      # process posts.
      posts = res["data"]
      for post in posts:
        yield post

  """Post related code.
  """

  def get_post(self, post_id):
    """Retrieve info about post.
    """
    post = self.get_object(post_id, self.post_fields)
    return post


if __name__ == "__main__":
  token = gen_fb_token_nonexpired("2141139379235357",
                                  "6b1316b647bef3f306453a38d1b9e380")
  api = FacebookAPI(fb_token=token)
  # print api.__dict__
  post_gen = api.get_page_posts("BetterHQ")
  post = next(post_gen)
  print post
