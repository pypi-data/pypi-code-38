import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json

import time

from zhulong4.util.etl import est_html, est_meta, add_info

_name_ = "ecp_cgnpc_com_cn"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='infoList']/ul/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='flipPage'][1]/span[1]")
        total = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = re.findall(r'(\d+)/', total)[0]
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='infoList']/ul/li[1]/a").get_attribute('href')[-30:]
        tar = driver.find_element_by_xpath("//div[@class='infoList']/ul/li[last()]/a").get_attribute('href')[-30:]
        driver.execute_script("pageDirection.jump('{}')".format(num))

        locator = (By.XPATH, "//div[@class='infoList']/ul/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, "//div[@class='infoList']/ul/li[last()]/a[not(contains(@href, '%s'))]" % tar)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_='infoList')
    lis = div.find_all('li')
    data = []
    for li in lis:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'https://ecp.cgnpc.com.cn' + link

        span = li.find('span', class_='date').text.strip()
        tmp = [title, span, href]
        data.append(tmp)
        # f = f3(driver, href)
        # print(f)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='infoList']/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='flipPage'][1]/span[1]")
        href = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = re.findall(r'/(\d+)', href)[0]
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='myPrintArea']")
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
    div = soup.find('div', id='myPrintArea')
    return div



data = [
    ["qy_zhaobiao_gg",
     "https://ecp.cgnpc.com.cn/CmsNewsController.do?method=newsList&channelCode=zgh_zbgg&parentCode=zgh_cgxx&page=1&rp=20&param=bulletin&id=zgh_zbgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qy_fei_zhaobiao_gg",
     "https://ecp.cgnpc.com.cn/CmsNewsController.do?method=newsList&channelCode=zgh_fzbgg&parentCode=zgh_cgxx&page=1&rp=20&param=bulletin&id=zgh_fzbgg",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'非招标'}), f2],

    ["qy_zhongbiao_gg",
     "https://ecp.cgnpc.com.cn/CmsNewsController.do?method=newsList&channelCode=zgh_zhongbgg&parentCode=zgh_cgxx&page=1&rp=20&param=bulletin&id=zgh_zhongbgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qy_zhongbiao_jieguo_gg",
     "https://ecp.cgnpc.com.cn/CmsNewsController.do?method=newsList&channelCode=zgh_cgjggg&parentCode=zgh_cgxx&page=1&rp=20&param=bulletin&id=zgh_cgjggg",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'采购结果'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中国广核集团有限公司", **args)
    est_html(conp, f=f3, **args)



if __name__ == '__main__':
        work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang3", "ecp_cgnpc_com_cn"])

    # driver = webdriver.Chrome()
    # url = "https://ecp.cgnpc.com.cn/CmsNewsController.do?method=newsList&channelCode=zgh_zhongbgg&parentCode=zgh_cgxx&page=1&rp=20&param=bulletin&id=zgh_zhongbgg"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "https://ecp.cgnpc.com.cn/CmsNewsController.do?method=newsList&channelCode=zgh_zhongbgg&parentCode=zgh_cgxx&page=1&rp=20&param=bulletin&id=zgh_zhongbgg"
    # driver.get(url)
    # for i in range(1, 3):
    #     df=f1(driver, i)
    #     print(df.values)
