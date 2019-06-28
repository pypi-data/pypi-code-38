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


_name_="zhejiang"



def f1(driver, num):
    locator = (By.XPATH, "//table[@width='98%']/tbody/tr[1]/td/a")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

    locator = (By.XPATH, "//td[@class='huifont']")
    str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall(r'(\d+)/', str)[0]
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@width='98%']/tbody/tr[1]/td/a").get_attribute('href')[-35:]
        if num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        driver.get(url)
        try:
            locator = (By.XPATH, "//table[@width='98%']/tbody/tr[1]/td/a[not(contains(@href, '%s'))]".format(val))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH, "//table[@width='98%']/tbody/tr[1]/td/a[not(contains(@href, '%s'))]".format(val))
            WebDriverWait(driver, 5).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table= soup.find("table", width='98%')
    tbody = table.find("tbody")
    trs = tbody.find_all("tr", height="30")
    data = []
    for tr in trs:
        a = tr.find("a")
        link = a["href"]
        tds = tr.find("td", width="80").text
        td = re.findall(r"\[(.*)\]", tds)[0]
        tmp = [a["title"].strip(), td.strip(), "http://new.zmctc.com"+link.strip()]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//table[@width='98%']/tbody/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[@class='huifont']")
    str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    num = re.findall(r'/(\d+)', str)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//td[@class='border']")
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
    div = soup.find('td', class_='border')
    return div


data = [
    ["jqita_zhaobiao_gongcheng_gg","http://new.zmctc.com/zjgcjy/jyxx/004001/004001001/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'工程'}),f2],

    ["jqita_zhaobiao_huowu_gg", "http://new.zmctc.com/zjgcjy/jyxx/004001/004001002/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'货物'}),f2],

    ["jqita_zhaobiao_fuwu_gg", "http://new.zmctc.com/zjgcjy/jyxx/004001/004001003/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'服务'}),f2],


    ["jqita_biangeng_gongcheng_gg", "http://new.zmctc.com/zjgcjy/jyxx/004002/004002001/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'工程'}),f2],

    ["jqita_biangeng_huowu_gg", "http://new.zmctc.com/zjgcjy/jyxx/004002/004002002/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'货物'}),f2],

    ["jqita_biangeng_fuwu_gg", "http://new.zmctc.com/zjgcjy/jyxx/004002/004002003/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'服务'}),f2],

    ["jqita_gqita_xmdj_gongcheng_gg", "http://new.zmctc.com/zjgcjy/jyxx/004003/004003001/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'工程','gglx':'项目登记'}),f2],

    ["jqita_gqita_xmdj_huowu_gg", "http://new.zmctc.com/zjgcjy/jyxx/004003/004003002/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'货物','gglx':'项目登记'}),f2],

    ["jqita_gqita_xmdj_fuwu_gg", "http://new.zmctc.com/zjgcjy/jyxx/004003/004003003/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'服务','gglx':'项目登记'}),f2],

    ["jqita_kaibiao_gongcheng_gg", "http://new.zmctc.com/zjgcjy/jyxx/004004/004004001/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'工程'}),f2],

    ["jqita_kaibiao_huowu_gg", "http://new.zmctc.com/zjgcjy/jyxx/004004/004004002/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'货物'}),f2],

    ["jqita_kaibiao_fuwu_gg", "http://new.zmctc.com/zjgcjy/jyxx/004004/004004003/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'服务'}),f2],
    ###

    ["jqita_zgys_gongcheng_gg", "http://new.zmctc.com/zjgcjy/jyxx/004005/004005001/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'工程'}), f2],

    ["jqita_zgys_huowu_gg", "http://new.zmctc.com/zjgcjy/jyxx/004005/004005002/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'货物'}), f2],

    ["jqita_zhongbiaohx_gongcheng_gg", "http://new.zmctc.com/zjgcjy/jyxx/004006/004006001/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'工程'}),f2],

    ["jqita_zhongbiaohx_huowu_gg", "http://new.zmctc.com/zjgcjy/jyxx/004006/004006002/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'货物'}),f2],

    ["jqita_zhongbiaohx_fuwu_gg", "http://new.zmctc.com/zjgcjy/jyxx/004006/004006003/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'服务'}),f2],

    ["jqita_hetong_gg", "http://new.zmctc.com/zjgcjy/jyxx/004007/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gongcheng_gg", "http://new.zmctc.com/zjgcjy/jyxx/004010/004010001/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'工程'}),f2],

    ["jqita_zhongbiao_huowu_gg", "http://new.zmctc.com/zjgcjy/jyxx/004010/004010002/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'货物'}),f2],

    ["jqita_zhongbiao_fuwu_gg", "http://new.zmctc.com/zjgcjy/jyxx/004010/004010003/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'服务'}),f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省省级",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zhejiang","zhejiang"])



