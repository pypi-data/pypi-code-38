import json
import time
import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver import ActionChains, DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs


_name_="hainan"


def f1(driver, num):
    locator = (By.XPATH, "//table[@class='newtable']/tbody/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='pagesite']/div")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall(r'(\d+)/', st)[0]
    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@class='newtable']/tbody/tr[1]/td/a").get_attribute('href')[-15:]
        if num == 1:
            driver.execute_script("location.href=encodeURI('index.jhtml');")
        else:
            driver.execute_script("location.href=encodeURI('index_{}.jhtml');".format(num))

        locator = (By.XPATH, "//table[@class='newtable']/tbody/tr[1]/td/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table= soup.find("table", class_="newtable")
    tbody = table.find("tbody")
    trs = tbody.find_all("tr")
    data = []
    for tr in trs[:-1]:
        info = {}
        if tr.find_all("td")[1]:
            diqu = tr.find_all("td")[1].text.strip()
            if diqu:
                info['diqu'] = diqu
        a = tr.find("a")
        if a == None:
            continue
        link = a["href"]
        td = tr.find_all("td")[-1].text.strip()
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = None
        tmp = [a["title"].strip(), td.strip(), link.strip(), info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df



def f2(driver):
    locator = (By.XPATH, "//table[@class='newtable']/tbody/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='pagesite']/div")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    num = re.findall(r'/(\d+)', st)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='newsTex'][string-length()>30]")
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
    div = soup.find('div', class_="newsTex")
    return div


data = [
    ["gcjs_zhaobiao_gg", "http://zw.hainan.gov.cn/ggzy/ggzy/jgzbgg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg", "http://zw.hainan.gov.cn/ggzy/ggzy/jgzbgs/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_bian_liu_gg", "http://zw.hainan.gov.cn/ggzy/ggzy/jsqtgg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://zw.hainan.gov.cn/ggzy/ggzy/cggg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg", "http://zw.hainan.gov.cn/ggzy/ggzy/cgzbgg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_bian_liu_gg", "http://zw.hainan.gov.cn/ggzy/ggzy/zfcgqtgg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["yiliao_gqita_tongzhi_gg", "http://zw.hainan.gov.cn/ggzy/ggzy/yygg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'jylx':'医药医械','gglx':'医药公告'}), f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="海南省海南市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","hainan","hainan"])

