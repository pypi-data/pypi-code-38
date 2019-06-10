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


import json

import time

from zhulong3.util.etl import est_html, est_meta, add_info

_name_="guangdong_zhongshan"


def f1(driver,num):
    locator=(By.XPATH,"//div[@class='nav_list']//li[1]//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=re.findall("jsp\?page=([0-9]{1,})",url)[0]
    if num!=int(cnum):
        val=driver.find_element_by_xpath("//div[@class='nav_list']//li[1]//a").get_attribute('href')[-30:]
        url=re.sub("(?<=page=)[0-9]{1,}",str(num),url)
        locator=(By.XPATH,"//div[@class='nav_list']//li[1]//a[not(contains(@href, '%s'))]"%val)
        driver.get(url)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    page=driver.page_source 
    soup=BeautifulSoup(page,"html.parser")

    div=soup.find("div",class_='nav_list')

    lis=div.find_all("li",class_="clear")
    data=[]
    for li in lis:
        try:
            a=li.find("a")
            span=li.find("span")
            tmp=[a["title"],span.text.strip(),"http://p.zsjyzx.gov.cn"+a["href"]]
        except:
            continue
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 

def f2(driver):
    locator=(By.XPATH,"//div[@class='nav_list']//li[1]//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    locator=(By.XPATH,"//div[@class='f-page']//li[@class='pageintro']")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    li=driver.find_element_by_xpath("//div[@class='f-page']//li[@class='pageintro']").text
    total=re.findall("共([0-9]{1,})页",li)[0]
    total=int(total)
    driver.quit()
    return total


def f3(driver,url):
    driver.get(url)
    driver.switch_to.frame(0)
    locator=(By.XPATH,"//div[@class='articalDiv']")
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
    div=soup.find('div',class_="articalDiv")
    return div


data=[

        ["gcjs_zhaobiao_gg","http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=58",
         ["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_gqita_bian_da_gg", "http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=59",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["gcjs_zhongbiaohx_gg","http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=60",
         ["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiao_gg","http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=61",
         ["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_gqita_liu_zhongz_gg","http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=107",
         ["name","ggstart_time","href","info"],add_info(f1, {'gglx':'项目公告'}),f2],

        ["gcjs_gqita_zhao_zhong_gg", "http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=172",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'招投标信息公开'}), f2],
        #####
        ["zfcg_zhaobiao_gg","http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=53",
         ["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhongbiao_gg","http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=55",
         ["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_biangeng_gg","http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=54",
         ["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_liubiao_gg","http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=138",
         ["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_yucai_gg", "http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=160",
         ["name", "ggstart_time", "href", "info"], f1, f2],
        ####
        ["yiliao_zhaobiao_gg", "http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=92",
         ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'医疗设备'}), f2],

        ["yiliao_biangeng_gg", "http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=93",
         ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'医疗设备'}), f2],

        ["yiliao_zhongbiaohx_gg", "http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=104",
         ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'医疗设备'}), f2],

        ["yiliao_zhongbiao_gg", "http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=105",
         ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'医疗设备'}), f2],

        ["yiliao_liubiao_gg", "http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=152",
         ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'医疗设备'}), f2],
    ####
        ["qsy_zhaobiao_gg", "http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=72",
         ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'综合交易'}), f2],

        ["qsy_gqita_bian_da_gg", "http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=112",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx': '综合交易'}), f2],

        ["qsy_gqita_zhonghx_liu_gg", "http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=113",
         ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'综合交易'}), f2],

        ["qsy_zhongbiao_gg", "http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=115",
         ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'综合交易'}), f2],

        ["qsy_gqita_gg", "http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=118",
         ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'综合交易','gglx':'其他公告'}), f2],

        ["qsy_gqita_yanqi_gg", "http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=135",
         ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'综合交易','gglx':'延期公告'}), f2],

    ]




def work(conp,**args):
    est_meta(conp,data=data,diqu="广东省中山市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","guoziqiang2","guangdong_zhongshan"])

    # driver = webdriver.Chrome()
    # url = "http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=160"
    # driver.get(url)
    # df = f2(driver)
    # print(df)

    # driver=webdriver.Chrome()
    # url = "http://p.zsjyzx.gov.cn/port/Application/NewPage/PageSubItem.jsp?page=1&node=107"
    # driver.get(url)
    # for i in range(1, 6):
    #     df=f1(driver, i)
    #     print(df.values)
