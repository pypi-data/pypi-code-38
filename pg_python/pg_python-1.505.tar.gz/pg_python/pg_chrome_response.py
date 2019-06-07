from selenium.webdriver import Chrome
from scrapy.http.response.html import HtmlResponse
import logging

"""
Gathering the HTML response from chrome.
retries is equal to 3
"""

MAX_NUM_RETRY = 3


def get_response(url):
    num_retries = 0
    driver = None
    while num_retries < MAX_NUM_RETRY:
        try:
            driver = Chrome()
            driver.get(url)
            response = HtmlResponse(url=url, body=driver.page_source, encoding='utf-8')
            driver.close()
            return response
        except Exception as e:
            logging.error("Exception %s" % e)
            num_retries += 1
    logging.error("Could not fetch the url")
    if driver is not None:
        driver.close()


if __name__ == "__main__":
    response = get_response("https://google.com")
    print(response)