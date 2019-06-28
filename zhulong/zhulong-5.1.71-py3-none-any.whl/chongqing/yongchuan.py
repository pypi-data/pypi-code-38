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
# url="http://www.cqyc.gov.cn/ztzl/ggzyjyzx/zfcg/cgjggg/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='yongchuan'

def f1(driver,num):

    locator=(By.XPATH,"//ul[@class='yc-gl-ls']/li[1]/a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    if "index.html" in url:
        cnum=1
    else:
        cnum=int(re.findall("index_([0-9]{1,}).html",url)[0])+1
    if num!=cnum:
        if num==1:
            url=re.sub("index[_0-9]*.htm","index.html",url)
        else:
            s="index_%d.html"%(num-1) if num>1 else "index.html"
            url=re.sub("index[_0-9]*.html",s,url)
        val=driver.find_element_by_xpath("//ul[@class='yc-gl-ls']/li[1]/a").get_attribute('href').rsplit('/',maxsplit=1)[1]
        driver.get(url)
        locator=(By.XPATH,"//ul[@class='yc-gl-ls']/li[1]/a[not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    main_url=url.rsplit('/',maxsplit=1)[0]

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    data=[]
    lis = soup.find('ul', class_='yc-gl-ls').find_all('li')

    for li in lis:
        href=li.a['href']
        name=li.a['title']
        ggstart_time=li.span.get_text()

        if re.findall('http', href):
            href = href
        elif re.findall('\.\./\.\./',href):
            href='http://yc.cq.gov.cn/ztzl/ggzyjyzx/' + href.strip(r'../../')
        else:
            href=main_url+href.strip(r'.')

        tmp = [name, ggstart_time, href]
        # print(tmp)
        data.append(tmp)

    df=pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[@class='yc-gl-ls']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath("(//a[@class='pg-opt pre-pg'])[last()]").text
    total=int(page)
    driver.quit()
    return total



def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="xl-sp-bk"]')

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
    div = soup.find('div',class_='xl-sp-bk')
    return div

data=[

    ["gcjs_zhaobiao_gg","http://yc.cq.gov.cn/ztzl/ggzyjyzx/gcztb/zbgg/index.html",["name","ggstart_time","href",'info'],f1,f2],
    ["gcjs_gqita_da_bian_gg","http://yc.cq.gov.cn/ztzl/ggzyjyzx/gcztb/dybl/index.html",["name","ggstart_time","href",'info'],f1,f2],
    ["gcjs_zhongbiaohx_gg","http://yc.cq.gov.cn/ztzl/ggzyjyzx/gcztb/zbgg_130/index.html",["name","ggstart_time","href",'info'],f1,f2],

    ["zfcg_zhaobiao_gg","http://www.cqyc.gov.cn/ztzl/ggzyjyzx/zfcg/cggg/index.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_gqita_da_bian_gg","http://www.cqyc.gov.cn/ztzl/ggzyjyzx/zfcg/dybg/index.html",["name","ggstart_time","href",'info'],f1,f2],
    ###包含中标,流标
    ["zfcg_gqita_zhong_liu_gg","http://www.cqyc.gov.cn/ztzl/ggzyjyzx/zfcg/cgjggg/index.html",["name","ggstart_time","href",'info'],f1,f2],

    ["qsy_zhaobiao_gg","http://www.cqyc.gov.cn/ztzl/ggzyjyzx/qtjy/jyggqtjy/index.html",["name","ggstart_time","href",'info'],f1,f2],
    ["qsy_zhongbiaohx_gg","http://www.cqyc.gov.cn/ztzl/ggzyjyzx/qtjy/jggsqtjy/index.html",["name","ggstart_time","href",'info'],f1,f2],


]
def work(conp,**args):
    est_meta(conp,data=data,diqu="重庆市永川区",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':


    conp=["postgres","since2015","192.168.3.171","chongqing","yongchuan"]

    work(conp=conp)