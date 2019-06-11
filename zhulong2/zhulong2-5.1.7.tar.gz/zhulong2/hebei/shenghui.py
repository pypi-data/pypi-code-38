import json

import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from zhulong2.util.etl import est_meta, est_html, add_info

_name_ = 'hebei_shenghui'


def f3(driver, url):

    driver.get(url)
    locator = (By.XPATH, "//table[@width='1002']/tbody/tr/td/table[@width='930']")
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
    div = soup.find_all('table', width='930')[0]
    return div


def f1(driver, num):
    locator = (By.XPATH, "//tr[@id='biaoti']")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//tr[@id='biaoti']/td/a").get_attribute("href")[-60:]

    cnum = int(driver.find_element_by_xpath("//div[@id='outlinebar']/span").text)
    # print('val', val, 'cnum', cnum)
    if int(cnum) != int(num):
        url = driver.current_url
        url = re.sub('page=\d+?', 'page=' + str(num), url, count=1)
        driver.get(url)
        locator = (By.XPATH, '//tr[@id="biaoti"]/td/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    locator = (By.XPATH, "//tr[@id='biaoti']")
    WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//tr[@id='biaoti']")
    date_time_list = body.xpath("//tr[@bgcolor='#E3EDF6']")
    for content, date in zip(content_list, date_time_list):
        name = content.xpath("./td/a/text()")[0].strip()
        ggstart_time = date.xpath("./td[2]/span[1]/text()")[0].strip()
        url = content.xpath("./td/a/@href")[0]
        area = date.xpath("./td[2]/span[2]/text()")[0].strip()
        purchaser = date.xpath("./td[2]/span[3]/text()")[0].strip()
        info = json.dumps({'area':area,"purchaser":purchaser},ensure_ascii=False)
        temp = [name, ggstart_time, url, info]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, '//*[@id="outlinebar"]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    if '尾页' in driver.page_source:
        driver.find_element_by_xpath('//*[@id="outlinebar"]/a[contains(string(),"尾页")]').click()
    total_page = driver.find_element_by_xpath('//*[@id="outlinebar"]/span[last()]').text
    # print('total_page', total_page)
    driver.quit()
    return int(total_page)


data = [
    #
    ["zfcg_zhaobiao_gg",
     "http://search.hebcz.gov.cn:8080/was5/web/search?page=1&channelid=228483&perpage=50&outlinepage=10&lanmu=zbgg&morelanmu=province",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://search.hebcz.gov.cn:8080/was5/web/search?page=1&channelid=228483&perpage=50&outlinepage=10&lanmu=zhbgg&morelanmu=province",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg",
     "http://search.hebcz.gov.cn:8080/was5/web/search?page=1&channelid=228483&perpage=50&outlinepage=10&lanmu=fbgg&morelanmu=province",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://search.hebcz.gov.cn:8080/was5/web/search?page=1&channelid=228483&perpage=50&outlinepage=10&lanmu=gzgg&morelanmu=province",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_danyilaiyuan_gg",
     "http://search.hebcz.gov.cn:8080/was5/web/search?page=1&channelid=228483&perpage=50&outlinepage=10&lanmu=dyly&morelanmu=province",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'zblx':'单一来源'}), f2],
]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="河北省", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "hebei"])
