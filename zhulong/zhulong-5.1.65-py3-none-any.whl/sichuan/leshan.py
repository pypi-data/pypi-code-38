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

_name_="leshan"



def f1(driver, num):
    url = driver.current_url
    locator = (By.XPATH, "//div[@class='news-list list-ul']/ul/li[1]/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    try:
        cnum = driver.find_element_by_xpath("//div[@class='pages']/a[@class='active']").text.strip()
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='news-list list-ul']/ul/li[1]/a").get_attribute('href').rsplit('/',maxsplit=1)[1]
        driver.execute_script("changePage({})".format(num-1))
        locator = (By.XPATH, '//div[@class="news-list list-ul"]/ul/li[1]/a[not(contains(@href,"%s"))]' % (val))
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("div", class_="news-list list-ul").ul
    trs = table.find_all("li")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = "http://www.lsggzy.com.cn" + a['href'].strip()
        td = tr.find("span", class_="time").text.strip()
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df





def f2(driver):
    locator = (By.XPATH, "//div[@class='news-list list-ul']/ul/li[1]/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='pages']/span[last()-1]")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = re.findall(r'(\d+)', val)[0]
    except:
        num = 1

    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='box-container'][string-length()>30] | //div[@class='content-box'][string-length()>30]")
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
    div = soup.find('div', class_="content-box")
    if div == None:
        div = soup.find('div', class_="box-container")
    return div

timesEnd = time.strftime('%Y-%m-%d',time.localtime(time.time()))

data = [
    ["gcjs_zhaobiao_gg",
     "http://www.lsggzy.com.cn/pub/jyxx/list.html?menuCode=JYGCJS&typeCode=ZBGG&title=&pubStime=2012-04-16&pubEtime=%s&page=1" % (timesEnd),
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.lsggzy.com.cn/pub/jyxx/list.html?menuCode=JYGCJS&typeCode=PBJG&title=&pubStime=2012-04-16&pubEtime=%s&page=1" % (timesEnd),
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_liu_zhongz_gg",
     "http://www.lsggzy.com.cn/pub/jyxx/list.html?menuCode=JYGCJS&typeCode=TBTZ&title=&pubStime=2012-04-16&pubEtime=%s&page=1" % (timesEnd),
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_hetong_gg",
     "http://www.lsggzy.com.cn/pub/jyxx/list.html?menuCode=JYGCJS&typeCode=QYLX&title=&pubStime=2012-04-16&pubEtime=%s&page=1" % (timesEnd),
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://www.lsggzy.com.cn/pub/jyxx/list.html?menuCode=JYZFCG&typeCode=CGGG&title=&pubStime=2012-04-16&pubEtime=%s&page=1" % (timesEnd),
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://www.lsggzy.com.cn/pub/jyxx/list.html?menuCode=JYZFCG&typeCode=GZGG&title=&pubStime=2012-04-16&pubEtime=%s&page=1" % (timesEnd),
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhong_liu_gg",
     "http://www.lsggzy.com.cn/pub/jyxx/list.html?menuCode=JYZFCG&typeCode=JGGG&title=&pubStime=2012-04-16&pubEtime=%s&page=1" % (timesEnd),
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_gqita_zhao_bian_gg",
     "http://www.lsggzy.com.cn/pub/jyxx/list.html?menuCode=JYQT&typeCode=GGXX&title=&pubStime=2012-04-16&pubEtime=%s&page=1" % (timesEnd),
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'jylx':'其他交易'}), f2],

    ["qsy_gqita_zhong_liu_gg",
     "http://www.lsggzy.com.cn/pub/jyxx/list.html?menuCode=JYQT&typeCode=JYJG&title=&pubStime=2012-04-16&pubEtime=%s&page=1" % (timesEnd),
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'jylx':'其他交易'}), f2],
]



def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省乐山市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","leshan"])
