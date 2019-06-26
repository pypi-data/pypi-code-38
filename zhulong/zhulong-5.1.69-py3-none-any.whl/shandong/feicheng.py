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
from zhulong.util.etl import est_tbs,est_meta,est_html


_name_='feicheng'

def f1(driver, num):
    locator = (By.XPATH, "(//a[@class='WebList_sub'])[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    # print(url)
    if "Paging=" not in url:
        cnum = 1
    else:
        cnum = int(re.findall("Paging=(\d+)", url)[0])
    if num != int(cnum):
        if "Paging=" not in url:
            s = "?Paging=%d" % (num) if num > 1 else "?Paging=1"
            url += s
        if num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        val = driver.find_element_by_xpath("(//a[@class='WebList_sub'])[1]").get_attribute('href')[-35:]
        driver.get(url)
        locator = (By.XPATH, "(//a[@class='WebList_sub'])[1][not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("div", id='right_table')
    tb = div.find("table", attrs={"width":"98%", "align":"center"})
    trs = tb.find_all("tr", attrs={'height':'30'})
    data = []
    for li in trs:
        a = li.find("a")
        title = a['title']
        link = "http://www.taggzyjy.com.cn" + a["href"]
        span = li.find("td", width='80').text.strip()
        date = re.findall(r'\[(.*)\]', span)[0]
        tmp = [title.strip(), date, link]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"]=None
    return df



def f2(driver):
    locator = (By.XPATH, '//td[@class="huifont"]')
    page_all = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    page = re.findall(r'/(\d+)', page_all)[0]
    driver.quit()
    return int(page)



def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH,"//td[@width='998'][string-length()>30]")
    WebDriverWait(driver,15).until(EC.presence_of_all_elements_located(locator))
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
    div=soup.find('div',class_='inner')
    td=div.find("td",width="998")
    return td

data=[
        ["gcjs_zhaobiao_gg","http://www.taggzyjy.com.cn/Web_FeiCheng/jyxx/075001/075001001/",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_biangeng_gg","http://www.taggzyjy.com.cn/Web_FeiCheng/jyxx/075001/075001003/",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_zhongbiaohx_gg","http://www.taggzyjy.com.cn/Web_FeiCheng/jyxx/075001/075001002/",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_zhongbiao_gg", "http://www.taggzyjy.com.cn/Web_FeiCheng/jyxx/075001/075001004/",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["zfcg_yucai_gg", "http://www.taggzyjy.com.cn/Web_FeiCheng/jyxx/075002/075002004/",
         ["name", "ggstart_time", "href", "info"], f1, f2],

       ["zfcg_zhaobiao_gg", "http://www.taggzyjy.com.cn/Web_FeiCheng/jyxx/075002/075002001/",
        ["name", "ggstart_time", "href","info"],f1,f2],

       ["zfcg_biangeng_gg", "http://www.taggzyjy.com.cn/Web_FeiCheng/jyxx/075002/075002003/",
        ["name", "ggstart_time", "href","info"],f1,f2],

       ["zfcg_zhongbiao_gg", "http://www.taggzyjy.com.cn/Web_FeiCheng/jyxx/075002/075002002/",
        ["name", "ggstart_time", "href","info"],f1,f2],
]


def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省肥城市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","feicheng"])

