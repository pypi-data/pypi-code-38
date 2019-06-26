import re

import requests


class DownIndex:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"}
        self.base_url = "https://www.fidelity.com/news/"
        self.top_news_url = "https://www.fidelity.com/news/article/top-news/"

    def get_url(self):
        responses = requests.get(self.base_url, headers=self.headers)
        content = responses.text
        top_news = r"(?<=var topNews = ).+?(?=])"
        pattern = re.compile(top_news)
        result = re.search(pattern, content).group(0)
        result = result.strip("[").strip("]")
        guid = r'(?<=guid").+?(?=,)'
        pattern2 = re.compile(guid)
        url_list = re.findall(pattern2, result)
        url_list = [self.top_news_url + eval(i.replace(":", "")) for i in url_list]
        return url_list


if __name__ == "__main__":
    download = DownIndex()
    rs = download.get_url()
    print(rs)
