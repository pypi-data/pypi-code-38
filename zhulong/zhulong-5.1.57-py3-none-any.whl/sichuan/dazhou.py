import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command,db_query
from selenium.webdriver import DesiredCapabilities
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


_name_="dazhou"





def f1(driver, num):
    locator = (By.XPATH, "//div[@class='morecontent']/table/tbody/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[@class='huifont']")
    str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = re.findall(r'(\d+)/', str)[0]
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='morecontent']/table/tbody/tr[1]/td/a").get_attribute('href')[-45:]
        if "Paging" not in url:
            s = "?Paging=%d" % (num) if num > 1 else "?Paging=1"
            url = url + s
        elif num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        driver.get(url)
        try:
            locator = (By.XPATH, "//div[@class='morecontent']/table/tbody/tr[1]/td/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH, "//div[@class='morecontent']/table/tbody/tr[1]/td/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("div", class_="morecontent")
    trs = table.find_all("tr", class_='trfont')
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title = a.text.strip()
        except:
            title = a['title'].strip()
        link = "http://www.dzggzy.cn" + a['href'].strip()
        td = tr.find("td", align="right").text.strip()
        span = re.findall(r'\[(.*)\]', td)[0]
        tmp = [title, span, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='morecontent']/table/tbody/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[@class='huifont']")
    str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'/(\d+)', str)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@width='887'][string-length()>40]")
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
    div = soup.find('table', width="887")
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.dzggzy.cn/dzsggzy/jyxx/025001/025001001/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zgys_gg",
     "http://www.dzggzy.cn/dzsggzy/jyxx/025001/025001012/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gglx':'资格预审公告(抽签法)'}), f2],

    ["gcjs_zgysjg_gg",
     "http://www.dzggzy.cn/dzsggzy/jyxx/025001/025001017/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_liubiao_gg",
     "http://www.dzggzy.cn/dzsggzy/jyxx/025001/025001013/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://www.dzggzy.cn/dzsggzy/jyxx/025001/025001009/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://www.dzggzy.cn/dzsggzy/jyxx/025001/025001015/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.dzggzy.cn/dzsggzy/jyxx/025001/025001004/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_chouqian_gg",
     "http://www.dzggzy.cn/dzsggzy/jyxx/025001/025001005/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gglx':'抽签法评标结果公示'}), f2],
    #
    ["zfcg_zhaobiao_gg",
     "http://www.dzggzy.cn/dzsggzy/jyxx/025002/025002001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://www.dzggzy.cn/dzsggzy/jyxx/025002/025002003/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://www.dzggzy.cn/dzsggzy/jyxx/025002/025002005/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_liubiao_gg",
     "http://www.dzggzy.cn/dzsggzy/jyxx/025002/025002006/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_zhaobiao_gg",
     "http://www.dzggzy.cn/dzsggzy/jyxx/025006/025006001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'jylx':'其他交易'}), f2],

    ["qsy_biangeng_gg",
     "http://www.dzggzy.cn/dzsggzy/jyxx/025006/025006005/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其他交易'}), f2],

    ["qsy_zhongbiao_gg",
     "http://www.dzggzy.cn/dzsggzy/jyxx/025006/025006002/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其他交易'}), f2],

]



def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省达州市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","dazhou"])


