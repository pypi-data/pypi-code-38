import json

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
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info, est_gg

# driver=webdriver.Chrome()
# url="http://www.bygzjy.cn/f/trade/annogoods/list?selectedProjectType=3"
# driver.get(url)

_name_ = 'yangjiang'


def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url=driver.current_url

    cnum=int(re.findall('page=(\d+)',url)[0])

    if cnum != num:
        val = driver.find_element_by_xpath(
            '//ul[@class="list"]/li[1]/a').get_attribute('href')[-30:]

        url=re.sub('page=\d+','page=%s'%num,url)

        driver.get(url)

        locator = (
            By.XPATH, "//ul[@class='list']/li[1]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("ul", class_="list")
    dls = div.find_all("li",recursive=False)

    data = []
    for dl in dls:
        name = dl.find('a')['title']
        href = dl.find('a')['href']
        ggstart_time = dl.find('span').get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.yjggzy.cn' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None

    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total=driver.find_element_by_xpath('//div[@class="pagination"]/a[last()]').get_attribute('href')
    total=re.findall('page=(\d+)',total)[0]

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//dl[@class="acticlecontent"][string-length()>10] | //dl[@class="acticlecontent"]/dd/img')
    WebDriverWait(
        driver, 10).until(
        EC.presence_of_all_elements_located(locator))

    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5:
            break

    # f3 情况1
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='acticle')

    return div


data = [

    ["gcjs_zhaobiao_gg",
     "http://www.yjggzy.cn/Query/JsgcBidAfficheQuery2/d4f193435ad04447a997719474139181?page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_biangeng_gg",
     "http://www.yjggzy.cn/Query/ArticleQuery2/9cb01c8a51f54006ac15b302fe50cf0e?page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://www.yjggzy.cn/Query/JsgcWinBidAfficheQuery2/46eb01f656f4468cb65a434b77d73065?page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://www.yjggzy.cn/Query/ArticleQuery2/465c897866824460b1783cfa20985510?page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://www.yjggzy.cn/Query/ArticleQuery2/1512d4cad92c44858cd52b85debbd8ed?page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://www.yjggzy.cn/Query/ArticleQuery2/43a0fbd899a34465945625ea39e34d9c?page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省阳江市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(
        conp=[
            "postgres",
            "since2015",
            '192.168.3.171',
            "guangdong",
            "yangjiang"],
        headless=True,
        num=1,
        total=2)
