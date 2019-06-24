"""Linkedin Data API.

https://developer.linkedin.com/docs/guide/v2
"""


class LinkedInUserProfile(object):
  """Class for member profile.
  """
  pass


class LinkedInAPI(object):
  """Class for accessing Linkedin data.
  """
  _client_id = None
  _secret_id = None
  base_url = "https://api.linkedin.com/v1/people"

  def __init__(self, client_id, secret_id):
    self._client_id = client_id
    self._secret_id = secret_id


if __name__ == "__main__":
  pass