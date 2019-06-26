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


_name_="yueqing"




def f1(driver, num):
    url = driver.current_url
    locator = (By.XPATH, "//*[@id='DDLInfo']/tbody/tr[1]/td/li/div/a")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    locator = (By.XPATH, "//td[@class='huifont']")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = re.findall(r'(\d+)/', st)[0]
    if num != int(cnum):
        val = driver.find_element_by_xpath("//*[@id='DDLInfo']/tbody/tr[1]/td/li/div/a").get_attribute('href')[-40:]
        if num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        driver.get(url)
        try:
            locator = (By.XPATH, "//*[@id='DDLInfo']/tbody/tr[1]/td/li/div/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH, "//*[@id='DDLInfo']/tbody/tr[1]/td/li/div/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", id="DDLInfo")
    trs = table.find_all("tr")
    data = []
    for tr in trs:
        info = {}
        a = tr.find("a")
        if a.find('font', color="red"):
            diqu = a.find('font', color="red").text.strip()
            info['diqu'] = diqu
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()
        link = a["href"]
        td = tr.find("span", class_="wb-data-date").text.strip()
        links = "http://www.yqztb.gov.cn/yqweb/"+link.split('/', maxsplit=1)[1].strip()
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = None
        tmp = [title, td, links, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df




def f2(driver):
    locator = (By.XPATH, "//*[@id='DDLInfo']/tbody/tr[1]/td/li/div/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//td[@class='huifont']")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'/(\d+)', st)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    if 'Sorry, Page Not Found' in driver.page_source:
        return 404
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
     "http://www.yqztb.gov.cn/yqweb/ShowInfo/ShowSearchInfo.aspx?CategoryNum=001009001&Eptr3=&Paging=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_zhaobiaowenjian_gg",
     "http://www.yqztb.gov.cn/yqweb/ShowInfo/ShowSearchInfo.aspx?CategoryNum=001009002&Eptr3=&Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gglx':'招标文件'}), f2],

    ["gcjs_gqita_bian_da_gg",
     "http://www.yqztb.gov.cn/yqweb/ShowInfo/ShowSearchInfo.aspx?CategoryNum=001009003&Eptr3=&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.yqztb.gov.cn/yqweb/ShowInfo/ShowSearchInfo.aspx?CategoryNum=001009004&Eptr3=&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://www.yqztb.gov.cn/yqweb/ShowInfo/ShowSearchInfo.aspx?CategoryNum=001009005&Eptr3=&Paging=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_kaibiao_gg",
     "http://www.yqztb.gov.cn/yqweb/ShowInfo/ShowSearchInfo.aspx?CategoryNum=001009009&Eptr3=&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ####
    ["zfcg_zhaobiao_gg",
     "http://www.yqztb.gov.cn/yqweb/ShowInfo/ShowSearchInfo.aspx?CategoryNum=001010001&Eptr3=&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://www.yqztb.gov.cn/yqweb/ShowInfo/ShowSearchInfo.aspx?CategoryNum=001010002&Eptr3=&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://www.yqztb.gov.cn/yqweb/ShowInfo/ShowSearchInfo.aspx?CategoryNum=001010003&Eptr3=&Paging=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_yucai_gg",
     "http://www.yqztb.gov.cn/yqweb/ShowInfo/ShowSearchInfo.aspx?CategoryNum=001010005&Eptr3=&Paging=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省乐清市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zhejiang","yueqing"])

