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


from zhulong.util.etl import est_tbs, est_meta, est_html, est_gg


# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='lasa'

def f1(driver,num):
    locator = (By.XPATH, '//div[@id="listCon"]/ul/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    p1 = url.rsplit('=', maxsplit=1)[1]
    # 寻找当前页
    cnum = driver.find_element_by_xpath('//span[@class="page-cur"]').text.strip()

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//div[@id="listCon"]/ul/li[1]/a').get_attribute(
            "href")[- 20:]

        driver.execute_script("SearchArticleOnce({p1},0,{num},10)".format(p1=p1, num=num))

        locator = (By.XPATH, '//div[@id="listCon"]/ul/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', id='listCon')
    lis = div.find_all('li')
    for li in lis:
        href = li.a['href']
        name = li.a.get_text().strip()
        ggstart_time = li.find('span').get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.lsggzy.cn' + href
        tmp = [name, href, ggstart_time]
        data.append(tmp)

    df=pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, '//div[@id="listCon"]/ul/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//div[@class="pagination fr"]/a[last()]').get_attribute('onclick')

    page = page.split(',')[2]
    total=int(page)
    driver.quit()
    return total

def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@id="content"] | /html/body/img')

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
    div = soup.find('div', id="content")
    if div == None:
        div = soup.find('body').find('img',recursive=False)
        if div == None:
            raise ValueError

    return div

data=[
    #
    ["gcjs_zhaobiao_gg","http://www.lsggzy.cn/Category/More?id=643",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["gcjs_zhongbiaohx_gg","http://www.lsggzy.cn/Category/More?id=661",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["gcjs_gqita_da_bian_gg","http://www.lsggzy.cn/Category/More?id=644",[ "name", "href", "ggstart_time","info"],f1,f2],
    ####包含中标,流标
    ["gcjs_gqita_zhong_liu_gg","http://www.lsggzy.cn/Category/More?id=668",[ "name", "href", "ggstart_time","info"],f1,f2],

    ["zfcg_yucai_gg","http://www.lsggzy.cn/Category/More?id=1730",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["zfcg_zhaobiao_gg","http://www.lsggzy.cn/Category/More?id=724",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["zfcg_gqita_da_bian_gg","http://www.lsggzy.cn/Category/More?id=725",[ "name", "href", "ggstart_time","info"],f1,f2],

    ###暂时无数据
    # ["zfcg_liubiao_gg","http://www.lsggzy.cn/Category/More?id=726",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["zfcg_zhongbiao_gg","http://www.lsggzy.cn/Category/More?id=727",[ "name", "href", "ggstart_time","info"],f1,f2],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="西藏自治区拉萨市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","xizang","lasa"]

    work(conp=conp,headless=False,num=1,total=5)