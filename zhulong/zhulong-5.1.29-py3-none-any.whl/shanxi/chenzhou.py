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


_name_="chenzhou"



def f1(driver, num):
    url = driver.current_url
    locator = (By.XPATH, '//ul[@class="clearfix list-ul"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        try:
            pnum = re.findall(r'pager\.offset=(\d+)', url)[0]
            cnum = int(int(pnum) / 15 + 1)
        except:
            cnum = re.findall(r'index_(\d+)', url)[0]
    except:
        cnum = 1

    if num != int(cnum):
        val = driver.find_element_by_xpath('//ul[@class="clearfix list-ul"]/li[1]/a').get_attribute('href')[-20:]
        if 'htm' in url:
            if "index.htm" in url:
                s = "index_%d.htm" % (num-1) if num > 1 else "index.htm"
                url = re.sub("index\.htm", s, url)
            elif num == 1:
                url = re.sub("index_[0-9]*", "index", url)
            else:
                s = "index_%d" % (num-1) if num > 1 else "index"
                url = re.sub("index_[0-9]*", s, url)
            driver.get(url)
        else:
            if num == 1:
                url = re.sub("pager\.offset=[0-9]*", "pager.offset=0", url)
            else:
                s = "pager.offset=%d" % ((num-1)*15) if num > 1 else "pager.offset=0"
                url = re.sub("pager\.offset=[0-9]*", s, url)
            driver.get(url)
        locator = (By.XPATH, "//ul[@class='clearfix list-ul']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    ul = soup.find("ul", class_='clearfix list-ul')
    trs = ul.find_all("li")
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
        if 'http' in link:
            links = link.strip()
        else:
            url = driver.current_url
            tt = re.findall(r'(.*)index', url)[0]
            links = tt + link.strip()
        span = tr.find('span').text.strip()
        tmp = [title, span, links]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df




def f2(driver):
    locator = (By.XPATH, '//ul[@class="clearfix list-ul"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, '//ul[@class="pager"]/li[last()]/a')
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')
        try:
            pnum = re.findall(r'pager\.offset=(\d+)', str)[0]
            num = int(pnum)/15 + 1
        except:
            pnum = re.findall(r'index_(\d+)', str)[0]
            num = int(pnum) + 1
    except:
        num = 1
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='arc'][string-length()>40]")
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
    div = soup.find('div', class_="arc")
    return div


data = [
    ["gcjs_zhaobiao_fangwu_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18371/18382/18383/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'房屋市政'}), f2],

    ["gcjs_zhaobiao_jiaotong_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18371/18382/18384/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'交通'}), f2],

    ["gcjs_zhaobiao_shuili_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18371/18382/18385/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'水利'}), f2],

    ["gcjs_zhaobiao_qita_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18371/18382/18386/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'其他'}), f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18371/18388/18389/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zgysjg_gg",
     "http://czggzy.czs.gov.cn/18360/18370/18371/18388/18390/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18371/18392/18393/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ###
    ["zfcg_zhaobiao_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18372/18396/18397/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_jingzheng_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18372/18396/18398/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'竞争性谈判'}), f2],

    ["zfcg_zhaobiao_xunjia_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18372/18396/18399/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'询价'}), f2],

    ["zfcg_zhaobiao_danyilaiyuan_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18372/18396/18400/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'单一来源'}), f2],

    ["zfcg_zhaobiao_zigeyushen_gg",
     "http://czggzy.czs.gov.cn/18360/18370/18372/18396/18401/index.htm",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'资格预审'}), f2],

    ["zfcg_zhongbiao_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18372/18406/18407/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_liu_zhongz_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18372/18406/18408/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18372/18409/18410/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhao_liu_gg",
     "http://czggzy.czs.gov.cn/18360/18370/18372/18411/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'其他公告'}), f2],
]


def work(conp,**args):
    est_meta(conp,data=data,diqu="陕西省郴州市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shanxi","chenzhou"])


