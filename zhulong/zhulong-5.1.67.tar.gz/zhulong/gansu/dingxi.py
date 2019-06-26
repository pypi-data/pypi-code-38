import json

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
from zhulong.util.etl import gg_meta,gg_html,est_meta,est_html

from zhulong.util.etl import add_info


_name_='dingxi'

# driver=webdriver.Chrome()
# url='http://ggzy.dingxi.gov.cn/jyxx/project.html?categoryNum=004001004'
# driver.get(url)


def f1(driver, num):
    locator = (By.XPATH, "//div[@id='dt']/ul[@class='wb-data-item']/li[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//span[@class="current pageIdx ewb-fan"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    time.sleep(0.5)
    cnum = int(driver.find_element_by_xpath('//span[@class="current pageIdx ewb-fan"]').text)

    if num != cnum:
        page_count=len(driver.page_source)
        val = driver.find_element_by_xpath("//div[@id='dt']/ul[@class='wb-data-item']/li[1]//a").get_attribute(
            'href')
        val=re.findall('javascript:redirectpage\("(.+?)",".+"\)',val)[0]
        inp = driver.find_element_by_xpath("//input[@class='pg_num_input']")
        driver.execute_script("arguments[0].value='%s';" % num, inp)
        go = driver.find_element_by_xpath('//a[@class="pg_gobtn ewb-fan"]')
        driver.execute_script("arguments[0].click()", go)

        locator = (By.XPATH, "//div[@id='dt']/ul[@class='wb-data-item']/li[1]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        WebDriverWait(driver, 10).until(lambda driver:len(driver.page_source) != page_count)

    page = driver.page_source

    soup = BeautifulSoup(page, "html.parser")

    ul = soup.find("ul", class_="wb-data-item")

    lis = ul.find_all("li")

    data = []

    for li in lis:
        name = li.find("a")['title']
        href_js = li.find("a")['href']
        ggstart_time = li.find('span', class_='wb-data-date').get_text().strip('[').strip(']')

        ggend_time=li.find('span',class_=re.compile('youxiaodate')).get_text().strip()
        diqu=li.find('font',color='#0066FF')

        diqu=diqu.get_text().strip('[').strip(']') if diqu else None


        href=href_js

        info=json.dumps({"ggent_time":ggend_time,"diqu":diqu},ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]

        data.append(tmp)



    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, "//div[@id='dt']/ul[@class='wb-data-item']/li[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//div[@id="divInfoReportPage"]/span[@class="pg_maxpagenum"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    time.sleep(1)

    total=re.findall('<span class="pg_maxpagenum">1/(\d+)</span>',driver.page_source)[0]

    driver.quit()
    return int(total)




def f3(driver, url):
    mark_url=driver.current_url
    if 'http://ggzy.dingxi.gov.cn/jyxx/project.html?categoryNum=004001' != mark_url:
        driver.get('http://ggzy.dingxi.gov.cn/jyxx/project.html?categoryNum=004001')
        locator = (By.XPATH, "//div[@id='dt']/ul[@class='wb-data-item']/li[1]//a")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        time.sleep(1)

    driver.execute_script(url)
    time.sleep(1)
    post=driver.window_handles

    driver.switch_to.window(post[1])

    locator = (
    By.XPATH, '//div[@id="content"][string-length()>100] | //div[@class="ewb-wrap"][string-length()>100]')

    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


    before = len(driver.page_source)
    time.sleep(0.2)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.2)
        after = len(driver.page_source)
        i += 1
        if i > 10: break

    time.sleep(1)
    locator=(By.XPATH,'//div[@id="layui-layer2"]/div[@class="layui-layer-content layui-layer-loading0"]')
    WebDriverWait(driver, 10).until(EC.invisibility_of_element_located(locator))

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    div = soup.find('div', class_='ewb-wrap')

    if not  div:
        div = soup.find('div',id="content")


    driver.close()
    driver.switch_to.window(post[0])

    return div



data=[

    ["gcjs_gqita_gg","http://ggzy.dingxi.gov.cn/jyxx/project.html?categoryNum=004001",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_gqita_gg","http://ggzy.dingxi.gov.cn/jyxx/project.html?categoryNum=004002",["name","ggstart_time","href","info"],f1,f2],
    ["jqita_yangguang_gqita_gg","http://ggzy.dingxi.gov.cn/jyxx/project.html?categoryNum=004005",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"阳光采购"}),f2],
    ["jqita_zhongda_gqita_gg","http://ggzy.dingxi.gov.cn/jyxx/project.html?categoryNum=004006",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"重大项目"}),f2],


    ]



##### f3 为全流程

def work(conp,**args):
    est_meta(conp,data=data,diqu="甘肃省定西市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    # work(conp=["postgres","zhulong.com.cn",'192.168.169.47',"gansu","dingxi"],num=1,headless=False,total=2)
    work(conp=["postgres","since2015",'192.168.3.171',"gansu","dingxi"])
    # driver=webdriver.Chrome()
    # url='javascript:redirectpage("75ed984e-45f3-4a41-866c-6049a6ae5c6f","004005001")'
    # #
    # q=f3(driver,url)
    #
    # print(q)
    pass