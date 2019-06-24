"""Scraper for instagram.
"""

import datetime
import json
import requests
from tqdm import tqdm
import concurrent.futures


class InstagramUser(object):
  """User class.
  """

  def __init__(self):
    self.user_id = ""
    self.username = ""
    self.fullname = ""
    self.profile_img_url = ""
    self.num_posts = 0
    self.num_followers = 0
    self.num_following = 0
    self.bio = ""
    self.is_verified = False
    self.is_private = False

  def to_json(self):
    return json.loads(json.dumps(self.__dict__))


class InstagramPost(object):
  """Class of an Instagram post.
  """

  def __init__(self):
    self.post_id = ""
    self.account_id = ""
    self.caption = ""
    self.post_date = ""
    self.num_likes = 0
    self.num_comments = 0
    self.img_url = ""
    self.img_width = 0
    self.img_height = 0
    self.vid_url = ""
    self.comments = []
    self.tags = []
    self.location = None

  def __str__(self):
    return "post: {}, published at: {}, img: {}, h: {}, w: {}".format(
        self.post_id, self.post_date, self.img_url, self.img_width,
        self.img_height)

  def to_json(self):
    return json.loads(json.dumps(self.__dict__))


class InstagramAPI(object):
  """Class for Instagram data.
  """

  def __init__(self):
    self.engine = None
    self.base_url = "https://www.instagram.com/"

  def convert_raw_post(self, raw_post):
    """Converting raw post json to object.

    The post json corresponds to edge node.
    """
    post = InstagramPost()
    post.account_id = raw_post["owner"]["id"]
    post.img_url = raw_post["display_url"]
    post.img_width = raw_post["dimensions"]["width"]
    post.img_height = raw_post["dimensions"]["height"]
    post.num_likes = raw_post["edge_media_preview_like"]["count"]
    post.num_comments = raw_post["edge_media_to_comment"]["count"]
    post.post_date = datetime.datetime.fromtimestamp(
        int(raw_post["taken_at_timestamp"])).isoformat()
    post.post_id = raw_post["id"]
    post.caption = raw_post["edge_media_to_caption"]["edges"][0]["node"][
        "text"]
    return post

  def get_user_posts(self, username, only_img=True, start_stamp=""):
    """Fetch user post.

    Returns:
      a generator for user post.
    """
    user_info = self.get_user_info(username)
    end_cursor = start_stamp
    while True:
      # request one page.
      MEDIA_URL = "{}graphql/query/?query_id=17888483320059182&id={}&first=100&after={}".format(
          self.base_url, user_info.user_id, end_cursor)
      res = requests.get(MEDIA_URL).json()
      if res["status"] == "ok":
        res_data = res["data"]["user"]["edge_owner_to_timeline_media"]
        page_info = res_data["page_info"]
        post_data = res_data["edges"]
        for raw_post in post_data:
          raw_post = raw_post["node"]
          if only_img and raw_post["is_video"]:
            continue
          cur_post = self.convert_raw_post(raw_post)
          yield cur_post
        if page_info["has_next_page"]:
          end_cursor = page_info["end_cursor"]
        else:
          break
      else:
        break

  def get_user_info(self, username):
    """Get information about a user.
    """
    USER_URL = "{}{}/?__a=1".format(self.base_url, username)
    res = requests.get(USER_URL).json()
    user_info = res["user"]
    cur_user = InstagramUser()
    cur_user.user_id = user_info["id"]
    cur_user.username = user_info["username"]
    cur_user.fullname = user_info["full_name"]
    cur_user.bio = user_info["biography"]
    cur_user.is_private = user_info["is_private"]
    cur_user.is_verified = user_info["is_verified"]
    cur_user.num_following = user_info["follows"]["count"]
    cur_user.num_followers = user_info["followed_by"]["count"]
    cur_user.profile_img_url = user_info["profile_pic_url_hd"]
    cur_user.num_posts = user_info["media"]["count"]
    return cur_user


if __name__ == "__main__":
  scraper = InstagramAPI()
  media = scraper.get_user_posts("livecandid")
  print next(media)
  print next(media)
