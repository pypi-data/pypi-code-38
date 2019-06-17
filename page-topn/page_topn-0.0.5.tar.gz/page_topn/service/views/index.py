import tornado.web
import docker
from page_topn.service.configs import settings
import datetime
from page_topn.pagetopn import page_topn
class IndexHandler(tornado.web.RequestHandler):

    def get(self,*args,**kwargs):
        url = self.get_argument("url")
        num = int(self.get_argument("num"))
        isdynamic = self.get_argument("isdynamic","n")
        driver_path = self.get_argument("driver_path","./chromedriver")
        if "n" in isdynamic:
            words = page_topn(url, num)
            self.write(str(words))

        elif "d" in isdynamic:

            words = page_topn(url, num,True,driver_path)
            self.write(str(words))