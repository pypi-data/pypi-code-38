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


_name_="quzhou"


num_list = []

def f1(driver, num):
    url = driver.current_url
    locator = (By.XPATH, "(//ul[@class='ewb-news-items']/li/a)[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//li[@class='ewb-page-li ewb-page-noborder ewb-page-num']/span")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall(r'(\d+)/', st)[0]
    if num != int(cnum):
        val = driver.find_element_by_xpath("(//ul[@class='ewb-news-items']/li/a)[1]").get_attribute('href')[-30:]
        if num == 1:
            url = re.sub("/[0-9]*\.html", "/1.html", url)
        else:
            s = "/%d.html" % (num) if num > 1 else "/1.html"
            url = re.sub("/[0-9]*\.html", s, url)
        driver.get(url)
        locator = (By.XPATH, "(//ul[@class='ewb-news-items']/li/a)[1][not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("ul", class_='ewb-news-items')
    trs = table.find_all("li")
    data = []
    for tr in trs:
        a = tr.find("a")
        link = a["href"]
        td = tr.find("span", class_="ewb-news-date").text
        tmp = [a["title"].strip(), td.strip(), "http://www.qzggzy.com" + link.strip()]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "(//ul[@class='ewb-news-items']/li/a)[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//li[@class='ewb-page-li ewb-page-noborder ewb-page-num']/span")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    num = re.findall(r'/(\d+)', st)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='ewb-details-info'] | //div[@class='ewb-info-con']")
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
    div = soup.find('div', class_='ewb-details-info')
    if div == None:
        div = soup.find('div', class_='ewb-info-con')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.qzggzy.com/jyxx/002001/002001001/1.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_biangeng_gg",
     "http://www.qzggzy.com/jyxx/002001/002001002/1.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_kaibiao_gg",
     "http://www.qzggzy.com/jyxx/002001/002001003/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.qzggzy.com/jyxx/002001/002001004/1.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiao_gg",
     "http://www.qzggzy.com/jyxx/002001/002001006/1.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhaobiao_gg",
     "http://www.qzggzy.com/jyxx/002002/002002001/1.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_gqita_zhong_liu_gg",
     "http://www.qzggzy.com/jyxx/002002/002002002/1.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_hetong_gg",
     "http://www.qzggzy.com/jyxx/002002/002002003/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhao_yu_gg",
     "http://www.qzggzy.com/jyxx/002002/002002004/1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'单一来源'}), f2],

    ["zfcg_biangeng_gg",
     "http://www.qzggzy.com/jyxx/002002/002002005/1.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["qsy_zhaobiao_gg",
     "http://www.qzggzy.com/jyxx/002004/002004001/002004001001/1.html",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'其他交易'}), f2],

    ["qsy_biangeng_gg",
     "http://www.qzggzy.com/jyxx/002004/002004002/002004002001/1.html",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'其他交易'}), f2],

    ["qsy_gqita_zhong_liu_gg",
     "http://www.qzggzy.com/jyxx/002004/002004004/002004004001/1.html",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'其他交易'}), f2],

    ["qsy_gqita_zhao_zhong_liu_gg",
     "http://www.qzggzy.com/jyxx/002004/002004003/002004003001/1.html",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'其他交易'}), f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省衢州市",**args)
    est_html(conp,f=f3,**args)


# 网站数据减少，需保存历史数据，删除gg,重跑
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zhejiang","quzhou"])



