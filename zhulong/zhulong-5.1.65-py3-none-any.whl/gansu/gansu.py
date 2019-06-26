from collections import OrderedDict
from pprint import pprint

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
import json

from zhulong.util.etl import add_info,est_meta,est_html,est_tbs,add_info

_name_="gansu"



def f1(driver,num):
    
    locator=(By.XPATH,'//div[@class="annoListType"]/div[1]/dl[1]//a')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    locator=(By.XPATH,"//li[@class='paginate_button active']")
    cnum=int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text)

    if num!=cnum:
        page_count = len(driver.page_source)
        val=driver.find_element_by_xpath('//div[@class="annoListType"]/div[1]/dl[1]//a').text.strip()

        driver.execute_script("page(%s,10,'');"%num)

        locator=(By.XPATH,"//div[@class='annoListType']/div[1]/dl[1]//a[not(contains(string(),'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
        WebDriverWait(driver, 10).until(lambda driver: len(driver.page_source) != page_count)

    page=driver.page_source

    soup=BeautifulSoup(page,"html.parser")

    div=soup.find("div",class_="sTradingInformationSelectedBtoList")


    dls=div.find_all("dl")

    data=[]

    for dl in dls:
        name=dl.find("a").get_text().strip()
        href=dl.find("a")['href']
        ggstart_time=dl.find("i").text.strip()
        if 'http' in href:
            href=href
        else:
            href='http://ggzyjy.gansu.gov.cn'+href

        tmp=[name,ggstart_time,href]

        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df


def f4(driver, num):
    locator = (By.XPATH, '//div[@id="annoList"]/a[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//li[@class='paginate_button active']")
    cnum = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text)

    if num != cnum:
        page_count = len(driver.page_source)
        val = driver.find_element_by_xpath('//div[@id="annoList"]/a[1]').get_attribute('href')
        val=re.findall(r'/f/(.+)$',val)[0]

        driver.execute_script("page(%s,15,'');" % num)

        locator = (By.XPATH, "//div[@id='annoList']/a[1][not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        WebDriverWait(driver, 10).until(lambda driver: len(driver.page_source) != page_count)
    page = driver.page_source

    soup = BeautifulSoup(page, "html.parser")

    div = soup.find("div", id="annoList")

    dls = div.find_all("a")

    data = []

    for dl in dls:
        name = dl.find("div")['title']
        href = dl['href']
        ggstart_time = dl.find("span")['title']
        if 'http' in href:
            href = href
        else:
            href = 'http://47.110.5.187:3040' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f5(driver, num):
    locator = (By.XPATH, '(//li[@class="clear"])[1]//p')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//li[@class='paginate_button active']")
    cnum = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text)

    if num != cnum:
        page_count = len(driver.page_source)
        val = driver.find_element_by_xpath('(//li[@class="clear"])[1]').get_attribute('onclick')

        driver.execute_script("page(%s,20,'');" % num)

        locator = (By.XPATH, "(//li[@class='clear'])[1][not(contains(@onclick,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        WebDriverWait(driver, 10).until(lambda driver: len(driver.page_source) != page_count)
    page = driver.page_source

    soup = BeautifulSoup(page, "html.parser")

    div = soup.find_all("li", class_="clear")

    data = []

    for dl in div:
        name = dl.find("p").get_text().strip()
        href = dl['onclick']
        ggstart_time = dl.find("i").get_text().strip()

        mark_url=re.findall("opendetail\((\d+),''\)",href)[0]

        if 'http' in href:
            href = href
        else:
            href = 'http://ggzyjy.gansu.gov.cn/f/front/information/newsInfo?informationId=%s&selected=2'%mark_url

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df



def f2(driver):
    locator=(By.XPATH,"//ul[@class='pagination pagination-outline']//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    try:
        total=driver.find_element_by_xpath("//ul[@class='pagination pagination-outline']/li[last()-2]/a").text
        total=int(total)
    except:
        total=1

    driver.quit()
    return total



def chang_address(f,num1,num2):
    def wrap(*arg):
        driver=arg[0]
        locator = (By.XPATH, '//div[@class="annoListType"]/div[1]/dl[1]//a')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        total = driver.find_element_by_xpath("//ul[@class='pagination pagination-outline']/li[last()-2]/a").text
        total = int(total)

        if (total > 700 and num2 ==1) or (total > 1700 and num2 == 2):
            val=driver.find_element_by_xpath('//div[@class="annoListType"]/div[1]/dl[1]//a').text.strip()

            input_diqu=driver.find_element_by_xpath('//input[@id="area%s"]'%num1)
            driver.execute_script("arguments[0].click()", input_diqu)
            locator = (By.XPATH, "//div[@class='annoListType']/div[1]/dl[1]//a[not(contains(string(),'%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

            if num2 == 2:
                input_ggtype=driver.find_element_by_xpath('//input[@id="projectTypeId%s"]'%num2)
                driver.execute_script("arguments[0].click()", input_ggtype)
                val = driver.find_element_by_xpath('//div[@class="annoListType"]/div[1]/dl[1]//a').text.strip()
                locator = (By.XPATH, "//div[@class='annoListType']/div[1]/dl[1]//a[not(contains(string(),'%s'))]" % val)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        return f(*arg)

    return wrap


def change_type(f,num1):
    def wrap(*arg):
        driver=arg[0]
        locator = (By.XPATH, '//div[@id="annoList"]/a[1]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        ctext=driver.find_element_by_xpath('//li[@class="yGovTypeMenuActive"]/h3').text

        if ctext == '限额以下工程建设':

            val = driver.find_element_by_xpath('//div[@id="annoList"]/a[1]').get_attribute('href')
            val = re.findall(r'/f/(.+)$', val)[0]

            ele = driver.find_element_by_xpath('//ul[@class="yGovTypeMenuWrap clear"]/li[%s]' % num1)
            driver.execute_script("arguments[0].click()", ele)

            locator = (By.XPATH, "//div[@id='annoList']/a[1][not(contains(@href,'%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        return f(*arg)
    return wrap



def f3(driver,url):


    driver.get(url)

    locator=(By.XPATH,'//div[@class="jxTradingPublic"][string-length()>100] | '
                      '//div[@id="content"][string-length()>100] | //div[@class="gNewsInfoDetailMain"]//iframe | '
                      '//div[@class="jxGonggaoInformationDetail"]//iframe')

    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        fra=driver.find_element_by_xpath('//div[contains(@class,"annogoods")][not(@style)]//div[@class="jxGonggaoInformationDetail"]//iframe')
        driver.switch_to.frame(fra)
        mark=1
        locator = (By.XPATH, '//body[string-length()>500]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    except:
        mark=0



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

    div=soup.find('div',class_='jxTradingPublic')
    if div == None:
        div=soup.find('div',id='content')
        if div == None:
            div = soup.find('div',class_='gNewsInfoDetailMain')
            if div == None and mark==1:
                div=soup.find('body')
                if '有效期失效不能访问' in page:
                    raise ValueError('ip失效')
    driver.switch_to.parent_frame()
    return div


def get_data():
    data = []

    ##zfcg_gcjs

    adtype1 = OrderedDict([("兰州", "1"), ("嘉峪关", "2"),("金昌","3"),("白银","4"),
                           ('天水', '5'), ("武威", "6"), ("张掖", "7"), ("平凉", "8"),('酒泉',"9"),
                           ('庆阳',"10"),("定西","11"),('陇南','12'),('临夏','13'),('甘南','14'),('省级平台(兰州新区)','15')])

    #gcjs

    for w2 in adtype1.keys():
        href = "http://ggzyjy.gansu.gov.cn/f/newprovince/annogoods/list?selectedProjectType=1"
        tmp = ["gcjs_zhaobiao_diqu%s_gg" % (adtype1[w2]), href, ["name","ggstart_time","href",'info'],
               chang_address(add_info(f1, {"diqu": w2}),adtype1[w2], 1) , chang_address(f2,adtype1[w2],1)]
        data.append(tmp)

    #zfcg
    for w2 in adtype1.keys():
        href = "http://ggzyjy.gansu.gov.cn/f/newprovince/annogoods/list?selectedProjectType=2"
        tmp = ["zfcg_zhaobiao_diqu%s_gg" % (adtype1[w2]), href, ["name","ggstart_time","href",'info'],
               chang_address(add_info(f1, {"diqu": w2}),adtype1[w2], 2) , chang_address(f2,adtype1[w2],2)]
        data.append(tmp)


    data1 = data.copy()

    data3 = [

        ["gcjs_zhaobiao_diqu0_gg", "http://ggzyjy.gansu.gov.cn/f/newprovince/annogoods/list?selectedProjectType=1",
         ["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':'省级平台(省局)'}), f2],
        ["zfcg_zhaobiao_diqu0_gg", "http://ggzyjy.gansu.gov.cn/f/newprovince/annogoods/list?selectedProjectType=2",
         ["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':'省级平台(省局)'}), f2],
        ["jqita_zhaobiao_gg", "http://ggzyjy.gansu.gov.cn/f/newprovince/annogoods/list?selectedProjectType=0",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '重大项目'}), f2],
        ["gcjs_zhaobiao_xiane_gg", "http://47.110.5.187:3040/f", ["name", "ggstart_time", "href", "info"],
         add_info(f1, {'tag': '限额以下交易'}), f2],
        ["zfcg_zhaobiao_xieyi_gg", "http://47.110.5.187:3040/f", ["name", "ggstart_time", "href", "info"],
         change_type(add_info(f1, {'tag': '限额以下交易'}), 2), change_type(f2, 2)],
        ["zfcg_zhaobiao_xiane_gg", "http://47.110.5.187:3040/f", ["name", "ggstart_time", "href", "info"],
         change_type(add_info(f1, {'tag': '限额以下交易'}), 3), change_type(f2, 3)],

        ["yiliao_zhaobiao_jizhong_gg",
         "http://ggzyjy.gansu.gov.cn/f/front/information/infoitemList?siteitemid=37&selecteditem=97&selected=2",
         ["name", "ggstart_time", "href", "info"], add_info(f5, {'tag': '药品集中采购'}), f2],
        ["yiliao_zhongbiao_jizhong_gg",
         "http://ggzyjy.gansu.gov.cn/f/front/information/infoitemList?siteitemid=37&selecteditem=123&selected=2",
         ["name", "ggstart_time", "href", "info"], add_info(f5, {'tag': '药品集中采购'}), f2],

        ["yiliao_zhaobiao_yangguang_gg",
         "http://ggzyjy.gansu.gov.cn/f/front/information/infoitemList?siteitemid=37&selecteditem=247&selected=2",
         ["name", "ggstart_time", "href", "info"], add_info(f5, {'tag': '药品阳光采购'}), f2],
        ["yiliao_zhongbiao_yangguang_gg",
         "http://ggzyjy.gansu.gov.cn/f/front/information/infoitemList?siteitemid=37&selecteditem=248&selected=2",
         ["name", "ggstart_time", "href", "info"], add_info(f5, {'tag': '药品阳光采购'}), f2],

        ["yiliao_zhaobiao_haocai_gg",
         "http://ggzyjy.gansu.gov.cn/f/front/information/infoitemList?siteitemid=37&selecteditem=250&selected=2",
         ["name", "ggstart_time", "href", "info"], add_info(f5, {'tag': '医用耗材阳光采购'}), f2],
        ["yiliao_zhongbiao_haocai_gg",
         "http://ggzyjy.gansu.gov.cn/f/front/information/infoitemList?siteitemid=37&selecteditem=251&selected=2",
         ["name", "ggstart_time", "href", "info"], add_info(f5, {'tag': '医用耗材阳光采购'}), f2],

        ["yiliao_zhaobiao_tiwai_gg",
         "http://ggzyjy.gansu.gov.cn/f/front/information/infoitemList?siteitemid=37&selecteditem=326&selected=2",
         ["name", "ggstart_time", "href", "info"], add_info(f5, {'tag': '体外诊断试剂阳光采购'}), f2],
        ["yiliao_zhongbiao_tiwai_gg",
         "http://ggzyjy.gansu.gov.cn/f/front/information/infoitemList?siteitemid=37&selecteditem=327&selected=2",
         ["name", "ggstart_time", "href", "info"], add_info(f5, {'tag': '体外诊断试剂阳光采购'}), f2],

    ]

    data1.extend(data3)
    return data1




data=get_data()
# pprint(data)


def work(conp,**args):
    est_meta(conp,data=data,diqu="甘肃省",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    # work(conp=["postgres","since2015",'192.168.3.171',"gansu","gansu"],headless=True,total=4)
    pass
    # driver=webdriver.Chrome()
    # f=f3(driver,'http://ggzyjy.gansu.gov.cn/f/cityTenderProject/0876-1812243/cityTenderprojectIndex?projectType=D&table=purchase_quali_inquery_ann')
    # print(f)