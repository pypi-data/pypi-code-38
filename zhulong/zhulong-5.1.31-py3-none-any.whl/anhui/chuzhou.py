import time
from collections import OrderedDict
from os.path import join, dirname
from pprint import pprint

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json

from zhulong.util.etl import est_tbs, est_meta, est_html, gg_existed, add_info
from zhulong.util.conf import get_conp

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]


# url="http://www.hbzbcg.cn/hbweb/jyxx/002001/002001001/002001001001/MoreInfo.aspx?CategoryNum=002001001001"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_ = 'chuzhou'


def f1(driver, num):

    locator = (By.XPATH, '//div[@class="right-wrap-ccontent-text"]/div/table//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum = re.findall('Paging=(\d+)',url)[0]
    if int(cnum) != num:
        val = driver.find_element_by_xpath(
            '//div[@class="right-wrap-ccontent-text"]/div/table//tr[1]//a').get_attribute('href')[-60:-30]

        url=re.sub('Paging=\d+','Paging=%s'%num,url)
        driver.get(url)
        # 第二个等待
        locator = (By.XPATH,
                   '//div[@class="right-wrap-ccontent-text"]/div/table//tr[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='right-wrap-ccontent-text')
    trs = div.find_all('tr', height=25)

    for tr in trs:
        href = tr.find('td', align='left').a['href']
        name = tr.find('td', align='left').a['title']
        ggstart_time = tr.find('td', align='right').get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://ggzy.chuzhou.gov.cn' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):

    locator = (By.XPATH, '//div[@class="right-wrap-ccontent-text"]/div/table//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//td[@class="huifont"]').text

    total_ = re.findall(r'/(\d+)', page)[0]

    total = int(total_)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[contains(@id,"menutab") and (not(@style) or @style="")]')

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

    div = soup.find('div', attrs={'id': re.compile('menutab_6_\d'), 'style': ''})
    if div == None:
        div = soup.find('div', attrs={'id': re.compile('menutab_5_\d'), 'style': ''})
        if div == None:
            raise ValueError

    return div




def get_data():
    data = []

    #gcjs
    ggtype1 = OrderedDict([("zhaobiao","001"),("gqita_da_bian", "002"), ("zhongbiaohx", "003"),("zhongbiao","004"),('liubiao','006')])
    #zfcg
    ggtype2 = OrderedDict([("zhaobiao","001"),("biangeng","002"),("zhongbiao", "003"), ("liubiao", "005")])

    ##zfcg_gcjs
    adtype1 = OrderedDict([('市辖区','001'),("南谯区", "002"), ("琅琊区", "003"),("天长市","004"),("明光市","005"),
                           ('全椒县', '006'), ("凤阳县", "007"), ("定远县", "008"), ("来安县", "009")])

    #gcjs
    for w1 in ggtype1.keys():
        for w2 in adtype1.keys():
            href = "http://ggzy.chuzhou.gov.cn/Front_jyzx/jyxx/002008/002008{jy}/002008{jy}{dq}/?Paging=1".format(dq=adtype1[w2],jy=ggtype1[w1])
            tmp = ["gcjs_%s_diqu%s_gg" % (w1, adtype1[w2]), href, ["name","ggstart_time","href",'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)
    for w1 in ggtype2.keys():
        for w2 in adtype1.keys():
            href = "http://ggzy.chuzhou.gov.cn/Front_jyzx/jyxx/002009/002009{jy}/002009{jy}{dq}/?Paging=1".format(dq=adtype1[w2],jy=ggtype2[w1])
            tmp = ["zfcg_%s_diqu%s_gg" % (w1, adtype1[w2]), href, ["name","ggstart_time","href",'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)

    data1 = data.copy()


    return data1


data=get_data()
# pprint(data)



#网站变更 : http://ggzy.chuzhou.gov.cn
#变更时间 : 2019-6-4

def work(conp, **args):
    est_meta(conp, data=data, diqu="安徽省滁州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anhui", "chuzhou"])
    pass