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
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs
from collections import OrderedDict

_name_='dongying'


def f1(driver, num):
    locator = (By.XPATH, "//*[@id='MoreInfoList1_DataGrid1']/tbody/tr[1]/td[2]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        cnum = int(driver.find_element_by_xpath('//*[@id="MoreInfoList1_Pager"]/table/tbody/tr/td[1]/font[3]/b').text)
    except StaleElementReferenceException:
        cnum = int(driver.find_element_by_xpath('//*[@id="MoreInfoList1_Pager"]/table/tbody/tr/td[1]/font[3]/b').text)
    val = driver.find_element_by_xpath('//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a').get_attribute('href')[-35:]
    if num != cnum:
        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','{}')".format(num))
        time.sleep(0.5)
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
            td = tr.find_all("td")[2]
            tmp = [a["title"], td.text.strip(), "http://ggzy.dongying.gov.cn" + a["href"]]
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
    locator = (By.XPATH, "//*[@id='MoreInfoList1_DataGrid1']/tbody/tr[1]/td[2]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.ID, 'MoreInfoList1_Pager')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        txt=driver.find_element_by_id("MoreInfoList1_Pager").text
        total=int(re.findall("总页数：([0-9]*)",txt)[0])
    except:
        total=1
    driver.quit()
    return total


def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH,"//td[@class='infodetail'][string-length()>30]")
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
    div=soup.find('td',class_='infodetail')
    return div


def get_data():
    xs=OrderedDict([("东营市","001"),("东营区","002"),("河口区","003"),("广饶县","004"),("垦利区","005")
        ,("利津县","006"),("开发区","007"),("东营港","008"),("农高区","009")])

    ggtype1=OrderedDict([("zhaobiao","001"),("zhongbiao","003"),("gqita_liu_zhongz","004"),("biangeng","005")])

    ggtype2=OrderedDict([("zhaobiao","001"),("biangeng","002"),("gqita_zhong_liu","003")])
    data=[]

    for w1 in ggtype1.keys():
        for w2 in xs.keys():
            p1="004001%s"%(ggtype1[w1])
            p2="004001%s%s"%(ggtype1[w1],xs[w2])
            href="http://ggzy.dongying.gov.cn/dyweb/004/004001/%s/%s/MoreInfo.aspx?CategoryNum=%s"%(p1,p2,p2)
            tmp=["gcjs_%s_diqu%s_gg"%(w1,xs[w2]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w2}),f2]
            data.append(tmp)


    for w1 in ggtype2.keys():
        for w2 in xs.keys():
            p1="004002%s"%(ggtype2[w1])
            p2="004002%s%s"%(ggtype2[w1],xs[w2])
            href="http://ggzy.dongying.gov.cn/dyweb/004/004002/%s/%s/MoreInfo.aspx?CategoryNum=%s"%(p1,p2,p2)
            tmp=["zfcg_%s_diqu%s_gg"%(w1,xs[w2]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w2}),f2]
            data.append(tmp)
    data1=data.copy()
    arr=[]
    for w in data:
        if w[0] in arr:data1.remove(w)
    return data1

data=get_data()


def work(conp, **args):
    est_meta(conp,data=data,diqu="山东省东营市",**args)
    est_html(conp,f=f3, **args)

if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","dongying"])


# 更改时间：2019/5/27
# 网址更新：http://ggzy.dongying.gov.cn/dyweb/





