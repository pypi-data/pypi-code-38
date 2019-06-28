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
from zhulong.util.etl import est_tables,gg_meta,gg_html,est_html,est_meta


_name_='rizhao'



def f1(driver, num):
    locator = (By.XPATH, '//*[@id="DataList1"]/tbody/tr[1]/td/li/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = int(re.findall("Paging=(\d+)", url)[0])
    if num != cnum:
        if num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        val = driver.find_element_by_xpath("//*[@id='DataList1']/tbody/tr[1]/td/li/a").get_attribute('href')[-35:]
        driver.get(url)
        locator = (By.XPATH, "//*[@id='DataList1']/tbody/tr[1]/td/li/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    ul = soup.find("table", id="DataList1")
    trs = ul.find_all("tr")
    data = []
    for li in trs:
        a = li.find("a")
        link = "http://ggzyjy.rizhao.gov.cn:8607/rzwz/" + re.findall('../(.*)', a["href"])[0]
        try:
            span1 = li.find("div", class_="news-txt l").text.strip()
        except:
            span1 = "-"
        try:
            span2 = li.find("div", class_="news-date r").text.strip()
        except:
            span2 = "-"
        tmp = [span1, span2, link]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"]=None
    return df


def f2(driver):
    locator = (By.XPATH, "(//div[@class='news-txt l'])[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//td[@class='huifont']")
    page_all = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    page = re.findall('/(\d+)', page_all)[0]
    driver.quit()
    return int(page)


def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH,"//div[@class='detail-content'][string-length()>30]")
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
    div=soup.find('div',class_='detail-content')
    return div

data = [
        ["gcjs_zhaobiao_gg","http://ggzyjy.rizhao.gov.cn:8607/rzwz/ShowInfo/MoreJyxxList.aspx?categoryNum=071001001&Paging=1",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_biangeng_gg", "http://ggzyjy.rizhao.gov.cn:8607/rzwz/ShowInfo/MoreJyxxList.aspx?categoryNum=071001002&Paging=1",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_zhongbiao_gg", "http://ggzyjy.rizhao.gov.cn:8607/rzwz/ShowInfo/MoreJyxxList.aspx?categoryNum=071001003&Paging=1",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_liubiao_gg", "http://ggzyjy.rizhao.gov.cn:8607/rzwz/ShowInfo/MoreJyxxList.aspx?categoryNum=071001004&Paging=1",
         ["name", "ggstart_time", "href","info"],f1,f2],


        ["zfcg_yucai_gg", "http://ggzyjy.rizhao.gov.cn:8607/rzwz/ShowInfo/MoreJyxxList.aspx?categoryNum=071002001&Paging=1",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_zhaobiao_gg", "http://ggzyjy.rizhao.gov.cn:8607/rzwz/ShowInfo/MoreJyxxList.aspx?categoryNum=071002002&Paging=1",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_biangeng_gg", "http://ggzyjy.rizhao.gov.cn:8607/rzwz/ShowInfo/MoreJyxxList.aspx?categoryNum=071002003&Paging=1",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_gqita_zhong_liu_gg", "http://ggzyjy.rizhao.gov.cn:8607/rzwz/ShowInfo/MoreJyxxList.aspx?categoryNum=071002004&Paging=1",
         ["name", "ggstart_time", "href","info"],f1,f2],

    ]



def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省日照市",**args)
    est_html(conp,f=f3,**args)


# 网址更新：http://ggzyjy.rizhao.gov.cn:8607/rzwz/
# 更新日期：2019/6/27
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","rizhao"])
    #

    # for d in data:
    #     url = d[1]
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #     df = f1(driver, 3)
    #     print(df.values)
