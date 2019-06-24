"""Base class for Selenium based scraper.

https://medium.com/@pyzzled/running-headless-chrome-with-selenium-in-python-3f42d1f5ff1d
"""

import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotVisibleException, WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from datahunters.assets.webdrivers.downloader import download_chrome_driver


class SeleniumElementSelectorType(object):
  """Define what element type can be used.
  """
  CSS = 0
  XPATH = 1
  ID = 2

  @staticmethod
  def check_validity(sel_type):
    assert sel_type in [
        SeleniumElementSelectorType.CSS, SeleniumElementSelectorType.ID,
        SeleniumElementSelectorType.XPATH
    ]


class ContentPageType(object):
  """Type of content page.
  """
  # numbered pagination
  PAGINATION = 0
  # infinite scrolling
  INF_SCROLL = 1
  # infinite scrolling with button click
  INF_SCROLL_WITH_BTN = 2


class SeleniumScraper(object):
  """Generic class for selenium based scraper.
  """

  def __init__(self, headless=True):
    """Initialization.

    Specify driver paths.
    """
    # webdriver path.
    self.chrome_driver_path = None
    # headless or not.
    self.use_headless = headless
    # browser object.
    self.browser = None

    cur_dir = os.path.dirname(os.path.abspath(__file__))
    self.chrome_driver_path = os.path.join(
        cur_dir, "../assets/webdrivers/chrome/chromedriver")
    if not os.path.exists(self.chrome_driver_path):
      download_chrome_driver()
    self.create_driver()

  def create_driver(self):
    """Create a new driver instance.
    """
    try:
      options = webdriver.ChromeOptions()
      options.add_argument(" - incognito")
      options.add_argument("--no-sandbox")
      options.add_argument("--proxy-server='direct://'")
      options.add_argument("--proxy-bypass-list=*")
      if self.use_headless:
        options.add_argument("--headless")
      self.browser = webdriver.Chrome(
          executable_path=self.chrome_driver_path, chrome_options=options)
    except WebDriverException as ex:
      print("error in creating chrome driver: {}".format(ex))
      # print("switching to firefox driver")

  def __del__(self):
    """Clean resources.
    """
    if self.browser:
      self.browser.quit()
      print("browser quit")

  def load_content(self,
                   url,
                   wait_elem_selector=None,
                   selector_type=SeleniumElementSelectorType.CSS):
    """Load page content.
    """
    startt = time.time()
    SeleniumElementSelectorType.check_validity(selector_type)
    self.browser.get(url)
    if wait_elem_selector:
      timeout = 20
      try:
        select_by = None
        if selector_type == SeleniumElementSelectorType.CSS:
          select_by = By.CSS_SELECTOR
        if selector_type == SeleniumElementSelectorType.ID:
          select_by = By.ID
        if selector_type == SeleniumElementSelectorType.XPATH:
          select_by = By.XPATH
        WebDriverWait(self.browser, timeout).until(
            EC.visibility_of_element_located((select_by, wait_elem_selector)))
      except TimeoutException:
        print("timed out")
        self.browser.quit()
    print("content loading time: {}s".format(time.time() - startt))

  def find_elements(self,
                    selector,
                    selector_type=SeleniumElementSelectorType.CSS,
                    visible=False):
    """Retrieve elements from current page.

    Args:
      visible: if require elements to be visible.

    Returns:
      list of element objects.
    """
    try:
      startt = time.time()
      if selector_type == SeleniumElementSelectorType.CSS:
        elements = self.browser.find_elements_by_css_selector(selector)
      if selector_type == SeleniumElementSelectorType.XPATH:
        elements = self.browser.find_elements_by_xpath(selector)
      if selector_type == SeleniumElementSelectorType.ID:
        elements = self.browser.find_elements_by_id(selector)
      print("find elements time: {}s".format(time.time() - startt))
      if visible:
        startt = time.time()
        new_elements = []
        for elem in elements:
          if elem.is_displayed():
            new_elements.append(elem)
        print("fill new elements: {}s".format(time.time() - startt))
        return new_elements
      else:
        return elements
    except Exception as ex:
      print("error finding elements: {}".format(ex))
      return []

  def get_attribute_values(self, elements, attribute_name):
    """Extract attribute values from given elements.
    """
    attr = []
    for elem in elements:
      attr.append(elem.get_attribute(attribute_name))
    return attr

  def scroll_to_bottom(self, load_wait_time=3):
    """Scroll current page to bottom.

    Args:
      load_wait_time: seconds to wait for page load.
    """
    # scroll to bottom.
    scroll_script = """window.scrollTo(0, document.body.scrollHeight); 
                       var page_len=document.body.scrollHeight;
                       return page_len;"""
    startt = time.time()
    cur_page_len = self.browser.execute_script(scroll_script)
    max_cnt = 10
    startt = time.time()
    for _ in range(max_cnt):
      last_page_len = cur_page_len
      time.sleep(load_wait_time)
      cur_page_len = self.browser.execute_script(scroll_script)
      if last_page_len == cur_page_len:
        print("scrolling time: {}s".format(time.time() - startt))
        break
    print("scrolled to bottom.")

  def scrape_inf_scroll(self,
                        url,
                        target_elem_selector,
                        wait_elem_selector=None,
                        load_btn_selector=None,
                        selector_type=SeleniumElementSelectorType.CSS):
    """scrape elements from an infinite scroll page.

    Args:
      url: target url.
      target_elem_selector: selector for target elements.
      wait_elem_selector: selector for element to wait to be loaded.
      load_elem_selector: selector for load element button.

    Returns:
      a list of target elements.
    """
    try:
      startt = time.time()
      print("start scraping infinite scrolling")
      # load initial page.
      if not wait_elem_selector:
        wait_elem_selector = target_elem_selector
      self.load_content(
          url,
          wait_elem_selector=wait_elem_selector,
          selector_type=selector_type)
      # scroll to bottom.
      self.scroll_to_bottom(0.5)
      if load_btn_selector:
        # repeat until no load_more button found and reach buttom.
        while True:
          # find load more button and click.
          load_btns = self.find_elements(load_btn_selector, selector_type,
                                         True)
          if load_btns:
            # click load more button.
            load_btns[0].click()
            print("clicked load more button")
            self.scroll_to_bottom(0.5)
          else:
            # no load more button is found.
            print("no more content available")
            break
      # fetch all elements.
      print("start to fetch target elements...")
      all_elems = self.find_elements(target_elem_selector, selector_type)
      print("{} elements found".format(len(all_elems)))
      print("total time: {}s".format(time.time() - startt))
      return all_elems
    except Exception as ex:
      print("error in scrape inf scroll: {}".format(ex))


class SeleniumScraperTester(object):
  def __init__(self):
    self.scraper = None
    self.scraper = SeleniumScraper()

  def test_scrape(self):
    url = "https://www.google.com.sg/search?q=car&source=lnms&tbm=isch&sa=X&ei=0eZEVbj3IJG5uATalICQAQ&ved=0CAcQ_AUoAQ&biw=939&bih=591"
    elems = self.scraper.scrape_inf_scroll(
        url, "a.rg_l", load_btn_selector="input#smb")
    print(len(elems))


if __name__ == "__main__":
  tester = SeleniumScraperTester()
  tester.test_scrape()
