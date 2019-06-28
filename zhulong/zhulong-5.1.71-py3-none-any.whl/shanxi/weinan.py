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


_name_="weinan"



def f1(driver, num):
    locator = (By.XPATH, '//table[@class="moreinfocon"]/tbody/tr[1]/td/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//td[@class="huifont"]')
    str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = str.split('/')[0]
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath('//table[@class="moreinfocon"]/tbody/tr[1]/td/a').get_attribute('href')[-40:]
        if "Paging" not in url:
            s = "?Paging=%d" % (num) if num > 1 else "?Paging=1"
            url = url + s
        elif num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, "//table[@class='moreinfocon']/tbody/tr[1]/td/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", class_='moreinfocon')
    ul = table.find("tbody")
    trs = ul.find_all("tr", height="26")
    data = []
    for tr in trs:
        a = tr.find("a")
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()
        try:
            link = a["href"]
        except:
            link = '-'
        td = tr.find("td", align="right")
        span = td.find('span').text.strip()
        links = "http://www.wnggzy.com"+link.strip()
        tmp = [title, span, links]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df




def f2(driver):
    locator = (By.XPATH, '//table[@class="moreinfocon"]/tbody/tr[1]/td/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//td[@class="huifont"]')
    str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = str.split('/')[1]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@width='937'][string-length()>40]")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('table', width="937")
    return div


data = [
    ["gcjs_gqita_zhao_zhong_gg",
     "http://www.wnggzy.com/wnggzyweb/jyxx/002001/002001002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gglx':'招投标安排'}), f2],

    ["gcjs_zhaobiao_fangjian_gg",
     "http://www.wnggzy.com/wnggzyweb/jyxx/002001/002001006/002001006001/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'房建'}), f2],

    ["gcjs_biangeng_fangjian_gg",
     "http://www.wnggzy.com/wnggzyweb/jyxx/002001/002001006/002001006002/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'房建'}), f2],

    ["gcjs_zhongbiao_fangjian_gg",
     "http://www.wnggzy.com/wnggzyweb/jyxx/002001/002001006/002001006003/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'房建'}), f2],
    # #
    ["gcjs_zhaobiao_jiaotong_gg",
     "http://www.wnggzy.com/wnggzyweb/jyxx/002001/002001007/002001007001/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'交通'}), f2],

    ["gcjs_biangeng_jiaotong_gg",
     "http://www.wnggzy.com/wnggzyweb/jyxx/002001/002001007/002001007002/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'交通'}), f2],

    ["gcjs_zhongbiao_jiaotong_gg",
     "http://www.wnggzy.com/wnggzyweb/jyxx/002001/002001007/002001007003/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'交通'}), f2],
    # #
    ["gcjs_zhaobiao_shuili_gg",
     "http://www.wnggzy.com/wnggzyweb/jyxx/002001/002001008/002001008001/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'水利'}), f2],

    ["gcjs_biangeng_shuili_gg",
     "http://www.wnggzy.com/wnggzyweb/jyxx/002001/002001008/002001008002/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'水利'}), f2],

    ["gcjs_zhongbiao_shuili_gg",
     "http://www.wnggzy.com/wnggzyweb/jyxx/002001/002001008/002001008003/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'水利'}), f2],
    # #
    ["gcjs_zhaobiao_qita_gg",
     "http://www.wnggzy.com/wnggzyweb/jyxx/002001/002001009/002001009001/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'其他'}), f2],

    ["gcjs_biangeng_qita_gg",
     "http://www.wnggzy.com/wnggzyweb/jyxx/002001/002001009/002001009002/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'其他'}), f2],

    ["gcjs_zhongbiao_qita_gg",
     "http://www.wnggzy.com/wnggzyweb/jyxx/002001/002001009/002001009003/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'其他'}), f2],
    # #
    ["zfcg_zhaobiao_gg",
     "http://www.wnggzy.com/wnggzyweb/jyxx/002002/002002001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://www.wnggzy.com/wnggzyweb/jyxx/002002/002002003/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["yiliao_zhaobiao_gg",
     "http://www.wnggzy.com/wnggzyweb/jyxx/002005/002005001/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'医疗器械'}), f2],

    ["yiliao_zhongbiao_gg",
     "http://www.wnggzy.com/wnggzyweb/jyxx/002005/002005002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'jylx':'医疗器械'}), f2],
]


def work(conp,**args):
    est_meta(conp,data=data,diqu="陕西省渭南市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shanxi","weinan"],pageloadtimeout=60,pageLoadStrategy="none")


