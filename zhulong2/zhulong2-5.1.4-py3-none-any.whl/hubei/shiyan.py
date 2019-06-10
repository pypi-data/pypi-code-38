import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from zhulong2.util.etl import est_tbs, est_meta, est_html, est_gg, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='hubei_shiyan'


def f1(driver,num):

    locator = (By.XPATH, '//table[@id="bodytable"]/tbody/tr[2]/td[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url = driver.current_url

    if 'list_50.shtml' in url:
        cnum = 1
    else:
        cnum = int(re.findall("list_50_(\d+).shtml", url)[0]) + 1

    main_url = url.rsplit('/', maxsplit=1)[0]

    if num != cnum:
        s = "list_50_%s.shtml" % (num-1)
        if num == 1:
            url_ = re.sub("list_50_\d+.shtml", 'list_50.shtml', url)
        else:
            url_ = re.sub("list_50_{0,1}\d*.shtml", s, url)

        val = driver.find_element_by_xpath('//table[@id="bodytable"]/tbody/tr[2]/td[1]//a').get_attribute('href').rsplit(
            '/', maxsplit=1)[1]

        driver.get(url_)

        locator = (By.XPATH, '//table[@id="bodytable"]/tbody/tr[2]/td[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    ht = driver.page_source
    soup = BeautifulSoup(ht, 'html.parser')
    div = soup.find('table', id="bodytable").find('tbody')
    uls = div.find_all('tr',recursive=False)[1:]

    data = []
    for li in uls:
        tds=li.find_all('td',recursive=False)

        href = tds[0].find('a')['href'].strip('.')
        name = tds[0].find('a').get_text()

        if 'http' in href:
            href = href
        else:
            href = main_url + href

        ggstart_time = tds[-1].get_text()
        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"] = None

    return df



def f2(driver):
    locator = (By.XPATH, '//table[@id="bodytable"]/tbody/tr[2]/td[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//table[@id="bodytable"]/tbody/tr[2]/td[1]//a').get_attribute('href').rsplit(
        '/', maxsplit=1)[1]
    driver.execute_script('document.getElementById("thisNum").value ="1000"')

    driver.execute_script('toPage()')

    locator = (By.XPATH, '//table[@id="bodytable"]/tbody/tr[2]/td[1]//a[not(contains(@href,"%s"))]' % val)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//span[@class="current"]').text.strip()

    total = int(total)

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="display_content"][string-length()>10]')

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
    div = soup.find('div',class_="display_content")
    try:
        div.find('div',class_='syfb').extract()
    except:
        pass
    if div==None:raise ValueError
    return div




data=[
    ["zfcg_gqita_zhao_bian_gg", "http://www.shiyan.gov.cn/sysgovinfo/szfcgzx/sfgwgkml/zfcg_2150/cggg_2152/list_50.shtml",["name", "ggstart_time", "href", 'info'], f1 ,f2],
    ["zfcg_zhongbiao_gg", "http://www.shiyan.gov.cn/sysgovinfo/szfcgzx/sfgwgkml/zfcg_2150/zbgg_2153/list_50.shtml",["name", "ggstart_time", "href", 'info'], f1 ,f2],
    ["zfcg_zhaobiao_gg", "http://www.shiyan.gov.cn/sysgovinfo/szf/xxgkml/zbcg/zbgg_7671/list_50.shtml",["name", "ggstart_time", "href", 'info'], f1 ,f2],
    # ["zfcg_zhongbiaohx_gg", "http://www.shiyan.gov.cn/sysgovinfo/szf/xxgkml/zbcg/zbcjjg/list_50.shtml",["name", "ggstart_time", "href", 'info'], f1 ,f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="湖北省十堰市",**args)
    est_html(conp,f=f3,**args)
    # est_gg(conp,diqu="湖北省十堰市")



if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","lch","hubei_shiyan"]

    work(conp=conp,headless=False,pageloadtimeout=60,pageloadstrategy='none',num=1,cdc_total=1)