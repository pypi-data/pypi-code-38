import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zlshenpi.util.etl import add_info, est_meta, est_html, est_tbs, add_info, est_meta_large
import sys
import time
import json

_name_ = "xinjiangsheng"


def f1(driver, num):
    locator = (By.XPATH, "//table[@class='table nurmalTable']/tbody/tr[last()]//a")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//span[@class='layui-laypage-curr']")
    try:
        txt = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(txt)
    except:cnum=1

    if num != int(cnum):
        url = driver.current_url
        val = driver.find_element_by_xpath("//table[@class='table nurmalTable']/tbody/tr[last()]//a").get_attribute('onclick')
        val = re.findall(r'\(\'(.*)\'\)', val)[0].split("'")[0]

        url = re.sub('pageNo=[0-9]+', 'pageNo=%d'%num, url)
        driver.get(url)
        locator = (By.XPATH, "//table[@class='table nurmalTable']/tbody/tr[last()]//a[not(contains(@onclick, '%s'))]" % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find('table', class_='table nurmalTable').tbody
    trs = table.find_all('tr')
    data = []

    for tr in trs:
        info = {}
        a = tr.find('a')
        try:
            name = a['title'].strip()
        except:
            name = a.text.strip()
        xm_code = tr.find_all('td')[0].text.strip()
        ggstart_time = 'None'
        info['xm_code']=xm_code

        onclick = a['onclick']
        projectId =re.findall(r'\(\'(.*)\'\)', onclick)[0].split("','")[0]
        sxbh = re.findall(r'\(\'(.*)\'\)', onclick)[0].split("','")[1]
        sxzxbh = re.findall(r'\(\'(.*)\'\)', onclick)[0].split("','")[2]
        userId = re.findall(r'\(\'(.*)\'\)', onclick)[0].split("','")[3]
        cbsnum = re.findall(r'\(\'(.*)\'\)', onclick)[0].split("','")[4]

        href = 'http://www.xjtzxm.gov.cn/toTkxmblsx.jspx?projectId='+projectId+'&sxbh='+sxbh+'&sxzxbh='+sxzxbh+'&userId='+userId+'&cbsnum='+cbsnum
        try:
            shenpishixiang = tr.find_all('td')[2]['title'].strip()
        except:
            shenpishixiang = tr.find_all('td')[2].text.strip()
        info['shenpishixiang']=shenpishixiang
        shenpijieguo = tr.find_all('td')[3].text.strip()
        info['shenpijieguo']=shenpijieguo

        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:info = None
        tmp = [name,  ggstart_time,href,info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, "//a[@class='layui-laypage-last']")
    txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute('data-page')
    total_page = int(txt)
    driver.quit()
    return total_page


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@class='table nurmalTable'][string-length()>30]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

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
    div = soup.find('body')
    return div


data = [

    ["xm_jieguo_gg",
     "http://www.xjtzxm.gov.cn/toXmbljggs.jspx?pageNo=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="新疆省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres","since2015","192.168.3.171","zlshenpi","xinjiangsheng"],pageloadtimeout=120)

    # driver = webdriver.Chrome()
    # for d in data:
    #     driver.get(d[1])
    #     print(d[1])
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     df = f1(driver,4)
    #     print(df.values)
    #     for j in df[2].values:
    #         df = f3(driver, j)
    #         print(df)
