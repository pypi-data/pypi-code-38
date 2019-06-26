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

_name_='leling'


def f1(driver, num):
    locator = (By.XPATH, "(//a[@class='ewb-list-name'])[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url

    locator = (By.XPATH, '//td[@class="huifont"]')
    page_all = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall(r'(\d+)/', page_all)[0]

    if num != int(cnum):
        if 'Paging' not in url:
            s = "?Paging=%d" % (num) if num > 1 else "?Paging=1"
            url += s
        elif num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
            # print(cnum)
        val = driver.find_element_by_xpath("(//a[@class='ewb-list-name'])[1]").get_attribute('href')[-40:]
        driver.get(url)
        locator = (By.XPATH, "(//a[@class='ewb-list-name'])[1][not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tb = soup.find("table", cellspacing="3", align="center")
    trs = tb.find_all("tr")
    data = []
    for li in trs:
        a = li.find("a")
        title = a['title']
        link = "http://ggzyjy.dezhou.gov.cn" + a["href"]
        span = li.find_all("font")[-1]
        tmp = [title.strip(), span.text.strip(), link]
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
    time.sleep(1)
    locator=(By.XPATH,"//div[@class='ewb-right-info'][string-length()>15] | //div[contains(@id,'menutab')][@style=''][string-length()>15]")
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
    if 'ewb-right-info' in page:
        div=soup.find('div',class_='ewb-right-info')
    else:
        div=soup.find("div",id=re.compile("menutab.*"),style='')
    return div


data = [
        ["gcjs_zhaobiao_gg",
         "http://ggzyjy.dezhou.gov.cn/ll/xmxx/004001/004001001/004001001002/?Paging=1",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_biangeng_gg",
         "http://ggzyjy.dezhou.gov.cn/ll/xmxx/004001/004001002/004001002002/?Paging=1",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_gqita_zhong_liu_gg",
         "http://ggzyjy.dezhou.gov.cn/ll/xmxx/004001/004001003/004001003002/?Paging=1",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_yucai_gg",
         "http://ggzyjy.dezhou.gov.cn/ll/xmxx/004001/004001005/004001005002/?Paging=1",
         ["name", "ggstart_time", "href","info"],f1,f2],


       ["zfcg_zhaobiao_gg",
        "http://ggzyjy.dezhou.gov.cn/ll/xmxx/004002/004002001/004002001002/?Paging=1",
        ["name", "ggstart_time", "href","info"],f1,f2],

       ["zfcg_biangeng_gg",
        "http://ggzyjy.dezhou.gov.cn/ll/xmxx/004002/004002002/004002002002/?Paging=1",
        ["name", "ggstart_time", "href","info"],f1,f2],

       ["zfcg_gqita_zhong_liu_gg",
        "http://ggzyjy.dezhou.gov.cn/ll/xmxx/004002/004002003/004002003002/?Paging=1",
        ["name", "ggstart_time", "href","info"],f1,f2],

       ["zfcg_yucai_gg",
        "http://ggzyjy.dezhou.gov.cn/ll/xmxx/004002/004002005/004002005002/?Paging=1",
        ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_hetong_gg",
         "http://ggzyjy.dezhou.gov.cn/ll/xmxx/004002/004002006/004002006002/?Paging=1",
         ["name", "ggstart_time", "href","info"],f1,f2],

    ]

def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省乐陵市",num=5)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","leling"])

# 修改时间：2019/5/27
# 域名修改：http://ggzyjy.dezhou.gov.cn/ll/