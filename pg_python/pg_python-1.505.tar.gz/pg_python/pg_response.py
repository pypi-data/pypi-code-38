import requests
from scrapy.http.response.html import HtmlResponse
from scrapy.http.response.xml import XmlResponse
import logging

"""
Response = HTMLReponse of requests.get
"""
MAX_NUM_RETRY = 3


def get_response(url, headers=None, cookies=None, delay=30, response_type="html"):
    num_retries = 0
    response = None
    if cookies is None:
        cookies = {}
    while num_retries < MAX_NUM_RETRY:
        try:
            response = None
            if headers is not None:
                response = requests.get(url, headers=headers,timeout=delay, verify=False, cookies=cookies)
            else:
                response = requests.get(url, timeout=delay, verify=False, cookies=cookies)
            num_retries += 1
            if response.status_code >= 200:
                if response_type == "html":
                  ret_obj = HtmlResponse(url, status=response.status_code, body=response.content, encoding='utf-8')
                  return ret_obj
                elif response_type == "xml":
                  ret_obj = XmlResponse(url, status=response.status_code, body=response.content, encoding='utf-8')
                  return ret_obj
                else:
                    raise Exception("Invalid response type")

        except Exception as e:
            logging.error("Exception %s" %e.message)
            num_retries += 1
    logging.error("Could not fetch the url")
    if response_type == "html":
        err_obj = HtmlResponse(url, status=110, body="<html><body>Failure</body></html>", encoding='utf-8')
    else:
        err_obj = XmlResponse(url, status=110, body="<html><body>Failure</body></html>", encoding='utf-8')
    return err_obj




if __name__ == "__main__":
    for i in range(0, 100):
        r = get_response('https://eprocure.gov.in/cppp/latestactivetenders', delay=60,response_type="html")
        logging.info(r.status)


