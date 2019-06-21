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
_name_="meizhou"


def f1(driver,num):

    locator=(By.CLASS_NAME,"ewb-data-items")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    url=driver.current_url
    cnum=int(re.findall("(?<=Paging=)[0-9]{1,}",url)[0])

    if num!=cnum:
        url=re.sub("(?<=Paging=)[0-9]{1,}",str(num),url)
        locator=(By.XPATH,"//ul[@class='ewb-data-items ewb-pt6']/li[1]//a")
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
        val=driver.find_element_by_xpath("//ul[@class='ewb-data-items ewb-pt6']/li[1]//a").text
        driver.get(url)
        locator=(By.XPATH,"//ul[@class='ewb-data-items ewb-pt6']/li[1]//a[string()!='%s']"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    page=driver.page_source 
    soup=BeautifulSoup(page,"html.parser")

    ul=soup.find("ul",class_="ewb-data-items")
    lis=ul.find_all("li")
    data=[]

    for li in lis:
        a=li.find("a")
        span=li.find("span")
        tmp=[a['title'],span.text.strip(),"http://mzggzy.meizhou.gov.cn"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 

def f2(driver):
    locator=(By.CLASS_NAME,"ewb-data-items")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    locator=(By.XPATH,"//div[@class='pagemargin']//td[@class='huifont']")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    total=driver.find_element_by_xpath("//div[@class='pagemargin']//td[@class='huifont']").text.split("/")[1]
    total=int(total)
    driver.quit()
    return total


def f3(driver,url):


    driver.get(url)

    locator=(By.XPATH,"//table[@width='100%']")

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

    div=soup.find('table',width='100%')
    #div=div.find_all('div',class_='ewb-article')[0]
    
    return div


data=[
        ["gcjs_zhaobiao_gg","http://mzggzy.meizhou.gov.cn/TPFront/jsgc/004001/Default.aspx?Paging=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiaohx_gg","http://mzggzy.meizhou.gov.cn/TPFront/jsgc/004004/Default.aspx?Paging=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiao_gg","http://mzggzy.meizhou.gov.cn/TPFront/jsgc/004005/Default.aspx?Paging=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zsjg_gg","http://mzggzy.meizhou.gov.cn/TPFront/jsgc/004003/Default.aspx?Paging=1",["name","ggstart_time","href","info"],f1,f2],




        ["zfcg_zhaobiao_gg","http://mzggzy.meizhou.gov.cn/TPFront/zfcg/003001/Default.aspx?Paging=1",["name","ggstart_time","href","info"],f1,f2],


        ["zfcg_biangeng_gg","http://mzggzy.meizhou.gov.cn/TPFront/zfcg/003002/Default.aspx?Paging=1",["name","ggstart_time","href","info"],f1,f2],


        ["zfcg_zhongbiao_gg","http://mzggzy.meizhou.gov.cn/TPFront/zfcg/003003/Default.aspx?Paging=1",["name","ggstart_time","href","info"],f1,f2],



    ]


def work(conp,**args):
    est_meta(conp,data=data,diqu="广东省梅州市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","127.0.0.1","guangdong","meizhou"])

