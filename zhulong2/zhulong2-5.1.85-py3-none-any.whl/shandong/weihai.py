import datetime
import json
import random
import time

import pandas as pd
import re

import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from zhulong2.util.fake_useragent import UserAgent
from zhulong2.util.etl import est_tbs, est_meta, est_html, est_gg

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://www.whgp.gov.cn/whzf/front/pubmsg.do?msgtype=0&add=10&navigation=%CA%D0%B1%BE%BC%B6%B2%C9%B9%BA%B9%AB%B8%E6#"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_ = 'shandong_weihai'


def f1(driver, num):
    ua=UserAgent()
    locator = (By.XPATH, '//table[@class="aa"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cookies = driver.get_cookies()
    COOKIES = {}
    for cookie in cookies:
        COOKIES[cookie['name']] = cookie['value']

    headers = {
        "User-Agent": ua.chrome,
        "Referer": url,
    }

    form_data = {
        "currentPage":num,
    }

    time.sleep(random.random()+1)
    req = requests.post(url, data=form_data, headers=headers,cookies=COOKIES,timeout=20)
    if req.status_code != 200:
        print(req.status_code)
        raise ValueError

    data_=[]
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='aa').find_all('tr',style=re.compile('background.+'))
    for tr in div:
        tds=tr.find_all('td')
        href=tds[1].a['onclick']
        id1=re.findall("jump\('(.+?)'",href)[0]
        id2=re.findall("jump\('.+?' ,'(\d+)'",href)[0]
        href="http://www.whgp.gov.cn/whzf/front/pubmsg/one.do?id={id1}&msgtype={id2}&submenu=61000800".format(id1=id1,id2=id2)
        name=tds[1].a.get_text()
        ggstart_time = tds[2].get_text().strip()
        ggstart_time=re.findall('\d+-\d+?-\d+',ggstart_time)[0]
        tmp = [name, ggstart_time, href]
        data_.append(tmp)

    df = pd.DataFrame(data=data_)
    df["info"] = None
    return df



def f2(driver):
    locator = (By.XPATH, '//table[@class="aa"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//div[@id="pagination"]//table//td[3]').text

    total=re.findall('/(\d+?)页',total)[0]
    total=int(total)

    driver.quit()
    return total





def f3(driver, url):
    driver.get(url)

    try:
        locator = (By.XPATH, '//div[@id="content"][string-length()>10]')

        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    except:
        if 'login.jsp' in driver.current_url:
            return 'login'
        else:
            raise TimeoutError

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
    div = soup.find('div',id="content")

    return div


data = [

    ["zfcg_zhaobiao_diqu1_gg", "http://www.whgp.gov.cn/whzf/front/pubmsg.do?add=10&msgtype=0&mainmenu=&submenu=",["name",  "ggstart_time",  "href", 'info'], f1, f2],
    ["zfcg_zhongbiao_diqu1_gg", "http://www.whgp.gov.cn/whzf/front/pubmsg.do?add=10&msgtype=1&mainmenu=&submenu=",["name",  "ggstart_time",  "href", 'info'], f1, f2],
    ["zfcg_zhaobiao_diqu2_gg", "http://www.whgp.gov.cn/whzf/front/pubmsg.do?add=10&msgtype=2&mainmenu=&submenu=",["name",  "ggstart_time",  "href", 'info'], f1, f2],
    ["zfcg_zhongbiao_diqu2_gg", "http://www.whgp.gov.cn/whzf/front/pubmsg.do?add=10&msgtype=3&mainmenu=&submenu=",["name",  "ggstart_time",  "href", 'info'], f1, f2],

    ["zfcg_yucai_diqu1_gg", "http://www.whgp.gov.cn/whzf/front/pubinf.do?add=10&msgtype=0",["name",  "ggstart_time",  "href", 'info'], f1, f2],
    ["zfcg_yanshou_diqu1_gg", "http://www.whgp.gov.cn/whzf/front/pubinf.do?add=10&msgtype=2",["name",  "ggstart_time",  "href", 'info'], f1, f2],
    ["zfcg_yucai_diqu2_gg", "http://www.whgp.gov.cn/whzf/front/pubinf.do?add=10&msgtype=3",["name",  "ggstart_time",  "href", 'info'], f1, f2],
    ["zfcg_yanshou_diqu2_gg", "http://www.whgp.gov.cn/whzf/front/pubinf.do?add=10&msgtype=5",["name",  "ggstart_time",  "href", 'info'], f1, f2],

]


###网站失效



def work(conp, **args):
    est_meta(conp, data=data, diqu="山东省威海市", **args)
    est_html(conp,f=f3,**args)


if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "lch", "shandong_weihai"]

    work(conp=conp,headless=False,num=1)