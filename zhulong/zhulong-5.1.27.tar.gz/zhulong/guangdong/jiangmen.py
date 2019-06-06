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
_name_="jiangmen"


def f1(driver,num):
    locator=(By.CLASS_NAME,"itemtw")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    url=driver.current_url
    cnum=int(re.findall("index_([0-9]{1,})",url)[0])
    if num!=cnum:
        url=re.sub("(?<=index_)[0-9]{1,}",str(num),url)
        val=driver.find_element_by_xpath("//div[@class='tab-item itemtw']/ul/li[1]/a").text
        driver.get(url)
        locator=(By.XPATH,"//div[@class='tab-item itemtw']/ul/li[1]/a[string()!='%s']"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    page=driver.page_source 

    soup=BeautifulSoup(page,"html.parser")

    div=soup.find("div",class_="tab-item itemtw")

    ul=div.find("ul")

    lis=ul.find_all("li")

    data=[]
    for li in lis:
        a=li.find("a")
        span=li.find("span")
        tmp=[a["title"],a['href'],span.text.strip()]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None

    return df 

def f2(driver):
    locator=(By.CLASS_NAME,"itemtw")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    locator=(By.CLASS_NAME,"pagesite")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    total=re.findall("(?<=记录)[0-9\s/]{1,}(?=页)",driver.find_element_by_xpath("//div[@class='pagesite']/div").text)[0].split("/")[1]
    total=int(total)
    driver.quit()
    return total
def f3(driver,url):


    driver.get(url)
    try:
        locator=(By.CLASS_NAME,"newsTex")

        WebDriverWait(driver,5).until(EC.presence_of_all_elements_located(locator))
    except:
        pass
        # locator=(By.XPATH,"//table[@width='860']")

        # WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))

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
    if soup.find('div',class_='newsTex') is not None:
        div=soup.find('div',class_='newsTex')
    else:
        div=soup.find('table',width='860')
    #div=div.find_all('div',class_='ewb-article')[0]
    
    return div

data=[
        ["gcjs_zhaobiao_gg","http://zyjy.jiangmen.gov.cn/zbgg/index_1.htm",["name","href","ggstart_time","info"],f1,f2],

        ["gcjs_zhongbiaohx_gg","http://zyjy.jiangmen.gov.cn/jggs/index_1.htm",["name","href","ggstart_time","info"],f1,f2],

        ["gcjs_zhongbiao_gg","http://zyjy.jiangmen.gov.cn/zbgs/index_1.htm",["name","href","ggstart_time","info"],f1,f2],

        ["zfcg_zhaobiao_gg","http://zyjy.jiangmen.gov.cn/cggg/index_1.htm",["name","href","ggstart_time","info"],f1,f2],

        ["zfcg_zhongbiao_gg","http://zyjy.jiangmen.gov.cn/cjgg/index_1.htm",["name","href","ggstart_time","info"],f1,f2],

        ["zfcg_zhaobiao_xunjia_gg","http://zyjy.jiangmen.gov.cn/wsxjgg/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{'zbfs':"网上询价"}),f2],

        ["zfcg_zhongbiao_xunjiajieguo_gg","http://zyjy.jiangmen.gov.cn/wsxjjggs/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{'zbfs':"网上询价"}),f2]
    ]



def work(conp,**args):
    est_meta(conp,data=data,diqu="广东省江门市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","127.0.0.1","guangdong","jiangmen"])