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
    locator=(By.XPATH,'//div[@class="tab-item itemtw"]//li[1]/a')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    url=driver.current_url
    cnum=int(re.findall("index_([0-9]{1,})",url)[0])

    if num!=cnum:
        page_count=len(driver.page_source)
        url=re.sub("(?<=index_)[0-9]{1,}",str(num),url)
        val=driver.find_element_by_xpath("//div[@class='tab-item itemtw']/ul/li[1]/a").get_attribute('href')[-15:]
        driver.get(url)
        locator=(By.XPATH,"//div[@class='tab-item itemtw']/ul/li[1]/a[@href != '%s']"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
        WebDriverWait(driver,10).until(lambda driver:len(driver.page_source) != page_count)

    page=driver.page_source 

    soup=BeautifulSoup(page,"html.parser")

    div=soup.find("div",class_="tab-item itemtw")

    ul=div.find("ul")

    lis=ul.find_all("li")

    data=[]
    for li in lis:
        a=li.find("a")
        span=li.find("span")
        href=a['href']
        if 'http' in href:
            href=href
        else:
            href='http://zyjy.jiangmen.cn'+href

        tmp=[a["title"],href,span.text.strip()]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None

    return df 

def f2(driver):
    locator = (By.XPATH, '//div[@class="tab-item itemtw"]//li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator=(By.CLASS_NAME,"pagesite")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    total=re.findall("(?<=记录)[0-9\s/]{1,}(?=页)",driver.find_element_by_xpath("//div[@class='pagesite']/div").text)[0].split("/")[1]
    total=int(total)
    driver.quit()
    return total
def f3(driver,url):

    if 'cgzx.jiangmen.gov.cn' in url:
        return

    driver.get(url)

    locator=(By.XPATH,'//div[@class="newsCon"][string-length()>50] | //table[@class="border2"][string-length()>50]')

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
    div=soup.find('div',class_='newsTex')
    if div == None:
        div=soup.find('table',class_='border2')

    return div

data=[
        ["gcjs_zhaobiao_gg","http://zyjy.jiangmen.cn/zbgg/index_1.htm",["name","href","ggstart_time","info"],f1,f2],

        ["gcjs_zhongbiaohx_gg","http://zyjy.jiangmen.cn/jggs/index_1.htm",["name","href","ggstart_time","info"],f1,f2],

        ["gcjs_gqita_da_bian_gg","http://zyjy.jiangmen.cn/zbgzgg/index_1.htm",["name","href","ggstart_time","info"],f1,f2],

        ["gcjs_zhongbiao_gg","http://zyjy.jiangmen.cn/zbgs/index_1.htm",["name","href","ggstart_time","info"],f1,f2],

        ["zfcg_zhaobiao_gg","http://zyjy.jiangmen.cn/cggg/index_1.htm",["name","href","ggstart_time","info"],f1,f2],

        ["zfcg_zhongbiao_gg","http://zyjy.jiangmen.cn/cjgg/index_1.htm",["name","href","ggstart_time","info"],f1,f2],

        ["zfcg_zhaobiao_xunjia_gg","http://zyjy.jiangmen.cn/wsxjgg/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{'zbfs':"网上询价"}),f2],

        ["zfcg_zhongbiao_xunjiajieguo_gg","http://zyjy.jiangmen.cn/wsxjjggs/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{'zbfs':"网上询价"}),f2]
    ]



##域名变更:http://zyjy.jiangmen.cn
##修改时间:2019-06-10

def work(conp,**args):
    est_meta(conp,data=data,diqu="广东省江门市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","127.0.0.1","guangdong","jiangmen"])