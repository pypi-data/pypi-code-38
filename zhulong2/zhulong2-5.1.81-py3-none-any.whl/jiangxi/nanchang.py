import json
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


from zhulong2.util.etl import est_tbs, est_meta, est_html, est_gg


# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='jiangxi_nanchang'


def f1(driver,num):

    locator = (By.XPATH, '//ul[@class="listbox"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url = driver.current_url
    mark=re.findall('sid=(\d+?)&',url)[0]
    mark_dict={
        "100002011":"002006004",
        "100002003":"002006001",
    }

    cnum = int(re.findall("Page=(\d+)", url)[0])
    main_url=url.rsplit('=',maxsplit=1)[0]
    if num != cnum:
        url=main_url+'=%s'%num
        val = driver.find_element_by_xpath('//ul[@class="listbox"]/li[1]/a').get_attribute('href')[-30:]
        driver.get(url)

        locator = (By.XPATH, "//ul[@class='listbox']/li[1]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


    ht = driver.page_source
    soup = BeautifulSoup(ht, 'html.parser')
    uls = soup.find('ul', class_="listbox")
    lis = uls.find_all('li')
    data = []
    for li in lis:
        name = li.a['title']
        href = li.a['href']
        url_href=re.findall('id=(.+)$',href)[0]
        ggstart_time = li.div.get_text().strip()
        index = name.find('[')
        if index == 0:
            url_time = ggstart_time.replace('-', '')
            href = "http://www.jxsggzy.cn/web/jyxx/002006/{mark}/{time}/{ids}.html".\
                format(mark=mark_dict[mark],time=url_time, ids=url_href)

            address=re.findall('\[(.+?)\]',name)[0]
            name=re.findall('\[.+?\](.+)',name)[0]
            info = json.dumps({'diqu': address}, ensure_ascii=False)
        else:
            name=name
            info=None
            href="http://www.ncszfcg.gov.cn/"+href

        tmp = [name, ggstart_time, href,info]

        data.append(tmp)
    df=pd.DataFrame(data=data)

    return df


def f2(driver):

    locator = (By.XPATH, '//ul[@class="listbox"]/li[1]/a')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    total=int(driver.find_element_by_xpath('//div[@class="mod-pager-box"]/b[3]').text)

    driver.quit()
    return total

def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="article-info"][string-length()>10] | //div[@class="main"][string-length()>10]')

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
    div = soup.find('div',class_="ewb-detail-box")
    if div == None:
        div=soup.find('div',class_="main")
    return div



data=[

    ["zfcg_zhaobiao_gg","http://www.ncszfcg.gov.cn/more2018.cfm?sid=100002003&Page=1",["name","ggstart_time","href",'info'],f1,f2],
    ###包含中标,流标
    ["zfcg_zhongbiao_gg","http://www.ncszfcg.gov.cn/more2018.cfm?sid=100002011&Page=1",["name","ggstart_time","href",'info'],f1,f2],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="江西省南昌市",**args)
    est_html(conp,f=f3,**args)



if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","lch","jiangxi_nanchang"]

    work(conp=conp)