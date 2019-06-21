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

_name_ = "gansu_shenghui"


def f1(driver, num):
    locator = (By.XPATH, "(//td[@class='list1'])[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        locator = (By.XPATH, "//li[@class='thisclass']")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("(//td[@class='list1'])[1]//a").get_attribute('href')[-30:]
        s = Select(driver.find_element_by_name('sldd'))
        s.select_by_visible_text('{}'.format(num))

        locator = (By.XPATH, "(//td[@class='list1'])[1]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    lis = soup.find_all("td", attrs={'class':'list1','colspan':'2'})
    data = []
    for li in lis:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()

        span = li.find("font", color="#666666").text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://www.gsgcjs.com' + link
        tmp = [title, span, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "(//td[@class='list1'])[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//select[@name='sldd']/option[last()]")
        num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@cellpadding='2']")
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
    div = soup.find('table', cellpadding='2')
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.gsgcjs.com/a/jiaoyixinxi/zhaobiaoxinxi/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://www.gsgcjs.com/a/jiaoyixinxi/zhongbiaoxinxi/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="甘肃省省会", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "gansu_shenghui"])

    # driver = webdriver.Chrome()
    # url = "http://www.gsgcjs.com/a/jiaoyixinxi/zhaobiaoxinxi/"
    # driver.get(url)
    # df = f2(driver)
    # print(df)

    # driver=webdriver.Chrome()
    # url = "http://www.gsgcjs.com/a/jiaoyixinxi/zhaobiaoxinxi/"
    # driver.get(url)
    # for i in range(3, 5):
    #     df=f1(driver, i)
    #     print(df.values)
