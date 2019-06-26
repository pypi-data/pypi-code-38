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

_name_ = "qinghaisheng"


def f1(driver, num):
    locator = (By.XPATH, "//table[@class='search-sub-detail tcollapse list_table']/tbody/tr[(contains(@class, 'search-top'))][1]/td[1]/a")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='qmanu']")
    try:
        txt = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(re.findall('\d+', txt)[2])
    except:cnum=1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@class='search-sub-detail tcollapse list_table']/tbody/tr[(contains(@class, 'search-top'))][1]/td[1]/a").get_attribute('onclick')
        val = re.findall(r'\(\'(.*)\'\)', val)[0]
        locator = (By.XPATH, "//input[@id='pageNum']")
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).clear()
        locator = (By.XPATH, "//input[@id='pageNum']")
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).send_keys(num)
        driver.execute_script('goToPage();')
        locator = (By.XPATH, "//table[@class='search-sub-detail tcollapse list_table']/tbody/tr[(contains(@class, 'search-top'))][1]/td[1]/a[not(contains(@onclick, '%s'))]" % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find('table', class_='search-sub-detail tcollapse list_table').tbody
    trs = table.find_all('tr', class_='search-top')
    data = []
    for tr in trs:
        info = {}
        a = tr.find_all('a')[-1]
        try:
            name = tr.find_all('td')[1]['title'].strip()
        except:
            name = a.text.strip()
        td1 = tr.find_all('td')[0]
        try:
            xm_code = td1['title'].strip()
        except:
            xm_code = td1.text.strip()
        ggstart_time = tr.find_all('td')[-1].text.strip()
        info['xm_code']=xm_code
        onclick = re.findall(r'\(\'(.*)\'\)', a['onclick'])[0]
        href = 'http://www.qhtzxm.gov.cn'+onclick

        shenpishixiang = tr.find_all('td')[2]['title'].strip()
        info['shenpishixiang']=shenpishixiang
        shenpibumen = tr.find_all('td')[3]['title'].strip()
        info['shenpibumen']=shenpibumen
        shenpijieguo = tr.find_all('td')[4].text.strip()
        info['shenpijieguo']=shenpijieguo
        pifuwenhao = tr.find_all('td')[5]['title'].strip()
        info['pifuwenhao']=pifuwenhao
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:info = None
        tmp = [name,  ggstart_time,href,info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='qmanu']")
    txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    total_page = int(re.findall('\d+', txt)[0])
    driver.quit()
    return total_page


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='regmain'][string-length()>40]")
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('div', id='regmain')
    return div


data = [

    ["xm_jieguo_gg",
     "http://www.qhtzxm.gov.cn/tzxmspweb/portalopenPublicInformation.do?method=queryExamineAll",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="青海省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres","since2015","192.168.3.171","zlshenpi","qinghaisheng"],pageloadtimeout=120)

    # driver = webdriver.Chrome()
    # for d in data:
    #     driver.get(d[1])
    #     print(d[1])
    #     # df = f2(driver)
    #     # print(df)
    #     driver.maximize_window()
    #     df = f1(driver,4)
    #     print(df.values)
    #     for j in df[2].values:
    #         df = f3(driver, j)
    #         print(df)
