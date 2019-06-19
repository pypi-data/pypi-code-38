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

_name_ = "shanxisheng"


def f1(driver, num):
    locator = (By.XPATH, "//table[@id='materialtab']/tbody/tr[last()]/td[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='pageFlip']/a[@class='cur']")
    try:
        txt = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(txt)
    except:cnum=1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@id='materialtab']/tbody/tr[last()]/td[last()]/a").get_attribute('onclick')
        val = re.findall(r'\(\'(.*)\'\)', val)[0].split("'")[0]
        locator = (By.XPATH, "//input[@id='pageNoSelect']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).clear()
        locator = (By.XPATH, "//input[@id='pageNoSelect']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).send_keys(num)
        locator = (By.XPATH, "//div[@class='pageTurnTo']/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        locator = (By.XPATH, "//table[@id='materialtab']/tbody/tr[last()]/td[last()]/a[not(contains(@onclick, '%s'))]" % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find('table', id='materialtab').tbody
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
        ggstart_time = tr.find_all('td')[3].text.strip()
        info['xm_code']=xm_code
        href = a['onclick']
        shenbaodanwei = tr.find_all('td')[2].text.strip()
        info['shenbaodanwei']=shenbaodanwei
        state = tr.find_all('td')[4].text.strip()
        info['state']=state
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:info = None
        tmp = [name,  ggstart_time,href , info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='pageNum']/span[1]/strong")
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    total_page = int(txt)
    driver.quit()
    return total_page


def f3(driver, url):
    start_url = 'http://tzxm.shaanxi.gov.cn/tzxmweb/pages/home/approvalResult/recordquery.jsp'
    turl = driver.current_url
    if turl != start_url:
        driver.get(start_url)
    try:
        element = driver.find_element_by_xpath("//a[@class='layui-layer-ico layui-layer-close layui-layer-close1']")
        driver.execute_script("arguments[0].click()", element)
    except:
        pass
    locator = (By.XPATH, "//table[@id='materialtab']/tbody/tr[1]/td[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    driver.execute_script(url)
    locator = (By.XPATH, "//div[@class='layui-layer-content'][string-length()>30]")
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
    div = soup.find('div', class_="layui-layer-content")
    element = driver.find_element_by_xpath("//a[@class='layui-layer-ico layui-layer-close layui-layer-close1']")
    driver.execute_script("arguments[0].click()", element)
    return div


data = [

    ["xm_beian_gg",
     "http://tzxm.shaanxi.gov.cn/tzxmweb/pages/home/approvalResult/recordquery.jsp",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="陕西省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres","since2015","192.168.3.171","zlshenpi","shanxisheng"],pageLoadStrategy='none',pageloadtimeout=120)

    # driver = webdriver.Chrome()
    # for d in data:
    #     driver.get(d[1])
    #     print(d[1])
    #     # df = f2(driver)
    #     # print(df)
    #     driver.maximize_window()
    #     df = f1(driver,12)
    #     print(df.values)
    #     for j in df[2].values:
    #         print(j)
    #         df = f3(driver, j)
    #         print(df)
