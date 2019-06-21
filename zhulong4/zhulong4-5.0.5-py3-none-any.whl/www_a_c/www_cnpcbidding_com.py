import time

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



from zhulong4.util.etl import est_tbs, est_meta, est_html, est_meta_large

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fqztb.com/Home/tenderList?index=3&type=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_ = 'www_cnpcbidding_com'


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="c1-body"]/div[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//option[@selected="selected"]').get_attribute('value')

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//div[@class="c1-body"]/div[1]//a').get_attribute('href')[-10:-2]

        driver.execute_script("javascript:gotoPage(%d)" % num)
        # 第二个等待
        locator = (By.XPATH, '//div[@class="c1-body"]/div[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='c1-body')
    trs = div.find_all('div', recursive=False)
    for tr in trs:
        try:
            tr = tr.find_all('div')
            name = tr[0].a['title']
            href = tr[0].a['href']
            ggstart_time = tr[1].get_text().strip()
            company = tr[1]['title']
            ggstart_time = re.findall('\d+-\d+-\d+', ggstart_time)[0]

            info = {'company': company}
            info = json.dumps(info, ensure_ascii=False)
            href=href+'+++'+mark_url
            tmp = [name, ggstart_time, href, info]
        except:
            if num==total_page_num:
                continue
            else:
                raise ValueError('未知错误')
        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    global total_page_num
    locator = (By.XPATH, '//div[@class="c1-body"]/div[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//table[@class="centertable"]//a[@id="lastPage"]').get_attribute('href')
    total = re.findall('javascript:gotoPage\((\d+?)\)', total)[0]

    total = int(total)
    total_page_num=total
    driver.quit()

    return total


def get_url(f,num):
    def inner(*args):
        global mark_url
        url_list=[
         'http://www.cnpcbidding.com/wps/portal/ebid/wcm_search/bidnotice_publish',
         'http://www.cnpcbidding.com/wps/portal/ebid/wcm_search/bidnotice_zgys',
         'http://www.cnpcbidding.com/wps/portal/ebid/wcm_search/bidresult_publish',
         'http://www.cnpcbidding.com/wps/portal/ebid/wcm_search/bidresult_publish_1']
        mark_url=url_list[num]

        return f(*args)
    return inner



def f3(driver, url):
    url1=url.split('+++')[1]
    js_url=url.split('+++')[0]

    driver.get(url1)

    locator = (By.XPATH, '//div[@class="c1-body"]/div[1]//a')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    driver.execute_script(js_url)

    locator = (By.XPATH, '(//table[@class="table_st"])[1][string-length()>10] | //div[@id="mainContent"][string-length()>10]')
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    time.sleep(0.1)
    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 10: break

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    div = soup.find('table', class_="table_st")
    if div == None:
        div=soup.find('div',id="mainContent")


    return div


data = [
    ["qy_zhaobiao_gg", "http://www.cnpcbidding.com/wps/portal/ebid/wcm_search/bidnotice_publish",["name", "ggstart_time", "href", "info"], get_url(f1,0), f2],
    ["qy_zgys_gg", "http://www.cnpcbidding.com/wps/portal/ebid/wcm_search/bidnotice_zgys",["name", "ggstart_time", "href", "info"], get_url(f1,1), f2],
    ["qy_zhongbiaohx_gg", "http://www.cnpcbidding.com/wps/portal/ebid/wcm_search/bidresult_publish",["name", "ggstart_time", "href", "info"], get_url(f1,2), f2],
    ["qy_zhongbiao_gg", "http://www.cnpcbidding.com/wps/portal/ebid/wcm_search/bidresult_publish_1",["name", "ggstart_time", "href", "info"], get_url(f1,3), f2],

]


####招标公告,邀请招标中标结果要登录才能看,没有爬取


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="中国石油", **args)
    est_html(conp, f=f3, **args)



if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch3", "www_cnpcbidding_com"])
    pass