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

_name_ = 'shanwei'


def f1(driver, num):
    locator = (By.XPATH, '//ul[@id="listView"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum=int(driver.find_element_by_xpath('//span[@id="curpage"]').text)

    if cnum != num:
        val = driver.find_element_by_xpath(
            '//ul[@id="listView"]/li[1]/a').get_attribute('href')
        val=re.findall('details\?(.+?)=all',val)[0]
        print(val)

        driver.execute_script("""
        (function (pageIndex) {
          params.data.pageIndex = pageIndex - 1;
          actionHandler(params, function (args) {
          handlerCallback(pageIndex, args, pageIndex);
            });})(%d) """%num)

        locator = (
            By.XPATH, "//ul[@id='listView']/li[1]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("ul", id="listView")
    dls = div.find_all("li", recursive=False)

    data = []
    for dl in dls:

        name = dl.find('a').get_text()
        href = dl.find('a')['href']
        ggstart_time = dl.find('span').get_text()
        diqu=re.findall('^【(.+?)】',name)[0]
        info = json.dumps({'diqu':diqu},ensure_ascii=False)

        if 'http' in href:
            href = href
        else:
            href = 'http://swggzy.shanwei.gov.cn' + href

        tmp = [name, ggstart_time, href, info]
        # print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@id="listView"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total=driver.find_element_by_xpath('//span[@id="totalPages"]').text

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="content2"][string-length()>50] | //div[@class="content2"]/p/img')
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
    div = soup.find('div', class_='contentbox2')

    return div


data = [

    ["gcjs_zhaobiao_gg",
     "http://swggzy.shanwei.gov.cn/noticesList?rootId=4c9864644f2441718b124ff183daf3fd&columnId=4793892710e942bdb8edb883822dbab4&area=all",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_da_bian_gg",
     "http://swggzy.shanwei.gov.cn/noticesList?rootId=4c9864644f2441718b124ff183daf3fd&columnId=c0d135163be342c2b76a4957dc4b1999&area=all",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://swggzy.shanwei.gov.cn/noticesList?rootId=4c9864644f2441718b124ff183daf3fd&columnId=089ddf2ff80c4e259ac5b208e9154469&area=all",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["zfcg_zhaobiao_gg",
     "http://swggzy.shanwei.gov.cn/noticesList?rootId=a8950dedd38a4103973c8140784ab4d3&columnId=d3174a1009b141bcb4a99666527f53ed&area=all",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_gqita_da_bian_gg",
     "http://swggzy.shanwei.gov.cn/noticesList?rootId=a8950dedd38a4103973c8140784ab4d3&columnId=4a6dafa78918407eb17400c5ef72dcfe&area=all",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://swggzy.shanwei.gov.cn/noticesList?rootId=a8950dedd38a4103973c8140784ab4d3&columnId=02f4929cf37641a5b1dfbd746af46e7b&area=all",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省汕尾市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(
        conp=[
            "postgres",
            "zhulong.com.cn",
            '192.168.169.47',
            "guangdong",
            "shanwei"],
        headless=True,
        num=1,
        total=2)
