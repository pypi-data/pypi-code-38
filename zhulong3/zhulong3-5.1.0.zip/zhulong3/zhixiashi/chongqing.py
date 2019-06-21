import json

from collections import OrderedDict
from pprint import pprint

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

_name_ = 'zhixiashi_chongqing'


def f1(driver, num):
    locator = (By.XPATH, '(//table[@width="95%"]//tr[2]//a)[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum = url.rsplit('/',maxsplit=1)[1]

    if int(cnum) != num:
        val = driver.find_element_by_xpath(
            '(//table[@width="95%"]//tr[2]//a)[1]').get_attribute('href')[-40:]

        url='/'.join([url.rsplit('/',maxsplit=1)[0],str(num)])
        driver.get(url)

        locator = (
            By.XPATH, "(//table[@width='95%']//tr[2]//a)[1][not(contains(@href,'{}'))]".format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("table", width="95%")
    dls = div.find_all("tr")[1:]

    data = []
    for dl in dls:
        tds = dl.find_all('td')
        procode = tds[0].get_text().strip()
        name=tds[1].get_text().strip()
        href=tds[1].a['href']
        mark=div.find('tr').find_all('td')[2].get_text()
        ggstart_time = tds[-1].get_text().strip()

        if '中标' in mark:
            dw=tds[2].a['title']
            info = json.dumps({"procode": procode,"dw":dw}, ensure_ascii=False)
        else:
            info = json.dumps({"procode": procode}, ensure_ascii=False)

        if 'http' in href:
            href = href
        else:
            href = 'https://cpcb.cqggzy.com' + href

        tmp = [name, ggstart_time, href,info]
        print(tmp)

        data.append(tmp)
    df = pd.DataFrame(data=data)

    driver.switch_to.parent_frame()
    return df


def f2(driver):
    locator = (By.XPATH, '(//table[@width="95%"]//tr[2]//a)[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total=driver.find_element_by_xpath('//div[@class="mvcPager"]/a[last()]').get_attribute('href')
    total=total.rsplit('/',maxsplit=1)[1]

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '(//div[@class="nrkd left"])[1][string-length()>50]')
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
    div = soup.find('div', class_='nrkd left')

    return div



data=[

["gcjs_zhaobiao_gg" , 'https://cpcb.cqggzy.com/Front.aspx/Zbgg/1', ["name", "ggstart_time", "href", 'info'],f1, f2],
["gcjs_zhaobiao_yaoqing_gg" , 'https://cpcb.cqggzy.com/Front.aspx/InviteBidInfo/1', ["name", "ggstart_time", "href", 'info'],add_info(f1,{"zbfs":"邀请招标"}), f2],
["gcjs_zhongbiaohx_gg" , 'https://cpcb.cqggzy.com/Front.aspx/Zbgs/1', ["name", "ggstart_time", "href", 'info'],f1, f2],
      ]



def work(conp, **args):
    est_meta(conp, data=data, diqu="重庆市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(
        conp=[
            "postgres",
            "since2015",
            '192.168.3.171',
            "zhixiashi",
            "beijing"],
        headless=False,
        num=1,
        )
    pass