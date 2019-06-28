import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write, db_command, db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info

_name_ = "yueyang"


def f1(driver, num):
    locator = (By.ID, "categorypagingcontent")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url

    cnum = int(re.findall("/([0-9]{1,}).html", url)[0])

    if num != cnum:
        val = driver.find_element_by_xpath("//div[@id='categorypagingcontent']/div[@class='erjitongzhilist']//li[1]/a").get_attribute("title")

        url = re.sub("[0-9]{1,}(?=.html)", str(num), url)
        driver.get(url)

        locator = (By.XPATH, "//div[@id='categorypagingcontent']/div[@class='erjitongzhilist']//li[1]/a[@title!='%s']" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source

    soup = BeautifulSoup(page, "html.parser")

    div = soup.find("div", id="categorypagingcontent")
    div1 = div.find("div", class_="erjitongzhilist")

    lis = div1.find_all("li", class_="news-list-item")
    data = []
    for li in lis:
        a = li.find("a")
        span = li.find("span")
        tmp = [a["title"], span.text.strip(), "http://ggzy.yueyang.gov.cn" + a["href"]]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='fengye']/ul//a[string()='末页']")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    href = driver.find_element_by_xpath("//div[@class='fengye']/ul//a[string()='末页']").get_attribute("href")

    total = int(re.findall("/([0-9]{1,}).html", href)[0])

    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.CLASS_NAME, "xiangxiyekuang")

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

    soup = BeautifulSoup(page, 'html.parser')

    div1 = soup.find('div', class_='xiangxiyebiaoti')
    div2 = soup.find('div', class_='xiangxiyekuang')
    div3 = soup.find('div', class_='xiangxiyekuang')

    div = str(div1) + str(div2) + str(div3)
    return div


data = [
    ["gcjs_zhaobiao_gg", "http://ggzy.yueyang.gov.cn/004/004001/1.html", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_biangeng_gg", "http://ggzy.yueyang.gov.cn/004/004001/004001002/1.html", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg", "http://ggzy.yueyang.gov.cn/004/004001/004001003/1.html", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_gg", "http://ggzy.yueyang.gov.cn/004/004001/004001004/1.html", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://ggzy.yueyang.gov.cn/004/004002/004002001/1.html", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg", "http://ggzy.yueyang.gov.cn/004/004002/004002002/1.html", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg", "http://ggzy.yueyang.gov.cn/004/004002/004002003/1.html", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_gg", "http://ggzy.yueyang.gov.cn/004/004002/004002004/1.html", ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省岳阳市", **args)
    est_html(conp, f=f3, **args)

if __name__ == '__main__':
    driver = webdriver.Chrome()
    print(f3(driver, 'http://ggzy.yueyang.gov.cn/004/004002/004002004/20190619/d7ae7216-497d-471e-85d9-700f28877ae2.html'))