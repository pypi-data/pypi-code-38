import math

import pandas as pd
import re
from lxml import etree
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

from zhulong2.util.etl import est_meta, est_html, add_info

_name_ = 'jilin_changchun'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="details"]')
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
    div = soup.find('div', class_='details')
    return div


def f1(driver, num):
    locator = (By.XPATH, '//*[@id="row"]/tbody/tr[1]/td[1]/a')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//*[@id="row"]/tbody/tr[1]/td[1]/a').get_attribute("href")[-40:]
    cnum = driver.find_element_by_xpath('//font[@color="red"]/strong').text
    # print('val', val, 'cnum', cnum,'num',num)
    if int(cnum) != int(num):
        url = driver.current_url
        url = re.sub(r'd-16544-p=\d+', 'd-16544-p=' + str(num), url)
        driver.get(url)
        locator = (By.XPATH, '//*[@id="row"]/tbody/tr[1]/td[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//*[@id="row"]/tbody/tr')
    for content in content_list:
        name = content.xpath("./td/a/text()")[0].strip()
        ggstart_time = content.xpath("./td[last()]/text()")[0].strip()
        url1 = "http://www.cczfcg.gov.cn" + content.xpath("./td/a/@href")[0]
        temp = [name, ggstart_time, url1]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//span[@class="pagebanner"]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    total_num = int(re.sub(',', '', re.findall(r'共 ([^ ]+) 条记录',
                                               driver.find_element_by_xpath('//span[@class="pagebanner"]').text)[0]))
    numPerPage = len(driver.find_elements_by_xpath('//*[@id="row"]/tbody/tr'))
    total_page = math.ceil(total_num / numPerPage)
    driver.quit()
    return int(total_page)


data = [

    ["zfcg_zhaobiao_shiqu_gg", "http://www.cczfcg.gov.cn/article/bid_list.action?field=1&d-16544-p=1&getList=&type=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'市区'}), f2],
    ["zfcg_zhaobiao_xianqu_gg", "http://www.cczfcg.gov.cn/article/bid_list.action?field=2&d-16544-p=1&getList=&type=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'县区'}), f2],
    ["zfcg_zhaobiao_waifu_gg", "http://www.cczfcg.gov.cn/article/news_list.action?d-16544-p=1&getList=&type=13",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'外阜'}), f2],
    ["zfcg_zhongbiao_shiqu_gg", "http://www.cczfcg.gov.cn/article/bid_list.action?field=1&d-16544-p=1&getList=&type=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'市区'}), f2],
    ["zfcg_zhongbiao_xianqu_gg", "http://www.cczfcg.gov.cn/article/bid_list.action?field=2&d-16544-p=1&getList=&type=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'县区'}), f2],
    ["zfcg_zhongbiao_waihu_gg", "http://www.cczfcg.gov.cn/article/news_list.action?d-16544-p=1&getList=&type=14",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'外阜'}), f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="吉林省长春市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "jilin_changchun"])
