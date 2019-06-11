import pandas as pd
import re
from lxml import etree
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


_name_="zhoushan"


def f1(driver, num):
    locator = (By.XPATH, "(//a[@class='WebList_sub'])[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[@class='huifont']")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall(r'(\d+)/', st)[0]
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("(//a[@class='WebList_sub'])[1]").get_attribute('href')[-35:]
        if "?Paging" not in url:
            s = "?Paging=%d" % (num) if num > 1 else "?Paging=1"
            url+=s
        elif num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        driver.get(url)
        try:
            locator = (By.XPATH, "(//a[@class='WebList_sub'])[1][not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH, "(//a[@class='WebList_sub'])[1][not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", width='98%')
    tbody = table.find("tbody")
    trs = tbody.find_all("tr", height="30")
    data = []
    for tr in trs:
        a = tr.find("a")
        link = a["href"]
        tds = tr.find("td", width="80").text
        td = re.findall(r'\[(.*)\]', tds)[0]
        tmp = [a["title"].strip(), td.strip(), "http://www.zsztb.gov.cn" + link.strip()]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f2(driver):
    if '本栏目信息正在更新中' in driver.page_source:
        return 0
    locator = (By.XPATH, "(//a[@class='WebList_sub'])[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//td[@class="huifont"]')
    str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    num = re.findall(r'/(\d+)', str)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@id='tblInfo'][string-length()>30]")
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
    div = soup.find('table', id='tblInfo')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.zsztb.gov.cn/zsztbweb/gcjs/010008/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_biangeng_gg",
     "http://www.zsztb.gov.cn/zsztbweb/gcjs/010009/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_kaibiao_gg",
     "http://www.zsztb.gov.cn/zsztbweb/gcjs/010017/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.zsztb.gov.cn/zsztbweb/gcjs/010010/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_zhonghxbiangeng_gg",
     "http://www.zsztb.gov.cn/zsztbweb/gcjs/010011/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gglx':'中标候选人补充或变更公示'}),f2],

    ["gcjs_zhongbiao_gg",
     "http://www.zsztb.gov.cn/zsztbweb/gcjs/010015/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zgysjg_gg",
     "http://www.zsztb.gov.cn/zsztbweb/gcjs/010012/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_liubiao_gg",
     "http://www.zsztb.gov.cn/zsztbweb/gcjs/010013/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["qsy_zhaobiao_gg",
     "http://www.zsztb.gov.cn/zsztbweb/xzjd/037001/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'乡镇街道交易'}),f2],

    ["qsy_zhongbiaohx_gg",
     "http://www.zsztb.gov.cn/zsztbweb/xzjd/037002/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'乡镇街道交易'}),f2],

    ["jqita_zhaobiao_gg",
     "http://www.zsztb.gov.cn/zsztbweb/qtjy/039001/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其他交易'}), f2],

    ["jqita_zhongbiao_gg",
     "http://www.zsztb.gov.cn/zsztbweb/qtjy/039002/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其他交易'}), f2],

    ["zfcg_zhaobiao_jizhong_gg",
     "http://www.zsztb.gov.cn/zsztbweb/zfcg/011001/011001001/",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'集中采购'}),f2],

    ["zfcg_zhaobiao_fensan_gg",
     "http://www.zsztb.gov.cn/zsztbweb/zfcg/011001/011001002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'分散采购'}), f2],

    ["zfcg_zhaobiao_jinjia_gg",
     "http://www.zsztb.gov.cn/zsztbweb/zfcg/011001/011001003/",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'网上竞价'}), f2],

    ["zfcg_zhaobiao_xunjia_gg",
     "http://www.zsztb.gov.cn/zsztbweb/zfcg/011001/011001004/",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'协议询价'}), f2],

    ["zfcg_biangeng_jizhong_gg",
     "http://www.zsztb.gov.cn/zsztbweb/zfcg/011002/011002001/",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'集中采购'}),f2],

    ["zfcg_biangeng_fensan_gg",
     "http://www.zsztb.gov.cn/zsztbweb/zfcg/011002/011002002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'分散采购'}), f2],

    ["zfcg_biangeng_jinjia_gg",
     "http://www.zsztb.gov.cn/zsztbweb/zfcg/011002/011002003/",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'网上竞价'}), f2],

    ["zfcg_biangeng_xunjia_gg",
     "http://www.zsztb.gov.cn/zsztbweb/zfcg/011002/011002004/",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'协议询价'}), f2],


    ["zfcg_gqita_zhong_liu_jizhong_gg",
     "http://www.zsztb.gov.cn/zsztbweb/zfcg/011004/011004001/",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'集中采购'}),f2],

    ["zfcg_gqita_zhong_liu_fensan_gg",
     "http://www.zsztb.gov.cn/zsztbweb/zfcg/011004/011004002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'分散采购'}), f2],

    ["zfcg_gqita_zhong_liu_jinjia_gg",
     "http://www.zsztb.gov.cn/zsztbweb/zfcg/011004/011004003/",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'网上竞价'}), f2],

    ["zfcg_gqita_zhong_liu_xunjia_gg",
     "http://www.zsztb.gov.cn/zsztbweb/zfcg/011004/011004004/",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'协议询价'}), f2],

    ["zfcg_gqita_jieguobiangeng_jizhong_gg",
     "http://www.zsztb.gov.cn/zsztbweb/zfcg/011005/011005003/",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'集中采购','gglx':'政府采购结果变更公告'}),f2],

    ["zfcg_gqita_jieguobiangeng_fensan_gg",
     "http://www.zsztb.gov.cn/zsztbweb/zfcg/011005/011005004/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'分散采购','gglx':'政府采购结果变更公告'}), f2],

    ["zfcg_gqita_jieguobiangeng_jinjia_gg",
     "http://www.zsztb.gov.cn/zsztbweb/zfcg/011005/011005001/",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'网上竞价','gglx':'政府采购结果变更公告'}), f2],

    ["zfcg_yucai_gg",
     "http://www.zsztb.gov.cn/zsztbweb/zfcg/011003/011003001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_yucai_danyilaiyuan_gg",
     "http://www.zsztb.gov.cn/zsztbweb/zfcg/011003/011003002/",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'单一来源'}), f2],

]



def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省舟山市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zhejiang","zhoushan"])


