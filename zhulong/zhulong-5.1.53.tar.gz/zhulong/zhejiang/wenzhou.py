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


_name_="wenzhou"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='List-Li FloatL']/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='Zy-Page FloatL']/div")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall(r'(\d+)/', st)[0]
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='List-Li FloatL']/ul/li[1]/a").get_attribute("href")[-15:]
        if "index.htm" in url:
            s = "index_%d" % (num) if num > 1 else "index_1"
            url = re.sub("index", s, url)
        elif num == 1:
            url = re.sub("index_[0-9]*", "index_1", url)
        else:
            s = "index_%d" % (num) if num > 1 else "index_1"
            url = re.sub("index_[0-9]*", s, url)
        driver.get(url)
        try:
            locator = (By.XPATH, "//div[@class='List-Li FloatL']/ul/li[1]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH, "//div[@class='List-Li FloatL']/ul/li[1]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("div", class_='List-Li FloatL')
    ul = table.find('ul')
    trs = ul.find_all("li")
    data = []
    for tr in trs:
        info = {}
        a = tr.find("a")
        if a.find('em'):
            gglx = a.find('em').extract().text.strip()
            info['gglx'] = gglx
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()
        td = tr.find("span").text.strip()
        link = "https://ggzy.wzzbtb.com" + a["href"].strip()
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = None
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='List-Li FloatL']/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//div[@class='Zy-Page FloatL']/div")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    num = re.findall(r'/(\d+)', st)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='Content-Main FloatL']")
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
    div = soup.find('div', class_='Content-Main FloatL')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "https://ggzy.wzzbtb.com/wzcms/gcjszbgg/index.htm",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiaohx_gg",
     "https://ggzy.wzzbtb.com/wzcms/gcjshxgs/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "https://ggzy.wzzbtb.com/wzcms/gcjszbjg/index.htm",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_bian_da_gg",
     "https://ggzy.wzzbtb.com/wzcms/gcjsdybc/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "https://ggzy.wzzbtb.com/wzcms/zfcgcggg/index.htm",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhongbiao_gg",
     "https://ggzy.wzzbtb.com/wzcms/zfcgzbgg/index.htm",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_gqita_bian_liu_gg",
     "https://ggzy.wzzbtb.com/wzcms/zfcgdybc/index.htm",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_gqita_zhao_zhong_xunjia_gg",
     "https://ggzy.wzzbtb.com/wzcms/zxxjgg/index.htm",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'在线询价'}),f2],

    ["yiliao_gqita_zhao_zhong_gg",
     "https://ggzy.wzzbtb.com/wzcms/ypcgcggg/index.htm",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'药品采购'}), f2],

    ["yiliao_zhongbiao_gg",
     "https://ggzy.wzzbtb.com/wzcms/ypcgzbgg/index.htm",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'药品采购'}), f2],

    ["yiliao_gqita_bian_da_gg",
     "https://ggzy.wzzbtb.com/wzcms/ypcgbcdy/index.htm",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'药品采购'}), f2],

    ["qsy_gqita_zhao_bian_gg",
     "https://ggzy.wzzbtb.com/wzcms/gqcgcggg/index.htm",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'国企采购'}), f2],

    ["qsy_zhongbiao_gg",
     "https://ggzy.wzzbtb.com/wzcms/gqcgzbgg/index.htm",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'国企采购'}), f2],

    ["qsy_gqita_bian_da_gg",
     "https://ggzy.wzzbtb.com/wzcms/gqcgdybc/index.htm",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'国企采购'}), f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省温州市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zhejiang","wenzhou"],pageloadtimeout=120)


