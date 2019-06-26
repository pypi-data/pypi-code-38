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
import json

import time

from zhulong.util.etl import est_html, est_meta, add_info

_name_ = "guangzhou"


def f1(driver, num):

    locator = (By.XPATH, '//table[@class="wsbs-table"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//li[@class="currentpage"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = int(driver.find_element_by_class_name('currentpage').text)
    if num != cnum:

        page_count = len(driver.page_source)
        val = driver.find_element_by_xpath(
            "//table[@class='wsbs-table']//tr[2]//a").get_attribute('href')[-30:]

        driver.execute_script("goPage(%d)" % num)

        locator = (
            By.XPATH,
            "//table[@class='wsbs-table']//tr[2]//a[not(contains(@href,'%s'))]" %
            val)
        WebDriverWait(
            driver, 10).until(
            EC.presence_of_element_located(locator))

        WebDriverWait(
            driver, 10).until(lambda driver: len(driver.page_source) != page_count)

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    tb = soup.find_all("table", class_="wsbs-table")[0]

    trs = tb.find_all('tr')
    data = []
    for tr in trs[1:]:
        tds = tr.find_all("td")

        name = tds[1].text.strip()
        ggstart_time = tds[2].text.strip()
        href = "http://www.gzggzy.cn" + tds[1].a['href']

        bhs = re.findall(r'\[([A-Z0-9a-z\-]*)\]', name)
        if bhs == []:
            info = None
        else:
            info = json.dumps({"bh": bhs[0]}, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f1_zsjg(driver, num):
    locator = (By.XPATH, '//table[@class="wsbs-table"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//li[@class="currentpage"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = int(driver.find_element_by_class_name('currentpage').text)
    if num != cnum:
        page_count = len(driver.page_source)
        val = driver.find_element_by_xpath(
            "//table[@class='wsbs-table']//tr[2]//a").get_attribute('href')[-30:]

        driver.execute_script("goPage(%d)" % num)

        locator = (
            By.XPATH,
            "//table[@class='wsbs-table']//tr[2]//a[not(contains(@href,'%s'))]" %
            val)
        WebDriverWait(
            driver, 10).until(
            EC.presence_of_element_located(locator))

        WebDriverWait(
            driver, 10).until(lambda driver: len(driver.page_source) != page_count)

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    tb = soup.find_all("table", class_="wsbs-table")[0]

    trs = tb.find_all('tr')
    data = []
    for tr in trs[1:]:
        tds = tr.find_all("td")

        name = tds[1].text.strip()
        ggstart_time = tds[2].text.strip()
        ggend_time = tds[3].text.strip()
        href = "http://www.gzggzy.cn" + tds[1].a['href']

        bhs = re.findall(r'\[([A-Z0-9a-z\-]*)\]', name)
        if bhs == []:
            bh = None
        else:
            bh = bhs[0]
        info = {"ggend_time": ggend_time}
        if bh is not None:
            info['bh'] = bh

        info = json.dumps(info, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f1_zhongbiaohx(driver, num):
    locator = (By.XPATH, '//table[@class="wsbs-table"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//li[@class="currentpage"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = int(driver.find_element_by_class_name('currentpage').text)
    if num != cnum:
        page_count = len(driver.page_source)
        val = driver.find_element_by_xpath(
            "//table[@class='wsbs-table']//tr[2]//a").get_attribute('href')[-30:]

        driver.execute_script("goPage(%d)" % num)

        locator = (
            By.XPATH,
            "//table[@class='wsbs-table']//tr[2]//a[not(contains(@href,'%s'))]" %
            val)
        WebDriverWait(
            driver, 10).until(
            EC.presence_of_element_located(locator))

        WebDriverWait(
            driver, 10).until(lambda driver: len(driver.page_source) != page_count)
    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    tb = soup.find_all("table", class_="wsbs-table")[0]

    trs = tb.find_all('tr')
    data = []
    for tr in trs[1:]:
        tds = tr.find_all("td")

        name = tds[2].text.strip()
        ggstart_time = tds[4].text.strip()
        gctype1 = tds[3].text.strip()
        href = "http://www.gzggzy.cn" + tds[2].a['href']

        bh = tds[1].text.strip()
        info = {"gctype1": gctype1, "bh": bh}

        info = json.dumps(info, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f1_zhongbiaoxx(driver, num):
    locator = (By.XPATH, '//table[@class="wsbs-table"]//tr[2]/td[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//li[@class="currentpage"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = int(driver.find_element_by_class_name('currentpage').text)
    if num != cnum:

        page_count = len(driver.page_source)
        val=driver.find_element_by_xpath('//table[@class="wsbs-table"]//tr[2]/td[2]').text.strip()

        driver.execute_script("goPage(%d)" % num)

        locator = (By.XPATH, '//table[@class="wsbs-table"]//tr[2]/td[2][not(contains(string(),"%s"))]' %val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        WebDriverWait(
            driver, 10).until(lambda driver: len(driver.page_source) != page_count)

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    tb = soup.find_all("table", class_="wsbs-table")[0]
    trs = tb.find_all("tr")

    x = int(len(trs) / 5)
    data = []
    for i in range(x):

        tds1 = trs[i * 5 + 1].find_all("td")
        tmp1 = [w.text.strip() for w in tds1[1:]]
        tmp2 = [w.find_all('td')[1].text.strip()
                for w in trs[2 + 5 * i:5 * i + 6]]
        tmp = tmp1 + tmp2
        # tmp.append(None)
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f1_zfcg(driver, num):
    locator = (By.XPATH, '//table[@class="wsbs-table"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//div[@class="pagination page-mar"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    a = driver.find_element_by_class_name("page-mar")
    p1 = re.findall("第([0-9]*)页", a.text)[0]
    cnum = int(p1)
    if num != cnum:
        page_count = len(driver.page_source)
        val = driver.find_element_by_xpath(
            "//table[@class='wsbs-table']//tr[2]//a").get_attribute('href')[-30:]
        url = driver.current_url
        url = re.sub("page=[0-9]*", 'page=%d' % num, url)
        driver.get(url)

        locator = (
            By.XPATH,
            "//table[@class='wsbs-table']//tr[2]//a[not(contains(@href,'%s'))]" %
            val)
        WebDriverWait(
            driver, 10).until(
            EC.presence_of_element_located(locator))
        WebDriverWait(
            driver, 10).until(
            lambda driver: len(
                driver.page_source) != page_count)

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    tb = soup.find_all("table", class_="wsbs-table")[0]

    trs = tb.find_all('tr')
    data = []
    for tr in trs[1:]:
        tds = tr.find_all("td")

        name = tds[1].text.strip()
        ggstart_time = tds[2].text.strip()
        href = "http://www.gzggzy.cn" + tds[1].a['href']
        # info=None

        bhs = re.findall(r'\(([A-Z0-9a-z\-]*)\)', name)
        if bhs == []:
            info = None
        else:
            info = json.dumps({"bh": bhs[0]}, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.CLASS_NAME, "page-mar")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    a = driver.find_element_by_class_name("page-mar")
    p1 = re.findall("共([0-9]*)条", a.text)[0]
    p1 = int(p1)
    p = re.findall("共([0-9]*)页", a.text)[0]

    p = int(p)
    driver.quit()
    if p1 == 0:
        return 0
    return p


def f3(driver, url):

    driver.get(url)

    locator = (By.XPATH, "//div[@class='xx-main'][string-length()>100]")

    WebDriverWait(
        driver, 10).until(
        EC.presence_of_all_elements_located(locator))

    before = len(driver.page_source)
    time.sleep(0.5)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5:
            break

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    div = soup.find('div', class_='xx-main')

    return div


data = [
    ['gcjs_zhaobiao_fangjianshizheng_gg', 'http://www.gzzb.gd.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=503&channelids=15&pchannelid=466&curgclb=01,02,14&curxmlb=01,02,03,04,05,14&curIndex=1&pcurIndex=1',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1, {"gctype": "房建市政"}), f2
     ],


    ['gcjs_zsjg_fangjianshizheng_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=504&channelids=16&pchannelid=466&curgclb=01,02,14&curxmlb=01,02,03,04,05,14&curIndex=2&pcurIndex=1',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1_zsjg, {"gctype": "房建市政"}), f2
     ],

    ['gcjs_zhongbiaohx_fangjianshizheng_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=506&channelids=17&pchannelid=466&curgclb=01,02,14&curxmlb=01,02,03,04,05,14&curIndex=3&pcurIndex=1',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1_zhongbiaohx, {"gctype": "房建市政"}), f2
     ],

    ['gcjs_zhongbiaohx_toubiao_fangjianshizheng_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=519&channelids=17&pchannelid=466&curgclb=01,02,14&curxmlb=01,02,03,04,05,14&curIndex=4&pcurIndex=1',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1_zhongbiaohx, {"gctype": "房建市政"}), f2
     ],


    ['gcjs_zhongbiaoxx_fangjianshizheng_info', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=505&channelids=18&pchannelid=466&curgclb=01,02,14&curxmlb=01,02,03,04,05,14&curIndex=5&pcurIndex=1',
     ["bh", "xmmc", "zbdw", "zbdl", "zhongbiaodw", "zhongbiaojia", "fzr", "zb_tongzhishu_bh",
         "tongzhishu_fbdate", "info"], add_info(f1_zhongbiaoxx, {"gctype": "房建市政"}), f2
     ],



    # 交通
    ['gcjs_zhaobiao_jiaotong_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=510&channelids=15&pchannelid=467&curgclb=03&curxmlb=01,02,03,04,05,14&curIndex=1&pcurIndex=2',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1, {"gctype": "交通工程"}), f2
     ],

    ['gcjs_zsjg_jiaotong_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=511&channelids=16&pchannelid=467&curgclb=03&curxmlb=01,02,03,04,05,14&curIndex=2&pcurIndex=2',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1_zsjg, {"gctype": "交通工程"}), f2
     ],

    ['gcjs_zhongbiaohx_jiaotong_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=513&channelids=17&pchannelid=467&curgclb=03&curxmlb=01,02,03,04,05,14&curIndex=3&pcurIndex=2',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1_zhongbiaohx, {"gctype": "交通工程"}), f2
     ],


    ['gcjs_zhongbiaoxx_jiaotong_info', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=512&channelids=18&pchannelid=467&curgclb=03&curxmlb=01,02,03,04,05,14&curIndex=4&pcurIndex=2',
     ["bh", "xmmc", "zbdw", "zbdl", "zhongbiaodw", "zhongbiaojia", "fzr", "zb_tongzhishu_bh",
         "tongzhishu_fbdate", "info"], add_info(f1_zhongbiaoxx, {"gctype": "交通工程"}), f2
     ],


    # 电力

    ['gcjs_zhaobiao_dianli_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=515&channelids=15&pchannelid=468&curgclb=05&curxmlb=01,02,03,04,05,14&curIndex=1&pcurIndex=3',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1, {"gctype": "电力"}), f2
     ],


    ['gcjs_zhongbiaohx_dianli_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=518&channelids=17&pchannelid=468&curgclb=05&curxmlb=01,02,03,04,05,14&curIndex=2&pcurIndex=3',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1_zhongbiaohx, {"gctype": "电力"}), f2
     ],


    ['gcjs_zhongbiaoxx_dianli_info', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=517&channelids=18&pchannelid=468&curgclb=05&curxmlb=01,02,03,04,05,14&curIndex=3&pcurIndex=3',
     ["bh", "xmmc", "zbdw", "zbdl", "zhongbiaodw", "zhongbiaojia", "fzr", "zb_tongzhishu_bh",
         "tongzhishu_fbdate", "info"], add_info(f1_zhongbiaoxx, {"gctype": "电力"}), f2
     ],



    # 铁路

    ['gcjs_zhaobiao_tielu_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=520&channelids=15&pchannelid=469&curgclb=06&curxmlb=01,02,03,04,05,14&curIndex=1&pcurIndex=4',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1, {"gctype": "铁路"}), f2
     ],


    ['gcjs_zhongbiaohx_tielu_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=523&channelids=17&pchannelid=469&curgclb=06&curxmlb=01,02,03,04,05,14&curIndex=2&pcurIndex=4',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1_zhongbiaohx, {"gctype": "铁路"}), f2
     ],


    ['gcjs_zhongbiaoxx_tielu_info', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=522&channelids=18&pchannelid=469&curgclb=06&curxmlb=01,02,03,04,05,14&curIndex=3&pcurIndex=4',
     ["bh", "xmmc", "zbdw", "zbdl", "zhongbiaodw", "zhongbiaojia", "fzr", "zb_tongzhishu_bh",
         "tongzhishu_fbdate", "info"], add_info(f1_zhongbiaoxx, {"gctype": "铁路"}), f2
     ],




    # 水利

    ['gcjs_zhaobiao_shuili_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=525&channelids=15&pchannelid=470&curgclb=04&curxmlb=01,02,03,04,05,14&curIndex=1&pcurIndex=5',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1, {"gctype": "水利"}), f2
     ],


    ['gcjs_zsjg_shuili_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=526&channelids=16&pchannelid=470&curgclb=04&curxmlb=01,02,03,04,05,14&curIndex=2&pcurIndex=5',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1_zsjg, {"gctype": "水利"}), f2
     ],


    ['gcjs_zhongbiaohx_shuili_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=528&channelids=17&pchannelid=470&curgclb=04&curxmlb=01,02,03,04,05,14&curIndex=3&pcurIndex=5',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1_zhongbiaohx, {"gctype": "水利"}), f2
     ],

    ['gcjs_zhongbiaohx_toubiao_shuili_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=529&channelids=17&pchannelid=470&curgclb=04&curxmlb=01,02,03,04,05,14&curIndex=4&pcurIndex=5',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1_zhongbiaohx, {"gctype": "水利"}), f2
     ],

    ['gcjs_zhongbiaoxx_shuili_info', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=527&channelids=18&pchannelid=470&curgclb=04&curxmlb=01,02,03,04,05,14&curIndex=5&pcurIndex=5',
     ["bh", "xmmc", "zbdw", "zbdl", "zhongbiaodw", "zhongbiaojia", "fzr", "zb_tongzhishu_bh",
         "tongzhishu_fbdate", "info"], add_info(f1_zhongbiaoxx, {"gctype": "水利"}), f2
     ],





    # 园林
    ['gcjs_zhaobiao_yuanlin_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=543&channelids=15&pchannelid=472&curgclb=08&curxmlb=01,02,03,04,05,14&curIndex=1&pcurIndex=6',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1, {"gctype": "园林"}), f2
     ],


    ['gcjs_zsjg_yuanlin_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=544&channelids=16&pchannelid=472&curgclb=08&curxmlb=01,02,03,04,05,14&curIndex=2&pcurIndex=6',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1_zsjg, {"gctype": "园林"}), f2
     ],


    ['gcjs_zhongbiaohx_yuanlin_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=546&channelids=17&pchannelid=472&curgclb=08&curxmlb=01,02,03,04,05,14&curIndex=3&pcurIndex=6',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1_zhongbiaohx, {"gctype": "园林"}), f2
     ],

    ['gcjs_zhongbiaohx_toubiao_yuanlin_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=547&channelids=17&pchannelid=472&curgclb=08&curxmlb=01,02,03,04,05,14&curIndex=4&pcurIndex=6',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1_zhongbiaohx, {"gctype": "园林"}), f2
     ],

    ['gcjs_zhongbiaoxx_yuanlin_info', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=545&channelids=18&pchannelid=472&curgclb=08&curxmlb=01,02,03,04,05,14&curIndex=5&pcurIndex=6',
     ["bh", "xmmc", "zbdw", "zbdl", "zhongbiaodw", "zhongbiaojia", "fzr", "zb_tongzhishu_bh",
         "tongzhishu_fbdate", "info"], add_info(f1_zhongbiaoxx, {"gctype": "园林"}), f2
     ],


    # 民航
    ['gcjs_zhaobiao_minhang_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=539&channelids=15&pchannelid=471&curgclb=07&curxmlb=01,02,03,04,05,14&curIndex=1&pcurIndex=7',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1, {"gctype": "民航"}), f2
     ],

    ['gcjs_zhongbiaohx_minhang_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=542&channelids=17&pchannelid=471&curgclb=07&curxmlb=01,02,03,04,05,14&curIndex=2&pcurIndex=7',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1_zhongbiaohx, {"gctype": "民航"}), f2
     ],

    ['gcjs_zhongbiaoxx_minhang_info', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=541&channelids=18&pchannelid=471&curgclb=07&curxmlb=01,02,03,04,05,14&curIndex=3&pcurIndex=7',
     ["bh", "xmmc", "zbdw", "zbdl", "zhongbiaodw", "zhongbiaojia", "fzr", "zb_tongzhishu_bh",
         "tongzhishu_fbdate", "info"], add_info(f1_zhongbiaoxx, {"gctype": "民航"}), f2
     ],


    # 军队

    ['gcjs_zhaobiao_jundui_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=1033&channelids=9999&pchannelid=475&curgclb=&curxmlb=01,02,03,04,05,14&curIndex=1&pcurIndex=8',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1, {"gctype": "军队"}), f2
     ],

    ['gcjs_zsjg_jundui_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=1034&channelids=9999&pchannelid=475&curgclb=&curxmlb=01,02,03,04,05,14&curIndex=2&pcurIndex=8',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1_zsjg, {"gctype": "军队"}), f2
     ],


    ['gcjs_zhongbiaohx_jundui_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=1036&channelids=9999&pchannelid=475&curgclb=&curxmlb=01,02,03,04,05,14&curIndex=3&pcurIndex=8',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1_zhongbiaohx, {"gctype": "军队"}), f2
     ],

    ['gcjs_zhongbiaoxx_jundui_info', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=1035&channelids=9999&pchannelid=475&curgclb=&curxmlb=01,02,03,04,05,14&curIndex=4&pcurIndex=8',
     ["bh", "xmmc", "zbdw", "zbdl", "zhongbiaodw", "zhongbiaojia", "fzr", "zb_tongzhishu_bh",
         "tongzhishu_fbdate", "info"], add_info(f1_zhongbiaoxx, {"gctype": "军队"}), f2
     ],

    # 其它

    ['gcjs_zhaobiao_qita_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=535&channelids=15&pchannelid=474&curgclb=13&curxmlb=01,02,03,04,05,14&curIndex=1&pcurIndex=10',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1, {"gctype": "其它"}), f2
     ],

    ['gcjs_zsjg_qita_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=536&channelids=16&pchannelid=474&curgclb=13&curxmlb=01,02,03,04,05,14&curIndex=2&pcurIndex=10',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1_zsjg, {"gctype": "其它"}), f2
     ],


    ['gcjs_zhongbiaohx_qita_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=538&channelids=17&pchannelid=474&curgclb=13&curxmlb=01,02,03,04,05,14&curIndex=3&pcurIndex=10',
     ["name", "ggstart_time", "href", "info"], add_info(
         f1_zhongbiaohx, {"gctype": "其它"}), f2
     ],


    ['gcjs_zhongbiaoxx_qita_info', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/szlist.jsp?siteId=1&channelId=537&channelids=18&pchannelid=474&curgclb=13&curxmlb=01,02,03,04,05,14&curIndex=4&pcurIndex=10',
     ["bh", "xmmc", "zbdw", "zbdl", "zhongbiaodw", "zhongbiaojia", "fzr", "zb_tongzhishu_bh",
         "tongzhishu_fbdate", "info"], add_info(f1_zhongbiaoxx, {"gctype": "其它"}), f2
     ],


    ['zfcg_zhaobiao_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/zfcglist.jsp?page=1&siteId=1&channelId=456',
     ["name", "ggstart_time", "href", "info"], f1_zfcg, f2
     ],

    ['zfcg_yucai_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/zfcglist.jsp?page=1&siteId=1&channelId=448',
     ["name", "ggstart_time", "href", "info"], f1_zfcg, f2
     ],

    ['zfcg_biangeng_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/zfcglist.jsp?page=1&siteId=1&channelId=457',
     ["name", "ggstart_time", "href", "info"], f1_zfcg, f2
     ],


    ['zfcg_zhongbiao_gg', 'http://www.gzggzy.cn/cms/wz/view/index/layout2/zfcglist.jsp?page=1&siteId=1&channelId=458',
     ["name", "ggstart_time", "href", "info"], f1_zfcg, f2
     ],

]




# url="http://www.gzggzy.cn/cms/wz/view/index/layout2/zfcglist.jsp?page=1&siteId=1&channelId=456"
# driver=webdriver.Chrome()

# driver.get(url)


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省广州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(
        conp=[
            "postgres",
            "since2015",
            "192.168.3.171",
            "guangdong",
            "guangzhou_test"],
        num=1)
