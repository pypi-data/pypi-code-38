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


_name_="taizhou"


def f1(driver, num):
    locator = (By.XPATH, "//table[@class='table-box']/tbody/tr[2]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='Page-bg floatL']/div")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall(r'(\d+)/', st)[0]
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@class='table-box']/tbody/tr[2]/td/a").get_attribute('href')[-20:]
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
            locator = (By.XPATH, "//table[@class='table-box']/tbody/tr[2]/td/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH, "//table[@class='table-box']/tbody/tr[2]/td/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", class_='table-box').tbody
    trs = table.find_all("tr")
    data = []
    for tr in trs[1:]:
        a = tr.find("a")
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()
        link = "http://www.tzztb.com" + a['href'].strip()
        if tr.find_all('td')[-1]:
            span = tr.find_all('td')[-1].text.strip()
        else:
            span = '-'
        info = {}
        if tr.find_all("td")[0]:
            td1 = tr.find_all("td")[0].text.strip()
            if re.findall(r'(\w+)', td1):
                diqu = re.findall(r'(\w+)', td1)[0]
                info['diqu'] = diqu
        if tr.find("label"):
            td2 = tr.find("label").text.strip()
            if re.findall(r'(\w+)', td2):
                jylx = re.findall(r'(\w+)', td2)[0]
                info['lx'] = jylx
        if 'diqu' not in info.keys():
            if re.findall(r'^【(\w+?)】', title):
                diqu2 = re.findall(r'^【(\w+?)】', title)[0]
                info['diqu'] = diqu2
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = None
        tmp = [title, span, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df




def f2(driver):
    locator = (By.XPATH, "//table[@class='table-box']/tbody/tr[2]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='Page-bg floatL']/div")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    num = re.findall(r'/(\d+)', st)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='content-Border floatL'][string-length()>30] | //div[@class='content-box'][string-length()>30]")
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
    div = soup.find('div', class_='content-box')
    if div == None:
        div = soup.find('div', class_='content-Border floatL')
    return div


data = [
    ["gcjs_zhaobiao_diqu1_gg",
     "http://www.tzztb.com/tzcms/gcjyzhaobgg/index.htm?loca=1&xiaoe=1&type=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'gclx':'规模以上工程'}),f2],

    ["gcjs_zgys_diqu1_gg",
     "http://www.tzztb.com/tzcms/jsgcysgg/index.htm?loca=1&xiaoe=1&type=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx':'规模以上工程'}), f2],

    ["gcjs_zgysjg_diqu1_gg",
     "http://www.tzztb.com/tzcms/gcjyysgs/index.htm?loca=1&xiaoe=1&type=3",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'gclx':'规模以上工程'}), f2],

    ["gcjs_zhongbiaohx_diqu1_gg",
     "http://www.tzztb.com/tzcms/gcjyzbgg/index.htm?loca=1&xiaoe=1&type=4",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'gclx':'规模以上工程'}),f2],

    ["gcjs_zhongbiao_diqu1_gg",
     "http://www.tzztb.com/tzcms/gcjyzbjg/index.htm?loca=1&xiaoe=1&type=5",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'gclx':'规模以上工程'}),f2],

    ["gcjs_gqita_bian_bu_diqu1_gg",
     "http://www.tzztb.com/tzcms/gcjybcwj/index.htm?loca=1&xiaoe=1&type=6",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'gclx':'规模以上工程'}), f2],

    ["gcjs_zhaobiao_xiaoe_diqu1_gg",
     "http://www.tzztb.com/tzcms/xegccrgs/index.htm?loca=1&xiaoe=2&type=10",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '小额工程'}), f2],

    ["gcjs_zhongbiao_xiaoe_diqu1_gg",
     "http://www.tzztb.com/tzcms/xegccjgs/index.htm?loca=1&xiaoe=2&type=11",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '小额工程'}), f2],

    ####
    ["gcjs_zhaobiao_diqu2_gg",
     "http://www.tzztb.com/tzcms/lhxjsgc/index.htm?loca=2&xiaoe=1&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_diqu2_gg",
     "http://www.tzztb.com/tzcms/pbgslhxjsgc/index.htm?loca=2&xiaoe=1&type=4",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_diqu2_gg",
     "http://www.tzztb.com/tzcms/zbgglhxjsgc/index.htm?loca=2&xiaoe=1&type=5",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ####
    ["gcjs_zhaobiao_diqu3_gg",
     "http://www.tzztb.com/tzcms/wlxjsgc/index.htm?loca=3&xiaoe=1&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_diqu3_gg",
     "http://www.tzztb.com/tzcms/pbgswlxjsgc/index.htm?loca=3&xiaoe=1&type=4",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_diqu3_gg",
     "http://www.tzztb.com/tzcms/zbggwlxjsgc/index.htm?loca=3&xiaoe=1&type=5",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ####
    ["gcjs_zhaobiao_diqu4_gg",
     "http://www.tzztb.com/tzcms/yhxjsgc/index.htm?loca=4&xiaoe=1&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_diqu4_gg",
     "http://www.tzztb.com/tzcms/zbggyhxjsgc/index.htm?loca=4&xiaoe=1&type=5",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ####
    ["gcjs_zhaobiao_diqu5_gg",
     "http://www.tzztb.com/tzcms/ttxjsgc/index.htm?loca=5&xiaoe=1&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_diqu5_gg",
     "http://www.tzztb.com/tzcms/pbgsttxjsgc/index.htm?loca=5&xiaoe=1&type=4",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_diqu5_gg",
     "http://www.tzztb.com/tzcms/zbggttxjsgc/index.htm?loca=5&xiaoe=1&type=5",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ####
    ["gcjs_zhaobiao_diqu6_gg",
     "http://www.tzztb.com/tzcms/xjxjsgc/index.htm?loca=6&xiaoe=1&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_diqu6_gg",
     "http://www.tzztb.com/tzcms/zbggxjxjsgc/index.htm?loca=6&xiaoe=1&type=5",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ####
    ["gcjs_zhaobiao_diqu7_gg",
     "http://www.tzztb.com/tzcms/smxjsgc/index.htm?loca=7&xiaoe=1&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_diqu7_gg",
     "http://www.tzztb.com/tzcms/pbgssmxjsgc/index.htm?loca=7&xiaoe=1&type=4",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_diqu7_gg",
     "http://www.tzztb.com/tzcms/zbggsmxjsgc/index.htm?loca=7&xiaoe=1&type=5",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ####
    ["zfcg_zhaobiao_diqu1_gg",
     "http://www.tzztb.com/tzcms/zfcgcggg/index.htm?loca=1&xiaoe=1&type=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs': '集中采购'}),f2],

    ["zfcg_yucai_diqu1_gg",
     "http://www.tzztb.com/tzcms/zfcgzqyj/index.htm?loca=1&xiaoe=1&type=2",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs': '集中采购'}),f2],

    ["zfcg_zhongbiao_diqu1_gg",
     "http://www.tzztb.com/tzcms/zfcgzbhxgs/index.htm?loca=1&xiaoe=1&type=3",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs': '集中采购'}),f2],

    ["zfcg_gqita_bian_cheng_diqu1_gg",
     "http://www.tzztb.com/tzcms/zfcgdybc/index.htm?loca=1&xiaoe=1&type=4",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs': '集中采购'}),f2],
    #
    ["zfcg_zhaobiao_fensan_diqu1_gg",
     "http://www.tzztb.com/tzcms/fscggg/index.htm?loca=1&xiaoe=2&type=5",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '分散采购'}), f2],
    #
    ["zfcg_zhongbiao_fensan_diqu1_gg",
     "http://www.tzztb.com/tzcms/fszbgg/index.htm?loca=1&xiaoe=2&type=6",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '分散采购'}), f2],
    #
    ["zfcg_zhaobiao_diqu2_gg",
     "http://www.tzztb.com/tzcms/lhxzfcg/index.htm?loca=2&xiaoe=1&type=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhongbiao_diqu2_gg",
     "http://www.tzztb.com/tzcms/zbgglhxzfcg/index.htm?loca=2&xiaoe=1&type=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhaobiao_diqu3_gg",
     "http://www.tzztb.com/tzcms/wlxzfcg/index.htm?loca=3&xiaoe=1&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhongbiao_diqu3_gg",
     "http://www.tzztb.com/tzcms/zbggwlxzfcg/index.htm?loca=3&xiaoe=1&type=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhaobiao_diqu4_gg",
     "http://www.tzztb.com/tzcms/yhxzfcg/index.htm?loca=4&xiaoe=1&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhongbiao_diqu4_gg",
     "http://www.tzztb.com/tzcms/zbggyhxzfcg/index.htm?loca=4&xiaoe=1&type=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    #
    ["zfcg_zhaobiao_diqu5_gg",
     "http://www.tzztb.com/tzcms/ttxzfcg/index.htm?loca=5&xiaoe=1&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhongbiao_diqu5_gg",
     "http://www.tzztb.com/tzcms/zbggttxzfcg/index.htm?loca=5&xiaoe=1&type=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhaobiao_diqu6_gg",
     "http://www.tzztb.com/tzcms/xjxzfcg/index.htm?loca=6&xiaoe=1&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhongbiao_diqu6_gg",
     "http://www.tzztb.com/tzcms/zbggxjxzfcg/index.htm?loca=6&xiaoe=1&type=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhaobiao_diqu7_gg",
     "http://www.tzztb.com/tzcms/smxzfcg/index.htm?loca=7&xiaoe=1&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhongbiao_diqu7_gg",
     "http://www.tzztb.com/tzcms/zbggsmxzfcg/index.htm?loca=7&xiaoe=1&type=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省台州市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zhejiang","taizhou"])


