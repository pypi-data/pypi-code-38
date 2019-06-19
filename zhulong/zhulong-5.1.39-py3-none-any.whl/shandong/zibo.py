import time
import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs
from collections import OrderedDict

_name_='zibo'


def f1(driver, num):
    locator = (By.XPATH, "//*[@id='MoreInfoList1_DataGrid1']/tbody/tr[1]/td[2]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        cnum = int(driver.find_element_by_xpath('//*[@id="MoreInfoList1_Pager"]/div[1]/font[3]/b').text)
    except Exception as e:
        cnum = 1
    if num != cnum:
        val = driver.find_element_by_xpath('//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a').get_attribute('href')[-40:]
        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','{}')".format(num))
        locator = (By.XPATH, "//*[@id='MoreInfoList1_DataGrid1']/tbody/tr[1]/td[2]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tbody = soup.find("table", id="MoreInfoList1_DataGrid1")
    trs = tbody.find_all("tr")
    data = []
    for tr in trs:
        try:
            a = tr.find("a")
            title = a["title"].strip()
            if '</font>' in title:
                title = re.findall(r'(.*)<font', title)[0]
            td = tr.find_all("td")[2]
            tmp = [title, td.text.strip(), "http://ggzyjy.zibo.gov.cn" + a["href"]]
            data.append(tmp)
        except:
            a = tr.find_all("td")[1]
            td = tr.find_all("td")[2]
            tmp = [a.text.strip(), td.text.strip(), "-"]
            data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df




def f2(driver):
    try:
        locator = (By.ID, 'MoreInfoList1_Pager')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        txt=driver.find_element_by_id("MoreInfoList1_Pager").text
        total=int(re.findall("总页数：([0-9]*)",txt)[0])
        val = driver.find_element_by_xpath("//div[@id='MoreInfoList1_Pager']").text
        tal = int(re.findall("记录总数：([0-9]*)", val)[0])
        if tal == 0:
            return 0
    except:
        if '404 - 找不到文件或目录' in driver.page_source:
            return 0
        if ('本栏目信息正在更新中' in driver.page_source) or ('404' in driver.title):
            return 0
        total=1
    driver.quit()
    return total


def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH,"//table[@id='tblInfo'][string-length()>40]")
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
    div=soup.find('table',id='tblInfo')
    return div

def get_data():
    data=[]
    ggtype1=OrderedDict([("zhaobiao","001"),("biangeng","002"),("gqita_zhong_liu","003")])
    sx=OrderedDict([("市本级","001"),("张店区","002"),("高新区","004"),("文昌湖区","005"),("高青县","006"),("临淄区","007"),("桓台县","008"),("博山区","009"),("周村区", "010"),("经济开发区", "011"),("沂源县","012")])
    for w1 in ggtype1.keys():
        for w2 in sx.keys():
            p1 = "002001%s" % ggtype1[w1]
            p2 = "002001%s%s" % (ggtype1[w1], sx[w2])
            href = "http://ggzyjy.zibo.gov.cn/TPFront/jyxx/002001/%s/%s/" % (p1, p2)
            tmp=["gcjs_%s_diqu%s_gg"%(w1,sx[w2]),href,["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":w2}),f2]
            data.append(tmp)

    ggtype2=OrderedDict([("zhaobiao","001"),("biangeng","002"),("zhongbiaohx","003"),("yucai","004")])
    sx2=OrderedDict([("市本级","001"),("张店区","002"),("高新区","004"),("文昌湖区","005"),("沂源县","006"),("博山区","007"),("高青县","008"),("临淄区","009"),("桓台县","010")
                        ,("淄川区", "011"),("周村区", "012"),("经济开发区", "013")])
    ggtype22 = OrderedDict([("liubiao", "005")])
    sx22=OrderedDict([("市本级","001"),("张店区","002"),("高新区","003"),("文昌湖区","004"),("沂源县","005"),("博山区","006"),("高青县","007"),("临淄区","008"),("桓台县","009")
                        ,("淄川区", "010"),("周村区", "011"),("经济开发区", "012")])
    for w1 in ggtype2.keys():
        for w2 in sx2.keys():
            p1 = "002002%s" % ggtype2[w1]
            p2 = "002002%s%s" % (ggtype2[w1], sx2[w2])
            href = "http://ggzyjy.zibo.gov.cn/TPFront/jyxx/002002/%s/%s/" % (p1, p2)
            tmp=["zfcg_%s_diqu%s_gg"%(w1,sx2[w2]),href,["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":w2}),f2]
            data.append(tmp)

    for w1 in ggtype22.keys():
        for w2 in sx22.keys():
            p1 = "002002%s" % ggtype22[w1]
            p2 = "002002%s%s" % (ggtype22[w1], sx22[w2])
            href = "http://ggzyjy.zibo.gov.cn/TPFront/jyxx/002002/%s/%s/" % (p1, p2)
            tmp=["zfcg_%s_diqu%s_gg"%(w1,sx22[w2]),href,["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":w2}),f2]
            data.append(tmp)

    data1=data.copy()
    arr=[]
    for w in data:
        if w[0] in arr:data1.remove(w)
    return data1

data=get_data()

def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省淄博市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","zibo"])

    # driver = webdriver.Chrome()
    # url ="http://ggzyjy.zibo.gov.cn/TPFront/jyxx/002001/002001002/002001002012/"
    # driver.get(url)
    # df=f2(driver)
    # print(df)

