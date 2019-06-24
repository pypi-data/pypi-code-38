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

from zhulong3.util.etl import est_html, est_meta, add_info

_name_ = "sichuan_zigong"


def f1(driver, num):
    locator = (By.XPATH, "//section[@id='portlet_cms2_WAR_CMSportlet']//div[@class='portlet-body']/div/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    try:
        locator = (By.XPATH, '//div[@class="lfr-pagination-page-selector"]//option[@selected="selected"]')
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//section[@id='portlet_cms2_WAR_CMSportlet']//div[@class='portlet-body']/div/ul/li[1]/a").get_attribute('href')[-20:]
        s = Select(driver.find_element_by_xpath('//div[@class="lfr-pagination-page-selector"]/div/select'))
        s.select_by_visible_text("{}".format(num))

        locator = (By.XPATH, "//section[@id='portlet_cms2_WAR_CMSportlet']//div[@class='portlet-body']/div/ul/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    section = soup.find("section", id='portlet_cms2_WAR_CMSportlet')
    div = section.find("div", class_='portlet-body').div.ul
    lis = div.find_all("li")
    data = []
    for li in lis:
        try:
            a = li.find("a")
            try:
                title = a['title'].strip()
            except:
                title = a.text.strip()
            span = li.find("span").text.strip()
            span = re.findall(r'\[(.*)\]', span)[0]
            link = a["href"]
            if 'http' in link:
                href = link
            else:
                href = 'http://www.zg.gov.cn' + link
        except:
            continue
        tmp = [title, span, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//section[@id='portlet_cms2_WAR_CMSportlet']//div[@class='portlet-body']/div/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//div[@class="lfr-pagination-page-selector"]/div/select/option[last()]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    li = driver.find_element_by_xpath('//div[@class="lfr-pagination-page-selector"]/div/select/option[last()]').text.strip()
    total = int(li)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@class='content-table']")
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
    div = soup.find('table', class_='content-table')
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [

    ["gcjs_zhaobiao_gg", "http://www.zg.gov.cn/web/scxzfbzj/-18",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zhongbiaohx_gg", "http://www.zg.gov.cn/web/scxzfbzj/-27",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_gqita_bian_bu_gg", "http://www.zg.gov.cn/web/scxzfbzj/-29",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]



def work(conp, **args):
    est_meta(conp, data=data, diqu="四川省自贡市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "sichuan_zigong"])

    # driver = webdriver.Chrome()
    # url = "http://www.zg.gov.cn/web/scxzfbzj/-18"
    # driver.get(url)
    # df = f2(driver)
    # print(df)

    # driver=webdriver.Chrome()
    # url = "http://www.zg.gov.cn/web/scxzfbzj/-18"
    # driver.get(url)
    # for i in range(3, 6):
    #     df=f1(driver, i)
    #     print(df.values)
