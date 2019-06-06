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


from zhulong.util.etl import est_tbs,est_meta,est_html

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]

#
# url="http://www.yingtan.gov.cn/xxgk/zdgc/zdgcztb/index.htm"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='yingtan'

def f1(driver,num):
    locator=(By.XPATH,"//div[@class='ldjs_body']/ul/li[1]/a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    url=driver.current_url
    if "index.htm" in url:
        cnum=1
    else:
        cnum=int(re.findall("index_([0-9]{1,}).htm",url)[0])+1
    if num!=cnum:
        if num==1:
            url=re.sub("index[_0-9]*.htm","index.htm",url)
        else:
            s="index_%d.htm"%(num-1) if num>1 else "index.htm"
            url=re.sub("index[_0-9]*.htm",s,url)
        val=driver.find_element_by_xpath("//div[@class='ldjs_body']/ul/li[1]/a").get_attribute(
            "href")[- 30:-5]
        driver.get(url)
        locator=(By.XPATH,"//div[@class='ldjs_body']/ul/li[1]/a[not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    page = driver.page_source

    soup = BeautifulSoup(page, "html.parser")
    url = driver.current_url
    rindex = url.rfind('/')
    url_1 = url[:rindex]
    url_2 = re.findall('http://www.yingtan.gov.cn/\w+?/', url)[0]

    tables = soup.find('div', class_='ldjs_body')
    lis = tables.find_all('li')
    data = []
    for i in range(0, len(lis), 2):

        li = lis[i]
        href = li.a['href'].strip('.')

        title = li.get_text().strip().strip('•').strip()
        li = lis[i + 1]
        data_time = li.get_text().strip()
        if re.findall('http', href):
            href = href
        elif re.findall(r'/\.\./', href):
            href = href.split(r'/../')[1]
            href = url_2 + href
        else:
            href = url_1 + href

        tmp = [title, data_time, href]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):

    locator = (By.XPATH, "//div[@class='ldjs_body']/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.find_element_by_xpath("(//*[@class='cn'])[5]").text
    total = re.findall('总共(\d+)页', page)[0]
    total=int(total)
    driver.quit()
    return total

def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="artibody"] | //div[@class="ewb-detail-box"] |'
                         ' //div[@class="main_main"] | (//table[@class="table3"])[1]')

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
    div = soup.find('div',class_="artibody")
    if div == None:
        div=soup.find('div',class_="ewb-detail-box")
        if div == None:
            div=soup.find('div',class_="main_main")
            if div == None:
                div=soup.find('table',class_="table3")
    return div


data=[

    ["gcjs_zhaobiao_gg","http://www.yingtan.gov.cn/xxgk/zdgc/zdgcztb/index.htm",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_zhaobiao_gg","http://www.yingtan.gov.cn/xxgk/zfcg/zhaobgg/index.htm",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_zhongbiao_gg","http://www.yingtan.gov.cn/xxgk/zfcg/zbgg/index.htm",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_liubiao_gg","http://www.yingtan.gov.cn/xxgk/zfcg/fbgg/index.htm",["name","ggstart_time","href",'info'],f1,f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="江西省鹰潭市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':


    conp=["postgres","since2015","192.168.3.171","jiangxi","yingtan"]

    work(conp=conp,headless=False,num=4)
