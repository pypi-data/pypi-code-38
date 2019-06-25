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

_name_ = "shanxi_shenghui"


def f1(driver, num):
    locator = (By.XPATH, "//table[@cellspacing='3']/tbody/tr[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url

    locator = (By.XPATH, "//td[@class='huifont']")
    total = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = re.findall(r'(\d+)/', total)[0]
    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@cellspacing='3']/tbody/tr[last()]//a").get_attribute('href')[-40:]
        driver.execute_script("window.location.href='./?Paging={}'".format(num))
        locator = (By.XPATH, "//table[@cellspacing='3']/tbody/tr[last()]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("table", attrs={'cellspacing':'3',"valign":"top"}).tbody
    lis = div.find_all("tr")
    data = []
    for li in lis:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        span = li.find("td", align="right").text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://www.sxszbb.com' + link
        tmp = [title, span, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//table[@cellspacing='3']/tbody/tr[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//td[@class='huifont']")
    total = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'/(\d+)', total)[0]

    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@id='tblInfo'][string-length()>35]")
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
    div = soup.find('table', id='tblInfo')

    return div


data = [

    ["gcjs_zhaobiao_gg", "http://www.sxszbb.com/EpointFront/jyxx/001001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_biangeng_gg", "http://www.sxszbb.com/EpointFront/jyxx/001005/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg", "http://www.sxszbb.com/EpointFront/jyxx/001002/",
     ["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="陕西省省会", **args)
    est_html(conp, f=f3, **args)

# 网站新增：http://www.sxszbb.com/EpointFront/jyxx/
# 修改时间：2019/6/20
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "shanxi_shenghui"])

    # driver = webdriver.Chrome()
    # url = "http://www.sxszbb.com/EpointFront/jyxx/001001/"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    # #
    # driver=webdriver.Chrome()
    # url = "http://www.sxszbb.com/EpointFront/jyxx/001001/"
    # driver.get(url)
    # for i in range(11, 13):
    #     df=f1(driver, i)
    #     print(df.values)
