import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command,db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs


_name_="shengzhou"

def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='ewb-work-items']/li[1]/a")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-35:]
    try:
        locator = (By.XPATH, "//a[@class='ewb-page-default ewb-page-number ewb-page-family']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = str.split('/')[0]
    except:
        cnum = 1
    if num != int(cnum):
        driver.execute_script("ShowAjaxNewPage(window.location.pathname,'categorypagingcontent',{})".format(num))
        locator = (By.XPATH, "//ul[@class='ewb-work-items']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("ul", class_="ewb-work-items")
    trs = table.find_all("li")
    data = []
    for tr in trs:
        a = tr.find("a")
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()
        try:
            link = a["href"]
        except:
            link = '-'
        td = tr.find("span", class_="r ewb-work-date").text.strip()
        link = "http://220.191.224.142"+link.strip()
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f2(driver):
    # url = driver.current_url
    locator = (By.XPATH, "//ul[@class='ewb-work-items']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//a[@class='ewb-page-default ewb-page-number ewb-page-family']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = str.split('/')[1]
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='article-block']")
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
    div = soup.find('div', class_="article-block")
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://220.191.224.142/TPFront/jsxmjy/011001/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiaohx_gg",
     "http://220.191.224.142/TPFront/jsxmjy/011002/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://220.191.224.142/TPFront/jsxmjy/011003/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhaobiao_gg",
     "http://220.191.224.142/TPFront/zfcg/012001/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhongbiao_gg",
     "http://220.191.224.142/TPFront/zfcg/012002/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_biangeng_gg",
     "http://220.191.224.142/TPFront/zfcg/012003/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_yucai_gg",
     "http://220.191.224.142/TPFront/zfcg/012004/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_gqita_zhao_liu_gg",
     "http://220.191.224.142/TPFront/xzbm/022001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'乡镇(街道)、部门'}), f2],

    ["qsy_biangeng_gg",
     "http://220.191.224.142/TPFront/xzbm/022002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'乡镇(街道)、部门'}), f2],

    ["qsy_gqita_zhong_liu_gg",
     "http://220.191.224.142/TPFront/xzbm/022003/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'乡镇(街道)、部门'}), f2],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省嵊州市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zhejiang","shengzhou"])

