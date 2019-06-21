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
from zhulong.util.etl import est_html,est_meta


_name_="tengzhou"

def f1(driver, num):
    locator = (By.XPATH, '(//td[@class="line2"]//a)[1]')
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-15:]
    url = driver.current_url
    locator = (By.XPATH, "(//td[@class='f15']/span)[1]")
    page_all = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall(r'(\d+)/', page_all)[0]
    if num != int(cnum):
        if num == 1:
            url = re.sub("_[0-9]*", "_1", url)
        else:
            s = "_%d" % (num) if num > 1 else "_1"
            url = re.sub("_[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, "(//td[@class='line2']//a)[1][not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    ul = soup.find("td", class_="nr")
    trs = ul.find_all("td", class_="line2")
    data = []
    for li in trs:
        a = li.find("a")
        try:
            title = a["title"]
        except:
            title = a.text.strip()
        link = "http://www.tzccgp.gov.cn" + a["href"]
        try:
            span1 = li.find_all("td")[-1].text
        except:
            span1 = "-"
        tmp = [title, span1.strip(), link]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"]=None
    return df


def f2(driver):
    locator = (By.XPATH, '(//td[@class="line2"]//a)[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "(//td[@class='f15']/span)[1]")
    page_all = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    page = re.findall(r'/(\d+)', page_all)[0]
    driver.quit()
    return int(page)


def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH,"//td[@class='nr'][string-length()>30]")
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
    div=soup.find('td',class_='nr')
    return div



data = [
        ["jqita_zhaobiao_gg","http://www.tzccgp.gov.cn/list/?3_1.html",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["jqita_zhongbiao_gg", "http://www.tzccgp.gov.cn/list/?4_1.html",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["jqita_yanshou_gg", "http://www.tzccgp.gov.cn/list/?113_1.html",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["jqita_hetong_gg", "http://www.tzccgp.gov.cn/list/?112_1.html",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["jqita_yucai_gg", "http://www.tzccgp.gov.cn/list/?111_1.html",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["jqita_gqita_bian_liu_gg", "http://www.tzccgp.gov.cn/list/?109_1.html",
         ["name", "ggstart_time", "href","info"],f1,f2],

    ]


def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省滕州市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","tengzhou"])

