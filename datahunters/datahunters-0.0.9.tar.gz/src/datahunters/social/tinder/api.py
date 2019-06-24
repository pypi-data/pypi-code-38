"""Tinder api.
"""

import json

import pynder

from datahunters.social.common import SocialUser
from datahunters.social.tools import gen_fb_token


class TinderAPI(object):
  """API Class for Tinder.
  """
  # tinder session.
  engine = None

  def __init__(self, fb_email, fb_pw):
    try:
      fb_token = gen_fb_token(fb_email, fb_pw)
      self.engine = pynder.Session(fb_token)
      print("tinder api started")
    except Exception as ex:
      print("fail to create tinder api: {}".format(ex))

  def convert_to_socialuser(self, raw_user):
    """Convert api raw user to socialuser object.
    """
    user = SocialUser()
    user.name = raw_user.name
    user.photos = []
    for photo in raw_user.photos:
      user.photos.append(photo)
    user.age = raw_user.age
    user.gender = raw_user.gender
    user.custom["jobs"] = raw_user.jobs
    # school has problems
    user.custom["schools"] = raw_user.schools
    user.custom["distance_km"] = raw_user.distance_km
    user.custom["instagram"] = raw_user.instagram_username
    return user

  def get_profile(self):
    """Retrieve profile.
    """
    profile = self.engine.profile
    user = SocialUser()
    user.name = profile.name
    user.photos = profile.photos
    if profile.gender == 0:
      user.gender = "male"
    else:
      user.gender = "female"
    return user

  def candidate_generator(self):
    """Get candidate matches.

    Returns: generator of socialuser.
    """
    try:
      raw_users = self.engine.nearby_users()
      for raw_user in raw_users:
        try:
          user = self.convert_to_socialuser(raw_user)
          yield user
        except Exception as ex:
          print("candidate convertion error: {}".format(ex))
          continue
      yield None
    except Exception as ex:
      print("error in fetching candidate: {}".format(ex))
      yield None

  def get_existing_matches(self):
    """Get already matched users.
    """
    raw_matches = self.engine.matches()
    matches = []
    for raw_match in raw_matches:
      user = self.convert_to_socialuser(raw_match.user)
      matches.append(user)
    print("total {} matches found".format(len(matches)))
    return matches


if __name__ == "__main__":
  api = TinderAPI("flyfengjie@gmail.com", "detective3!")
  user_gen = api.candidate_generator()
  # api.get_existing_matches()
  cnt = 0
  while True:
    user = next(user_gen)
    if user is None:
      break
    # print user
    # print type(user)
    cnt += 1
    if cnt == 1:
      break
  # print cnt
