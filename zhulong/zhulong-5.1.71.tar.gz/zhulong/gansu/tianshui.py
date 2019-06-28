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


# 

# driver=webdriver.Chrome()
# url="http://www.tsggzyjy.gov.cn/f/trade/annogoods/list?prjpropertycode=A01"
# driver.get(url)

_name_='tianshui'


def f1(driver,num):
    locator=(By.XPATH,'//div[@class="ejcotlist"]//li[1]/a')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//ul[@class="pagination pagination-outline"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum=int(driver.find_element_by_xpath("//li[@class='paginate_button active']/a").text)
    if cnum!=num:
        page_count = len(driver.page_source)
        val = driver.find_element_by_xpath('//div[@class="ejcotlist"]//li[1]/a').get_attribute('href')
        val = re.findall(r'/(\d+)/', val)[0]

        driver.execute_script("page(%d,20,'');"%num)

        locator=(By.XPATH,"//div[@class='ejcotlist']//li[1]/a[not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
        WebDriverWait(driver, 10).until(lambda driver: len(driver.page_source) != page_count)

    page=driver.page_source
    soup=BeautifulSoup(page,'html.parser')
    div=soup.find("div",class_="ejcotlist")
    lis=div.find_all("li")
    data=[]
    for li in lis:
        href=li.a['href']
        name=li.a.get_text().strip()
        ggstart_time=li.span.get_text()
        href='http://www.tsggzyjy.gov.cn' + href
        tmp=[name,ggstart_time,href]

        data.append(tmp)


    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 


def f2(driver):

    locator=(By.XPATH,"//div[@class='ejcotlist']//li[1]/a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    locator=(By.XPATH,'//ul[@class="pagination pagination-outline"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        total = int(driver.find_element_by_xpath('//li[@class="paginate_button "][last()]/a').text)
    except:
        total=1

    driver.quit()
    return total



def f3(driver,url):


    driver.get(url)

    locator=(By.XPATH,'//div[@class="jxTradingMainLeft"][string-length()>100]')

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

    div=soup.find('div',class_='jxTradingMainLeft')

    
    return div


data=[
        ###招标
        ["gcjs_zhaobiao_gg","http://www.tsggzyjy.gov.cn/f/trade/annogoods/list?prjpropertycode=A01&annogoodstype=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiao_gg","http://www.tsggzyjy.gov.cn/f/trade/annogoods/list?prjpropertycode=A01&annogoodstype=2",["name","ggstart_time","href","info"],f1,f2],

        #交通水利工程

        ["gcjs_jiaotong_zhaobiao_gg","http://www.tsggzyjy.gov.cn/f/trade/annogoods/list?prjpropertycode=A02&annogoodstype=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_jiaotong_zhongbiao_gg","http://www.tsggzyjy.gov.cn/f/trade/annogoods/list?prjpropertycode=A02&annogoodstype=2",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_shuili_zhaobiao_gg","http://www.tsggzyjy.gov.cn/f/trade/annogoods/list?prjpropertycode=A03&annogoodstype=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_shuili_zhongbiao_gg","http://www.tsggzyjy.gov.cn/f/trade/annogoods/list?prjpropertycode=A03&annogoodstype=2",["name","ggstart_time","href","info"],f1,f2],

        #政府采购

        ["zfcg_zhaobiao_gg","http://www.tsggzyjy.gov.cn/f/trade/annogoods/list?prjpropertycode=D&annogoodstype=1",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhongbiao_gg","http://www.tsggzyjy.gov.cn/f/trade/annogoods/list?prjpropertycode=D&annogoodstype=2",["name","ggstart_time","href","info"],f1,f2]

    ]


## f3 为全流程

def work(conp,**args):
    est_meta(conp,data=data,diqu="甘肃省天水市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015",'192.168.3.171',"gansu","tianshui"],num=10,headless=True)
