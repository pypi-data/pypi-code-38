import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write, db_query, db_command
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from zhulong.util.etl import est_meta, est_html, add_info
import time

_name_ = "huangshi"


def f1(driver, num):
    url = driver.current_url
    if "pageIndex" not in url:
        url = url + "?pageIndex=%d" % num
    else:
        url = re.sub("(?<=pageIndex=)[0-9]{1,}", str(num), url)
    driver.get(url)
    locator = (By.CLASS_NAME, "filter-content")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source

    soup = BeautifulSoup(page, 'lxml')

    div = soup.find_all("div", class_="filter-content")[0]
    ul = div.find("ul")
    lis = ul.find_all("li")
    data = []
    for li in lis:
        a = li.find("a")
        span = li.find("span", class_="time")
        tmp = [a["title"],re.findall("[0-9/]{4,}", span.text)[0] , "http://www.hsztbzx.com" + a["href"]]
        data.append(tmp)
    df = pd.DataFrame(data=data, columns=["name", "ggstart_time", "href"])
    df["info"] = None
    return df


def f2(driver):
    locator = (By.CLASS_NAME, "pagination")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    a = driver.find_element_by_xpath("//ul[@class='pagination']/li/a[string()='尾页']")

    href = a.get_attribute("href")
    total = re.findall("pageIndex=([0-9]{1,})", href)[0]
    total = int(total)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.CLASS_NAME, "inner-main-content")

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5: break

    page = driver.page_source

    soup = BeautifulSoup(page, 'lxml')

    div = soup.find('div', class_='inner-main-content')
    # div=div.find_all('div',class_='ewb-article')[0]

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://www.hsztbzx.com/BidNotice/jsgc/zbgg", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_biangeng_gg", "http://www.hsztbzx.com/BidNotice/jsgc/bggg", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg", "http://www.hsztbzx.com/BidNotice/jsgc/zbhxrgs", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg", "http://www.hsztbzx.com/BidNotice/jsgc/zbjggg", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://www.hsztbzx.com/BidNotice/zfcg/cggg", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg", "http://www.hsztbzx.com/BidNotice/zfcg/bggg", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiaohx_gg", "http://www.hsztbzx.com/BidNotice/zfcg/zbhxrgs", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg", "http://www.hsztbzx.com/BidNotice/zfcg/zbjggg", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_liubiao_gg", "http://www.hsztbzx.com/BidNotice/zfcg/fbgg", ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data, diqu="湖北省黄石市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "127.0.0.1", "hubei", "huangshi"])
