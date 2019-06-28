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

_name_ = 'dongguan'


def f1(driver, num):
    locator = (By.XPATH, '//div[@id="tbl_div"]/table/tbody/tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = int(driver.find_element_by_xpath('//span[@class="curr"]').text)
    if cnum != num:
        page_count=len(driver.page_source)
        val = driver.find_element_by_xpath(
            '//div[@id="tbl_div"]/table/tbody/tr[1]//a').get_attribute('href')[-40:-15]

        driver.execute_script("kkpager._clickHandler(%s)" % num)

        locator = (
            By.XPATH, "//div[@id='tbl_div']/table/tbody/tr[1]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(
            driver, 10).until(
            EC.presence_of_element_located(locator))
        WebDriverWait(driver,10).until(lambda driver:len(driver.page_source) != page_count)

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("div", id="tbl_div")
    dls = div.find_all("tr")[1:]
    data = []
    for dl in dls:
        tds = dl.find_all('td')

        if len(tds) == 6:

            procode = tds[1].get_text()
            name = tds[2].a['title']
            href = tds[2].a['href']
            protype = tds[3].get_text()
            ggstart_time = tds[4].get_text()
            ggend_time = tds[5].get_text()
            info = json.dumps({'procode': procode,
                               'protype': protype,
                               'ggendtime': ggend_time},
                              ensure_ascii=False)

        elif len(tds) == 5:
            procode = tds[1].get_text()
            name = tds[2].a['title']
            href = tds[2].a['href']
            protype = tds[3].get_text()
            ggstart_time = tds[4].get_text()
            info = json.dumps({'procode': procode,
                               'protype': protype,},
                              ensure_ascii=False)


        else:
            name = tds[1].a['title']
            href = tds[1].a['href']
            ggstart_time = tds[2].get_text()

            info = None
        if 'http' in href:
            href = href
        else:
            href = 'http://ggzy.dg.gov.cn' + href

        tmp = [name, ggstart_time, href, info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, "//div[@id='tbl_div']/table/tbody/tr[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = int(driver.find_element_by_xpath(
        '//span[@class="totalPageNum"]').text)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="content"][string-length()>10]')
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
    div = soup.find('div', class_=re.compile('detail'))

    return div


data = [
    #
    ["gcjs_zhaobiao_gg",
     "http://ggzy.dg.gov.cn/ggzy/website/WebPagesManagement/jslist?fcInfotype=1&TypeIndex=0&KindIndex=-1",
     ["name",
      "ggstart_time",
      "href",
      "info"],
     f1,
     f2],

    ["gcjs_biangeng_gg",
     "http://ggzy.dg.gov.cn/ggzy/website/WebPagesManagement/jslist?fcInfotype=4&TypeIndex=1&KindIndex=-1",
     ["name",
      "ggstart_time",
      "href",
      "info"],
        f1,
        f2],

    ["gcjs_zhongbiaohx_gg",
     "http://ggzy.dg.gov.cn/ggzy/website/WebPagesManagement/jslist?fcInfotype=7&TypeIndex=2&KindIndex=-1",
     ["name",
      "ggstart_time",
      "href",
      "info"],
        f1,
        f2],
    ["gcjs_biangeng_yanqi_gg",
     "http://ggzy.dg.gov.cn/ggzy/website/WebPagesManagement/jslist?fcInfotype=4&fcInfopubsource=1&TypeIndex=3&KindIndex=-1",
     ["name",
      "ggstart_time",
      "href",
      "info"],
     add_info(f1,
              {'gclx': "延期公告"}),
        f2],

    ["zfcg_zhaobiao_gg",
     "http://ggzy.dg.gov.cn/ggzy/website/WebPagesManagement/TradeInfo/GovProcurement/govlist?fcInfotype=1&govTypeIndex=0&belongIndex=-1",
     ["name",
      "ggstart_time",
      "href",
      "info"],
        f1,
        f2],

    ["zfcg_biangeng_gg",
     "http://ggzy.dg.gov.cn/ggzy/website/WebPagesManagement/TradeInfo/GovProcurement/govlist?fcInfotype=4&govTypeIndex=1&belongIndex=-1",
     ["name",
      "ggstart_time",
      "href",
      "info"],
        f1,
        f2],

    ["zfcg_zhongbiao_gg",
     "http://ggzy.dg.gov.cn/ggzy/website/WebPagesManagement/TradeInfo/GovProcurement/govlist?fcInfotype=7&govTypeIndex=2&belongIndex=-1",
     ["name",
      "ggstart_time",
      "href",
      "info"],
        f1,
        f2],

    ["jqita_gqita_gg",
     "http://ggzy.dg.gov.cn/ggzy/website/WebPagesManagement/TenderPublishInfo/OtherPublishInfo/list",
     ["name",
      "ggstart_time",
      "href",
      "info"],
        f1,
        f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省东莞市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(
        conp=[
            "postgres",
            "since2015",
            '192.168.3.171',
            "guangdong",
            "dongguan_test"],
        headless=True,
        )
