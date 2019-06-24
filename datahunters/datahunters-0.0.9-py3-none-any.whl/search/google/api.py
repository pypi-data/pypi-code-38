"""Google api class.
"""

import urllib

from datahunters.shared.selenium_scraper import SeleniumScraper
from datahunters.search.common import ImgSearchObject


class GoogleImageAPI(SeleniumScraper):
  """Class for google image search api.
  """
  base_url = "https://www.google.com/search"

  def __init__(self, use_headless=True):
    super().__init__(use_headless)
    print("Google image api initialized")

  def convert_elem_to_obj(self, elem):
    """Convert page element to image object.
    """
    cur_res = ImgSearchObject()
    link = self.get_attribute_values([elem], "href")[0]
    link = urllib.parse.unquote(link)
    cur_res.img_url = link[link.find("imgurl=") + 7:link.find(
        "&imgrefurl")].rstrip(".")
    return cur_res

  def scrape(self, keywords, get_all=False):
    """Collect images from google search results.

    Args:
      keywords: search input.
      item_num: number of items to retrieve.
      offset: offset for results to start.

    Returns:
      list of image items.
    """
    all_res = []
    try:
      print("start scraping '{}' using Google".format(keywords))
      formatted_keywords = keywords.strip().replace(" ", "+")
      req_url = "{}?q={}&source=lnms&tbm=isch&sa=X&ei=0eZEVbj3IJG5uATalICQAQ&ved=0CAcQ_AUoAQ&biw=939&bih=591".format(
          self.base_url, formatted_keywords)
      # check default page.
      print("checking default data")
      if not get_all:
        self.load_content(req_url)
        elems = self.find_elements("a.rg_l")
      else:
        elems = self.scrape_inf_scroll(
            req_url, "a.rg_l", None, load_btn_selector="input#smb")
      print("total fetched items: {}".format(len(elems)))
      for elem in elems:
        try:
          cur_res = self.convert_elem_to_obj(elem)
          all_res.append(cur_res)
        except Exception as ex:
          print("error in processing item: {}".format(ex))
          continue
      print("Google image scraping finished.")
      return all_res
    except Exception as ex:
      print("error in Google image scraper: {}".format(ex))
      return all_res
