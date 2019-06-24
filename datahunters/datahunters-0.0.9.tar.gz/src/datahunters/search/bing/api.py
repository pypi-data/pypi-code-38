"""Google api class.
"""

import json

from datahunters.shared.selenium_scraper import SeleniumScraper
from datahunters.search.common import ImgSearchObject


class BingImageAPI(SeleniumScraper):
  """Class for google image search api.
  """
  base_url = "https://www.bing.com/images/search"

  def __init__(self, use_headless=True):
    super().__init__(use_headless)
    print("Bing image api initialized")

  def scrape(self, keywords, get_all=False):
    all_res = []
    try:
      print("start scraping {} using Bing".format(keywords))
      formatted_keywords = keywords.strip().replace(" ", "+")
      req_url = "{}?q={}&qs=n&form=QBILPG&sp=-1&sc=8-3&sk=&cvid=1B063871C36E42438CC99549B92CD76D".format(
          self.base_url, formatted_keywords)
      if get_all:
        elems = self.scrape_inf_scroll(
            req_url, "a.iusc", "a.iusc", load_btn_selector="a.btn_seemore")
      else:
        self.load_content(req_url)
        elems = self.find_elements("a.iusc")
      print("total fetched items: {}".format(len(elems)))
      for elem in elems:
        try:
          # create result object.
          cur_res = ImgSearchObject()
          raw_data = self.get_attribute_values([elem], "m")[0]
          # parse link.
          parsed_data = json.loads(raw_data)
          cur_res.img_url = parsed_data["murl"]
          all_res.append(cur_res)
        except Exception as ex:
          print("error in processing item: {}".format(ex))
          continue
      print("Bing image scraping finished.")
      return all_res
    except Exception as ex:
      print("error in Bing image scraper: {}".format(ex))
      return all_res


if __name__ == "__main__":
  api = BingImageAPI()
  # warm up
  all_imgs = api.scrape("cats", False)
  all_imgs = api.scrape("dental xray", True)
  print("scrape finished.")
