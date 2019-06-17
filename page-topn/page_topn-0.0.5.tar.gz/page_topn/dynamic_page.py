import time
from selenium import webdriver
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from page_topn.service.configs import set_driver
class Dynimic_process():
    enterprise_source_table = "dict_tmp_hz_qy_name"
    enterprise_list = []
    def __init__(self,driver_path):
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--headless")
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument("--no-sandbox")
        # self.client = webdriver.Chrome(executable_path="./chromedriver",chrome_options=chrome_options)
        self.client = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

        dispatcher.connect(self.spider_closed,signals.spider_closed)



    def spider_closed(self):
        self.client.quit()

    def start_requests(self,url):
        self.client.get(url)
        time.sleep(1)
        return self.client.page_source


if __name__ == "__main__":
    Dynimic_process().start_requests(url="http://zfcg.wlmq.gov.cn/infopublish.do?method=infoPublishView&infoid=89780E928AE02608E05311C410AC3412")
