"""Robinhood api.

https://github.com/sanko/Robinhood
"""

import json
import requests


# TODO: api not working.
class RobinhoodAPI(object):
  """Class for Robinhood API (unofficial).
  """

  def __init__(self, username=None, password=None):
    self.token = None
    if username is None or password is None:
      print(
          "You need to provide username and password to authenticate. Sign up an account on Robinhood."
      )
    else:
      return
      req_url = "https://api.robinhood.com/oauth2/token/"
      res = requests.post(req_url, {
          "username": username,
          "password": password
      })
      res.raise_for_status()
      self.token = res.json()["token"]

  def get_fundamentals(self, company_symbols):
    """Get fundemantal data of given companies.
    """
    req_url = "https://api.robinhood.com/fundamentals/?symbols="
    for symbol in company_symbols:
      req_url += symbol + ","
    # remove last comma
    req_url = req_url[:-2]
    res = requests.get(req_url)
    res.raise_for_status()
    print(res.json())


if __name__ == "__main__":
  api = RobinhoodAPI("flyfengjie@gmail.com", "detective3!")
  api.get_fundamentals(["MSFT", "FB", "TSLA"])
