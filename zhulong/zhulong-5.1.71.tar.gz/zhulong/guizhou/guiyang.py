
import pandas as pd
import re

import requests
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

import json
from zhulong.util.etl import gg_meta,gg_html,est_meta,est_html,est_tbs,add_info
from zhulong.util.fake_useragent import UserAgent

_name_="guiyang"
def f1(driver,num):
    locator = (By.XPATH, '//div[@class="list"]/ul/div[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url=driver.current_url
    cnum=int(re.findall('index_(\d+).htm',url)[0])
    
    if cnum != num:
        val=driver.find_element_by_xpath('//div[@class="list"]/ul/div[1]//a').get_attribute('href')[-30:]

        url=re.sub("index_\d+.htm","index_%s.htm"%num,url)
    
        driver.get(url)
    
        locator=(By.XPATH,'//div[@class="list"]/ul/div[1]//a[not(contains(@href,"%s"))]'%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    
    
    page=driver.page_source
    soup=BeautifulSoup(page,"html.parser")
    divs=soup.find_all(class_="c1-bline")
    data=[]
    for div in divs:
        name=div.find("a")['title']
        href=div.find("a")['href']
        ggstart_time=div.find("div",class_="f-right").get_text()

        tmp=[name,href,ggstart_time]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df



def f4(driver,num):
    locator = (By.XPATH, '//div[@id="ajaxpage-list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum=int(driver.find_element_by_xpath('//div[@id="pages"]/span').text)

    if cnum != num:
        page_count=len(driver.page_source)
        val = driver.find_element_by_xpath('//div[@id="ajaxpage-list"]/li[1]/a').get_attribute('href')[-30:]

        driver.execute_script('ajaxGoPage(%d)'%num)

        locator = (By.XPATH, '//div[@id="ajaxpage-list"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        WebDriverWait(driver, 10).until(lambda driver: len(driver.page_source) != page_count)
    page=driver.page_source
    soup=BeautifulSoup(page,"html.parser")
    div=soup.find(id="ajaxpage-list")
    lis=div.find_all("li")
    data=[]
    for li in lis:
        name=li.find("a").get_text()
        href=li.find("a")['href']
        ggstart_time=li.find("code").get_text()

        tmp=[name,href,ggstart_time]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    return df

def f2(driver):
    locator=(By.XPATH,'//div[@class="list"]/ul/div[1]//a')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    try:
        stext=driver.find_element_by_xpath("//div[@class='pg-3']/span[@class='total']").text
        rr=re.compile("共(.*)页")
        total=int(rr.findall(stext)[0])
    except:
        total=1
    driver.quit()

    return total

def f2_zf(driver):
    locator=(By.XPATH,'//div[@id="ajaxpage-list"]/li[1]/a')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    try:
        stext=driver.find_element_by_xpath("//div[@id='pages']/font/font/font").text
        rr=re.compile("共(.*)页")
        total=int(rr.findall(stext)[0])
    except:
        total=1

    driver.quit()

    return total
def f3(driver,url):

    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies={}

    ua = UserAgent()

    headers = {
        "User-Agent": ua.chrome,
    }

    req=requests.get(url,proxies=proxies,headers=headers,timeout=20)
    if req.status_code != 200:
        raise ValueError('status code is %s'%req.status_code)
    page=req.text

    # driver.get(url)
    #
    # locator = (By.XPATH, '//div[@class="sub-cont2"][string-length()>100] | //div[@class="text_c"][string-length()>100]')
    # WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    #
    # before=len(driver.page_source)
    # time.sleep(0.1)
    # after=len(driver.page_source)
    # i=0
    # while before!=after:
    #     before=len(driver.page_source)
    #     time.sleep(0.1)
    #     after=len(driver.page_source)
    #     i+=1
    #     if i>5:break
    #
    # page=driver.page_source

    soup=BeautifulSoup(page,'html.parser')

    div = soup.find('div',class_='sub-cont2')

    if div == None:
        div = soup.find('div',class_='text_c')

    if not div:
        raise ValueError

    return div


data=[
["gcjs_yucai_sg_gg","http://222.85.133.14:8899/buildNewsConstruts/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"施工"}),f2],
["gcjs_yucai_jl_gg","http://222.85.133.14:8899/buindNewsService/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"监理"}),f2],
["gcjs_yucai_sj_gg","http://222.85.133.14:8899/buildNewsDesigner/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"设计"}),f2],
["gcjs_yucai_ck_gg","http://222.85.133.14:8899/buildNewsrecon/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"勘察"}),f2],
["gcjs_yucai_sb_gg","http://222.85.133.14:8899/buildNewsEuqip/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"设备"}),f2],
["gcjs_yucai_zcb_gg","http://222.85.133.14:8899/buildContracting/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"总承包"}),f2],


["gcjs_zhaobiao_sg_gg","http://222.85.133.14:8899/noticeconstruct/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"施工"}),f2],
["gcjs_zhaobiao_jl_gg","http://222.85.133.14:8899/noticeservice/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"监理"}),f2],
["gcjs_zhaobiao_sj_gg","http://222.85.133.14:8899/noticedesign/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"设计"}),f2],
["gcjs_zhaobiao_ck_gg","http://222.85.133.14:8899/noticereconnaissance/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"勘察"}),f2],
["gcjs_zhaobiao_sb_gg","http://222.85.133.14:8899/noticequipment/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"设备"}),f2],
["gcjs_zhaobiao_zcb_gg","http://222.85.133.14:8899/noticeContracting/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"总承包"}),f2],


["gcjs_zhongbiao_sg_gg","http://222.85.133.14:8899/succonstruct/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"施工"}),f2],
["gcjs_zhongbiao_jl_gg","http://222.85.133.14:8899/succservice/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"监理"}),f2],
["gcjs_zhongbiao_sj_gg","http://222.85.133.14:8899/succdesign/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"设计"}),f2],
["gcjs_zhongbiao_ck_gg","http://222.85.133.14:8899/succreconnaissance/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"勘察"}),f2],
["gcjs_zhongbiao_sb_gg","http://222.85.133.14:8899/succequipment/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"设备"}),f2],
["gcjs_zhongbiao_zcb_gg","http://222.85.133.14:8899/contracting/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"总承包"}),f2],


["gcjs_gqita_baojian_sg_gg","http://222.85.133.14:8899/buildNewsConstruts/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"总承包","jytype":"报建信息"}),f2],
["gcjs_gqita_baojian_jl_gg","http://222.85.133.14:8899/buindNewsService/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"监理","jytype":"报建信息"}),f2],
["gcjs_gqita_baojian_sj_gg","http://222.85.133.14:8899/buildNewsDesigner/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"设计","jytype":"报建信息"}),f2],
["gcjs_gqita_baojian_ck_gg","http://222.85.133.14:8899/buildNewsrecon/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"勘察","jytype":"报建信息"}),f2],
["gcjs_gqita_baojian_sb_gg","http://222.85.133.14:8899/buildNewsEuqip/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"设备","jytype":"报建信息"}),f2],
["gcjs_gqita_baojian_zcb_gg","http://222.85.133.14:8899/buildContracting/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"总承包","jytype":"报建信息"}),f2],

#
["gcjs_zhaobiao_zjfb_gg","http://222.85.133.14:8899/directPub/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{'gctype':'直接发包'}),f2],
["gcjs_biangeng_gg","http://222.85.133.14:8899/changepub/index_1.htm",["name","href","ggstart_time","info"],f1,f2],
["gcjs_liubiao_gg","http://222.85.133.14:8899/flowNotice/index_1.htm",["name","href","ggstart_time","info"],f1,f2],
["gcjs_gqita_lanbiao_gg","http://222.85.133.14:8899/priceLevelPub/index_1.htm",["name","href","ggstart_time","info"],add_info(f1,{"gctype":"拦标价公示"}),f2],


["zfcg_zhaobiao_hw_gg","http://ggzy.guiyang.gov.cn/c14512/index.html",["name","href","ggstart_time","info"],add_info(f4,{"gctype":"货物"}),f2_zf],
["zfcg_zhaobiao_fw_gg","http://ggzy.guiyang.gov.cn/c14513/index.html",["name","href","ggstart_time","info"],add_info(f4,{"gctype":"服务"}),f2_zf],
["zfcg_zhaobiao_gc_gg","http://ggzy.guiyang.gov.cn/c14514/index.html",["name","href","ggstart_time","info"],add_info(f4,{"gctype":"工程"}),f2_zf],

["zfcg_biangeng_hw_gg","http://ggzy.guiyang.gov.cn/c14518/index.html",["name","href","ggstart_time","info"],add_info(f4,{"gctype":"货物"}),f2_zf],
["zfcg_biangeng_fw_gg","http://ggzy.guiyang.gov.cn/c14519/index.html",["name","href","ggstart_time","info"],add_info(f4,{"gctype":"服务"}),f2_zf],
["zfcg_biangeng_gc_gg","http://ggzy.guiyang.gov.cn/c14520/index.html",["name","href","ggstart_time","info"],add_info(f4,{"gctype":"工程"}),f2_zf],

["zfcg_zhongbiaohx_hw_gg","http://ggzy.guiyang.gov.cn/c14515/index.html",["name","href","ggstart_time","info"],add_info(f4,{"gctype":"货物"}),f2_zf],
["zfcg_zhongbiaohx_fw_gg","http://ggzy.guiyang.gov.cn/c14516/index.html",["name","href","ggstart_time","info"],add_info(f4,{"gctype":"服务"}),f2_zf],
["zfcg_zhongbiaohx_gc_gg","http://ggzy.guiyang.gov.cn/c14517/index.html",["name","href","ggstart_time","info"],add_info(f4,{"gctype":"工程"}),f2_zf],

["zfcg_zhaobiao_danyilaiyuan_hw_gg","http://ggzy.guiyang.gov.cn/c14521/index.html",["name","href","ggstart_time","info"],add_info(f4,{"gctype":"货物",'zbfs':'单一来源'}),f2_zf],
["zfcg_zhaobiao_danyilaiyuan_fw_gg","http://ggzy.guiyang.gov.cn/c14522/index.html",["name","href","ggstart_time","info"],add_info(f4,{"gctype":"服务",'zbfs':'单一来源'}),f2_zf],
["zfcg_zhaobiao_danyilaiyuan_gc_gg","http://ggzy.guiyang.gov.cn/c14523/index.html",["name","href","ggstart_time","info"],add_info(f4,{"gctype":"工程",'zbfs':'单一来源'}),f2_zf],

["zfcg_liubiao_hw_gg","http://ggzy.guiyang.gov.cn/c14524/index.html",["name","href","ggstart_time","info"],add_info(f4,{"gctype":"货物"}),f2_zf],
["zfcg_liubiao_fw_gg","http://ggzy.guiyang.gov.cn/c14525/index.html",["name","href","ggstart_time","info"],add_info(f4,{"gctype":"服务"}),f2_zf],
["zfcg_liubiao_gc_gg","http://ggzy.guiyang.gov.cn/c14526/index.html",["name","href","ggstart_time","info"],add_info(f4,{"gctype":"工程"}),f2_zf],


["zfcg_zhongbiao_hw_gg","http://ggzy.guiyang.gov.cn/c14527/index.html",["name","href","ggstart_time","info"],add_info(f4,{"gctype":"货物"}),f2_zf],
["zfcg_zhongbiao_fw_gg","http://ggzy.guiyang.gov.cn/c14528/index.html",["name","href","ggstart_time","info"],add_info(f4,{"gctype":"服务"}),f2_zf],
["zfcg_zhongbiao_gc_gg","http://ggzy.guiyang.gov.cn/c14529/index.html",["name","href","ggstart_time","info"],add_info(f4,{"gctype":"工程"}),f2_zf]

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="贵州省贵阳市",**args)
    est_html(conp,f=f3,**args)

if __name__ == '__main__':

    # work(conp=["postgres","zhulong.com.cn","192.168.169.47","guizhou","guiyang"])
    work(conp=["postgres","since2015","192.168.3.171","guizhou","guiyang"])