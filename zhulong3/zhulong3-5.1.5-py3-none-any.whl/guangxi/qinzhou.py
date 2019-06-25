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

from zhulong3.util.etl import est_html, est_meta, add_info

_name_ = "guangxi_qinzhou"


def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="ul5_list mt20"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        if 'index' not in url:
            cnum = 1
        else:
            cnum = int(re.findall(r'index_(\d+)', url)[0])
            cnum += 1
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath('//ul[@class="ul5_list mt20"]/li[1]/a').get_attribute('href')[-20:]

        if "index" not in url:
            s = "index_%d.html" % (num-1) if num > 1 else "index.html"
            url = url + s
        elif num == 1:
            url = re.sub("index_[0-9]*", "index", url)
        else:
            s = "index_%d" % (num-1) if num > 1 else "index"
            url = re.sub("index_[0-9]*", s, url)
            # print(cnum)
        driver.get(url)

        locator = (By.XPATH, "//ul[@class='ul5_list mt20']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("ul", class_='ul5_list mt20')
    lis = div.find_all("li", attrs={'style':''})
    data = []
    for li in lis:
        try:
            a = li.find("a")
            try:
                title = a['title'].strip()
            except:
                title = a.text.strip()
            span = li.find("span").text.strip()
            link = a["href"]
            if 'http' in link:
                href = link
            else:
                href = 'http://www.qzjgw.gov.cn/' + link
        except:
            continue
        tmp = [title, span, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="ul5_list mt20"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, '//div[@class="fenye"]/a[last()-1]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        li = driver.find_element_by_xpath('//div[@class="fenye"]/a[last()-1]').text
    except:
        li = 1
    total = int(li)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='lbyBox']")
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
    div = soup.find('div', class_='lbyBox')
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [

    ["gcjs_gqita_zhao_zhong_gg", "http://www.qzjgw.gov.cn/hygl/zbgg/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zhongbiao_gg", "http://www.qzjgw.gov.cn/hygl/zbgs/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_yucai_piqian_gg", "http://www.qzjgw.gov.cn/hygl/pqgs/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gglx':'批前公示'}), f2],
    #
    ["gcjs_yucai_pihou_gg", "http://www.qzjgw.gov.cn/hygl/phgs/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gglx':'批后公示'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广西省钦州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "guangxi_qinzhou"])

    # driver = webdriver.Chrome()
    # url = "http://www.qzjgw.gov.cn/hygl/zbgg/"
    # driver.get(url)
    # df = f2(driver)
    # print(df)

    # driver=webdriver.Chrome()
    # url = "http://www.qzjgw.gov.cn/hygl/zbgg/"
    # driver.get(url)
    # for i in range(1, 6):
    #     df=f1(driver, i)
    #     print(df.values)
