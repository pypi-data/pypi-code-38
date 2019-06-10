import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

from zhulong2.util.etl import est_meta, est_html

_name_ = 'heilongjiang_yichun'


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, "//div[@class='content']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
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
    div = soup.find('div', class_='content')

    return div


def f1(driver, num):
    locator = (By.XPATH, '//table[@class="list"]/tbody/tr[position()!=1]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//table[@class="list"]/tbody/tr[2]/td/a').get_attribute("href")[-40:]
    cnum = re.findall('(\d+)/', driver.find_element_by_xpath('//div[@class="page"]/b[last()]').text)[0]
    url = driver.current_url
    if int(cnum) != int(num):
        url = re.sub("pageNo=\d+", 'pageNo=' + str(num), url)
        driver.get(url)
        # print(url)
        locator = (By.XPATH, '//table[@class="list"]/tbody/tr[2]/td/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 40).until(EC.presence_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@class="list"]/tbody/tr[position()!=1]')

    for content in content_list:
        name = content.xpath("./td/a/text()")[0].strip()
        ggstart_time = re.sub(r'\.', '-', content.xpath("./td[3]/text()")[0].strip())
        href = 'http://www.yc.gov.cn' + content.xpath("./td/a/@href")[0].strip()
        temp = [name, ggstart_time, href]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="page"]/b[last()]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    total_page = re.findall('/(\d+)', driver.find_element_by_xpath('//div[@class="page"]/b[last()]').text)[0]
    driver.quit()
    return int(total_page)


data = [

    ["zfcg_zhaobiao_gg", "http://www.yc.gov.cn/docweb/docList.action?channelId=4017&parentChannelId=3992&pageNo=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://www.yc.gov.cn/docweb/docList.action?channelId=4018&parentChannelId=3992&pageNo=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="黑龙江省伊春市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "heilongjiang_yichun"], pageloadtimeout=60,
         pageloadstrategy='none')
