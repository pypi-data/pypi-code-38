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


_name_='zhangye'

# driver=webdriver.Chrome()
# url='http://117.78.26.203:8080/jyxx/001001/secondpage.html?title=&categornum=001001'
# driver.get(url)

def f1(driver,num):
    locator=(By.XPATH,'//li[@class="wb-data-list"][1]//a')
    WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//ul[@class='m-pagination-page']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    cnum=int(driver.find_element_by_xpath("//li[@class='active']").text)
    if num != cnum:
        page_count = len(driver.page_source)
        val=driver.find_element_by_xpath('//li[@class="wb-data-list"][1]//a').get_attribute('onclick')
        val=re.findall("/(.+?).html",val)[0]

        ele=driver.find_element_by_xpath("//input[@data-page-btn='jump']")
        driver.execute_script("arguments[0].value = '%s';"%num, ele)
        elego=driver.find_element_by_xpath("//button[@data-page-btn='jump']")
        driver.execute_script("arguments[0].click()", elego)

        locator=(By.XPATH,"//li[@class='wb-data-list'][1]//a[not(contains(@onclick,'%s'))]"%val)
        WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
        WebDriverWait(driver, 10).until(lambda driver: len(driver.page_source) != page_count)

    page=driver.page_source

    soup=BeautifulSoup(page,"html.parser")

    lis=soup.find_all("li",class_="wb-data-list")

    data=[]

    for li in lis:
        a=li.find("a")
        name=a.get_text().replace('[正在报名]','')
        href=re.findall("/(.+?.html)",a['onclick'])[0]
        ggstart_time=li.find('span','wb-data-date').get_text()
        diqu=re.findall('^\[.+?\]',name)
        diqu=diqu[0].strip(']').strip('[') if diqu else None

        info=json.dumps({'diqu':diqu},ensure_ascii=False)
        if 'http' in href:
            href=href
        else:
            href='http://117.78.26.203:8080/'+href
        tmp=[name,ggstart_time,href,info]

        data.append(tmp)



    df=pd.DataFrame(data=data)

    return df 

def f2(driver):
    locator = (By.XPATH, '//li[@class="wb-data-list"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator=(By.XPATH,"//ul[@class='m-pagination-page']")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    try:
        total=int(driver.find_element_by_xpath('//ul[@class="m-pagination-page"]/li[last()]/a').text)
    except:
        total=1
    driver.quit()
    return total


def f3(driver,url):


    driver.get(url)

    locator=(By.XPATH,"//body[string-length()>100]")

    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))

    before=len(driver.page_source)
    time.sleep(0.1)
    after=len(driver.page_source)
    i=0
    while before!=after:
        before=len(driver.page_source)
        time.sleep(0.1)
        after=len(driver.page_source)
        i+=1
        if i>5:break

    page=driver.page_source

    soup=BeautifulSoup(page,'html.parser')

    div=soup.find('body')
    if '有效期失效不能访问' in page:
        raise ValueError('ip失效')
    
    return div



data=[


    ["gcjs_zhaobiao_gg","http://117.78.26.203:8080/jyxx/001001/secondpage.html?title=&categornum=001001002",["name","ggstart_time","href","info"],f1,f2]

    ,["gcjs_biangeng_gg","http://117.78.26.203:8080/jyxx/001001/secondpage.html?title=&categornum=001001003",["name","ggstart_time","href","info"],f1,f2]

    ,["gcjs_zhaobiao_wenjian_gg","http://117.78.26.203:8080/jyxx/001001/secondpage.html?title=&categornum=001001004",["name","ggstart_time","href","info"],add_info(f1,{"tag":"招标文件"}),f2]

    ,["gcjs_gqita_da_bian_gg","http://117.78.26.203:8080/jyxx/001001/secondpage.html?title=&categornum=001001005",["name","ggstart_time","href","info"],f1,f2]

    ,["gcjs_zgysjg_gg","http://117.78.26.203:8080/jyxx/001001/secondpage.html?title=&categornum=001001006",["name","ggstart_time","href","info"],f1,f2]

    ,["gcjs_zhongbiaohx_gg","http://117.78.26.203:8080/jyxx/001001/secondpage.html?title=&categornum=001001007",["name","ggstart_time","href","info"],f1,f2]

    ,["gcjs_zhongbiao_gg","http://117.78.26.203:8080/jyxx/001001/secondpage.html?title=&categornum=001001008",["name","ggstart_time","href","info"],f1,f2]

    ,["gcjs_liubiao_gg","http://117.78.26.203:8080/jyxx/001001/secondpage.html?title=&categornum=001001009",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_zhaobiao_gg","http://117.78.26.203:8080/jyxx/001001/secondpage.html?title=&categornum=001002002",["name","ggstart_time","href","info"],f1,f2]

    ,["zfcg_biangeng_gg","http://117.78.26.203:8080/jyxx/001001/secondpage.html?title=&categornum=001002003",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_zhaobiao_wenjian_gg","http://117.78.26.203:8080/jyxx/001001/secondpage.html?title=&categornum=001002004",["name","ggstart_time","href","info"],add_info(f1,{"tag":"招标文件"}),f2]
    #
    ,["zfcg_gqita_da_bian_gg","http://117.78.26.203:8080/jyxx/001001/secondpage.html?title=&categornum=001002005",["name","ggstart_time","href","info"],f1,f2]

    ,["zfcg_zgysjg_gg","http://117.78.26.203:8080/jyxx/001001/secondpage.html?title=&categornum=001002013",["name","ggstart_time","href","info"],f1,f2]

    ,["zfcg_zhongbiao_gg","http://117.78.26.203:8080/jyxx/001001/secondpage.html?title=&categornum=001002006",["name","ggstart_time","href","info"],f1,f2]

    ,["zfcg_liubiao_gg","http://117.78.26.203:8080/jyxx/001001/secondpage.html?title=&categornum=001002007",["name","ggstart_time","href","info"],f1,f2]
]



def work(conp,**args):
    est_meta(conp,data=data,pageloadtimeout=80,diqu="甘肃省张掖市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015",'192.168.3.171',"gansu","zhangye"])