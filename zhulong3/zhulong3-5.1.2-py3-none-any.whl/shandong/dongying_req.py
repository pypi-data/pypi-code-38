import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json
import requests
from zhulong3.util.fake_useragent import UserAgent

from zhulong.util.etl import est_tbs, est_meta, est_html

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fzztb.com/CmsPortalWeb/main/project.xhtml"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_ = 'shandong_dongying'


def f1(driver, num):
    locator = (By.XPATH, '//div[@id="Grid"]/table/tbody/tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url=driver.current_url
    ua=UserAgent()
    if 'flag=-1' in url:
        url1='http://103.239.153.139:88/dyztb/ZTB/AnnounceList?areaCode=05&Grid-size=20&flag=-1'
    else:
        url1='http://103.239.153.139:88/dyztb/ZTB/AnnounceList?areaCode=05&Grid-size=20&flag=2'

    form_data={
        "page": num,
        "size": 20
        }
    headers={
        "Referer": url,
        "User-Agent": ua.chrome
    }

    req=requests.post(url1,headers=headers,data=form_data)
    if req.status_code != 200:
        raise ValueError('Error status code %s'%req.status_code)
    content=req.text

    content=json.loads(content,encoding='utf8')
    datas=content['data']
    data = []
    for d in datas:
        href =d.get('sfile')
        name =d.get('ProjectName')
        gg_type = d.get('CTitle')
        zbdl = d.get('CorpDL')
        jsdw =d.get('CorpZB')
        address =d.get('ASTitle')
        ggend_time=d.get('DateBidEnd')
        ggstart_time=d.get('DateBidStart')
        if ggend_time is None:
            ggend_time=d.get('EndDate')
        if ggstart_time is None:
            ggstart_time=d.get('StartDate')

        ggend_time =time.strftime('%Y-%m-%d',time.localtime(int(ggend_time[6:16])))
        ggstart_time = time.strftime('%Y-%m-%d',time.localtime(int(ggstart_time[6:16])))

        class_=d.get('zbflag')
        if class_ == 1:
            class_=5022
        else:
            class_=5021

        if 'flag=2' in url:
            href = 'http://103.239.153.139:88/dyztb/ztb/AnnounceDetail?id={id}&class=5070&flag={flag}&file={file}'.format(id=d.get('ID'),flag=d.get('zbflag'),file=href)
        else:
            href = 'http://103.239.153.139:88/dyztb/ztb/AnnounceDetail?id={id}&class={class_}&flag={flag}&file={file}'.format(id=d.get('ID'),flag=d.get('zbflag'),file=href,class_=class_)
        info={'gg_type':gg_type,'ggend_time':ggend_time,'zbdl':zbdl,'address':address,'jsdw':jsdw}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]

        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@id="Grid"]/table/tbody/tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath('//div[@class="t-page-i-of-n"]').text
    total = re.findall('共(.+)页', total)[0].strip()
    total=int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//div[@style="margin: auto;"]')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    time.sleep(0.1)
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

    div = soup.find('div', attrs={'style':re.compile('^margin: auto;$')})

    return div


data = [

    ##包含招标,变更
    ["gcjs_gqtia_zhao_gg", "http://103.239.153.139:88/dyztb/ZTB?flag=-1",["name", "ggstart_time", "href", "info"], f1, f2],
    ##包含中标,流标
    ["gcjs_gqita_zhong_gg", "http://103.239.153.139:88/dyztb/ZTB?flag=2",["name", "ggstart_time", "href", "info"], f1, f2],

]

def work(conp, **args):
    est_meta(conp, data=data, diqu="山东省东营市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "shandong_dongying"])