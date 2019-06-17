import jieba
import requests
import re

from collections import Counter
from page_topn.stop_words import stop_words
from page_topn.dynamic_page import Dynimic_process

def get_page_data(url,flag,driver_path):
    if flag:
        dynamic_process = Dynimic_process(driver_path)
        content = dynamic_process.start_requests(url)
        return content
    else:
        content = requests.get(url)
        return content.text

def process_data(data):
    chinese = "".join(re.findall("[\u4e00-\u9fa5]+",data))
    return jieba.tokenize(chinese,mode="search")


def page_topn(url, topn, flag=False,driver_path="./chromedriver"):
    data = get_page_data(url,flag,driver_path)

    words = []
    chinese = process_data(data)
    for e in chinese:
        word = e[0]
        if word not in stop_words:
            words.append(word)

    return Counter(words).most_common(topn)

if __name__ == "__main__":
    words = page_topn("http://zfcg.wlmq.gov.cn/infopublish.do?method=infoPublishView&infoid=89780E928AE02608E05311C410AC3412",
                      10,
                      True,
                      )
    print(words)