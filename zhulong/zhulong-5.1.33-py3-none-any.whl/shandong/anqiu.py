import json
import time
import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zhulong.util.etl import est_meta,est_html,add_info

_name_='anqiu'

def f1(driver, num):
    locator = (By.XPATH, '(//span[@class="info-name"]/a)[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = int(re.findall("Paging=(\d+)", url)[0])
    if num != cnum:
        if num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        val = driver.find_element_by_xpath("(//span[@class='info-name']/a)[1]").get_attribute('href')[-40:]
        driver.get(url)
        locator = (By.XPATH, "(//span[@class='info-name']/a)[1][not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    ul = soup.find("div", class_="info-form")
    tbody = ul.find('tbody')
    trs = tbody.find_all("tr")
    data = []
    for li in trs:
        info = {}
        a = li.find("a")
        link = "http://aqggzy.weifang.gov.cn" + a["href"]
        try:
            span1 = li.find_all("span", class_="info-date")[0].text.strip()
        except:
            span1 = "-"
        arr=li.find_all("span", class_="info-date")
        
        if len(arr)>1:
            info=json.dumps({"ggend_time":arr[1].text.strip()},ensure_ascii=False)

        else:info = None
        tmp = [a.text.strip(), span1.strip(), link, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, '(//span[@class="info-name"])[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//td[@class="huifont"]')
    page_all = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    page = re.findall(r'/(\d+)', page_all)[0]
    driver.quit()
    return int(page)


def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH,"//div[@class='detail-content'][string-length()>30]")
    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))
    before=len(driver.page_source)
    time.sleep(0.1)
    after=len(driver.page_source)
    i=0
    while before!=after:
        before=len(driver.page_source)
        time.sleep(0.1)
        after=len(driver.page_source)
        i+=1
        if i>5:break
    page=driver.page_source
    soup=BeautifulSoup(page,'html.parser')
    div=soup.find('div',class_='detail-content')
    return div


data = [
    ["gcjs_zhaobiao_gg",
    "http://aqggzy.weifang.gov.cn/anqggzy/showinfo/moreinfo_gg.aspx?type=&categorynum=004012001&Paging=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_biangeng_gg",
     "http://aqggzy.weifang.gov.cn/anqggzy/showinfo/moreinfo_gg.aspx?type=&categorynum=004012002&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_bian_da_gg",
     "http://aqggzy.weifang.gov.cn/anqggzy/showinfo/moreinfo_gg.aspx?type=&categorynum=004012005&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://aqggzy.weifang.gov.cn/anqggzy/showinfo/moreinfo_gg.aspx?type=&categorynum=004012006&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://aqggzy.weifang.gov.cn/anqggzy/showinfo/moreinfo_gg.aspx?type=&categorynum=004012007&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_liubiao_gg",
     "http://aqggzy.weifang.gov.cn/anqggzy/showinfo/moreinfo_gg.aspx?type=&categorynum=004012010&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["zfcg_yucai_gg",
     "http://aqggzy.weifang.gov.cn/anqggzy/showinfo/moreinfo_gg_zfcg_cgxq.aspx?categorynum=004002017&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://aqggzy.weifang.gov.cn/anqggzy/showinfo/moreinfo_gg_zfcgtwo.aspx?categorynum=004002001&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://aqggzy.weifang.gov.cn/anqggzy/showinfo/moreinfo_gg_zfcg.aspx?categorynum=004002011&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://aqggzy.weifang.gov.cn/anqggzy/showinfo/moreinfo_gg_zfcg.aspx?categorynum=004002012&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_liubiao_gg",
     "http://aqggzy.weifang.gov.cn/anqggzy/showinfo/moreinfo_gg_zfcg.aspx?categorynum=004002016&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_yanshou_gg",
     "http://aqggzy.weifang.gov.cn/anqggzy/showinfo/moreinfo_gg_zfcg.aspx?type=&categorynum=004002014&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["yiliao_zhaobiao_gg",
     "http://aqggzy.weifang.gov.cn/anqggzy/showinfo/moreinfo_gg_ylsb.aspx?categorynum=004006001&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'jylx':'医疗设备'}),f2],

    ["yiliao_zhongbiao_gg",
     "http://aqggzy.weifang.gov.cn/anqggzy/showinfo/moreinfo_gg_ylsb.aspx?categorynum=004006003&Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'医疗设备'}),f2],

    ["yiliao_liubiao_gg",
     "http://aqggzy.weifang.gov.cn/anqggzy/showinfo/moreinfo_gg_ylsb.aspx?categorynum=004006008&Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'医疗设备'}),f2],

    ["qsy_zhaobiao_gg",
     "http://aqggzy.weifang.gov.cn/anqggzy/showinfo/moreinfo_gg_qt.aspx?categorynum=004007001&Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其他交易'}),f2],

    ["qsy_biangeng_gg",
     "http://aqggzy.weifang.gov.cn/anqggzy/showinfo/moreinfo_gg_qt.aspx?categorynum=004007004&Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其他交易'}),f2],

    ["qsy_zhongbiao_gg",
     "http://aqggzy.weifang.gov.cn/anqggzy/showinfo/moreinfo_gg_qt.aspx?categorynum=004007002&Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其他交易'}),f2],

    ["qsy_liubiao_gg",
     "http://aqggzy.weifang.gov.cn/anqggzy/showinfo/moreinfo_gg_qt.aspx?categorynum=004007009&Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其他交易'}),f2],

]


def work(conp,**args):
    est_meta(conp=conp,data=data,diqu="山东省安丘市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.4.175","shandong","anqiu"])


