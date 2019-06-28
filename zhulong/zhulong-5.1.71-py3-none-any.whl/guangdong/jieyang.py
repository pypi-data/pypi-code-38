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


import time

from zhulong.util.etl import est_html,est_meta ,add_info
_name_="jieyang"


def f1(driver,num):
    locator=(By.XPATH,"//ul[@class='ewb-data-items ewb-pt6']/li[1]//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    try:
        cnum=int(driver.find_element_by_class_name("wb-page-number").text.strip().split("/")[0])
    except:
        cnum=1
    #print(cnum)
    if num!=cnum:
        val=driver.find_element_by_xpath("//ul[@class='ewb-data-items ewb-pt6']/li[1]//a").text
        #
        input1=driver.find_element_by_id("GoToPagingNo")
        input1.clear()
        input1.send_keys(num)
        driver.execute_script("GoToPaging();")
        locator=(By.XPATH,"//ul[@class='ewb-data-items ewb-pt6']/li[1]//a[not(contains(string(),'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
        #print(driver.find_element_by_xpath("//ul[@class='ewb-data-items ewb-pt6']/li[1]//a[not(contains(string(),'%s'))]"%val).text)

    page=driver.page_source 
    soup=BeautifulSoup(page,"html.parser")

    ul=soup.find("ul",class_="ewb-pt6")

    lis=ul.find_all("li",class_="ewb-data-item")
    data=[]

    for li in lis:
        a=li.find("a")
        span=li.find("span")
        tmp=[a.text.strip(),span.text.strip(),"http://www.jysggzy.com/"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 


def f2(driver):

    locator=(By.XPATH,"//ul[@class='ewb-data-items ewb-pt6']/li[1]//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    if "wb-page-number" in driver.page_source:
        total=int(driver.find_element_by_class_name("wb-page-number").text.strip().split("/")[1])
        driver.quit()
        return total
    else:
        return 1


def f3(driver,url):


    driver.get(url)

    locator=(By.XPATH,"//table[@width='887']")

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

    div=soup.find('table',width='887')
    #div=div.find_all('div',class_='ewb-article')[0]
    
    return div


data=[
        ["gcjs_zhaobiao_gg","http://www.jysggzy.com/TPFront/jsgc/004001/",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_gqita_zs_bian_gg","http://www.jysggzy.com/TPFront/jsgc/004002/",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiaohx_gg","http://www.jysggzy.com/TPFront/jsgc/004003/",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiao_gg","http://www.jysggzy.com/TPFront/jsgc/004004/",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_gqita_yicang_gg","http://www.jysggzy.com/TPFront/jsgc/004005/",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhaobiao_gg","http://www.jysggzy.com/TPFront/zfcg/003001/",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_biangeng_gg","http://www.jysggzy.com/TPFront/zfcg/003002/",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhongbiao_gg","http://www.jysggzy.com/TPFront/zfcg/003003/",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zsjg_gg","http://www.jysggzy.com/TPFront/zfcg/003004/",["name","ggstart_time","href","info"],f1,f2]


    ]



def work(conp,**args):
    est_meta(conp,data=data,diqu="广东省揭阳市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","127.0.0.1","guangdong","jieyang"])