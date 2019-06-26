import json
import os.path
import re
from datetime import datetime

import requests
from pytz import timezone
from news2play.web_downloader.clearning_tool import RemoveHTML
from news2play.web_downloader.ts_tools import Tool


class NewDownloader:
    def __init__(self, path="../storage/"):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"}
        self.remover = RemoveHTML()
        self.path = path
        self.fd = Tool(path)

    @staticmethod
    def download_pic(url, path):
        with open(path, 'wb') as f:
            f.write(requests.get(url).content)

    @staticmethod
    def validate_title(title):
        rstr = r"[\/\\\:\*\?\"\<\>\| ]"
        new_title = re.sub(rstr, "_", title)
        return new_title

    @staticmethod
    def get_est(timestamp):
        ts = datetime.fromtimestamp(timestamp)
        est = ts.astimezone(timezone('US/Eastern'))
        fdate = est.strftime('%Y-%m-%d %H:%M:%S')
        return fdate

    def parse_news(self, url):
        try:
            responses = requests.get(url, headers=self.headers)
            html = responses.content.decode()
            raw = re.findall("var articlejson =(.*?)\r\n", html)
            news = raw[0].replace(r"\r", "").strip(";")
            js = json.loads(news)
            title = js['story']['title']
            text = js['story']['text']
            text = re.sub("(?<=Equity'>).+?(?=<)", "", text)
            text = text.replace('&quot;', '"')
            autor = js['story']['byLine']
            timestamp = float(js["story"]['receivedTime']) / 1000
            # ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
            ts = self.get_est(timestamp)
            cleaned = self.cleaning(text)
            title = self.cleaning(title)
            path_name = self.validate_title(title)
            url_base = "https://www.fidelity.com"
            if js['story']['photo']:
                pic_url = url_base + js['story']['photo']['viewImage']
                folderpath = os.path.join(self.fd.choose_folder(), path_name + ".jpg")
                self.download_pic(pic_url, folderpath)
                result = {"title": title, "news": cleaned, "timestamp": ts, "url": url, "author": autor,
                          "filename": path_name,
                          "picture": folderpath}
            else:
                result = {"title": title, "news": cleaned, "timestamp": ts, "url": url, "author": autor,
                          "filename": path_name,
                          "picture": None}
            # with open(path, "w", encoding="utf-8")as f:
            #     f.write(json.dumps(result, indent=2))
            return result
        except Exception:
            pass

    def cleaning(self, text):
        cleaning = re.sub("<.*?>", "", text)
        final = self.remover.filter_tags(cleaning)
        final = final.replace("&", "&amp;")
        return final


if __name__ == "__main__":
    nd = NewDownloader()
    text = nd.parseNews("https://www.fidelity.com/news/article/top-news/201906192102RTRSNEWSCOMBINED_KCN1TL00T-OUSBS_1")
    print(text)
