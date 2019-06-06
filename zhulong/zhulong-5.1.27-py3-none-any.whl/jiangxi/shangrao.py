import time

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

from zhulong.util.etl import est_tbs,est_meta,est_html,est_gg

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='shangrao'


def f1(driver,num):
    locator = (By.XPATH, "//table[@width='650']//tr[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url=driver.current_url
    cnum=re.findall('page=(\d+)',url)[0]

    if int(cnum) != num:

        val = driver.find_element_by_xpath(
            "//table[@width='650']//tr[1]//a").get_attribute('href')[-15:-5]

        main_url = url.rsplit('=',maxsplit=1)[0]
        main_url=main_url+'='+str(num)
        driver.get(main_url)

        locator = (By.XPATH,
                   "//table[@width='650']//tr[1]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data=[]
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find_all('tr', height=27)
    for tr in trs:
        tds = tr.find_all('td')
        href = tds[0].a['href']
        name = tds[0].a.get_text()
        ggstart_time = tds[1].get_text()

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):

    locator = (By.XPATH, '//table[@width="650"]//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath("//ul[@class='pagination']/li[last()-1]").text
    total=int(total)
    driver.quit()
    return total

def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '(//table[@width="900"])[1]')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5: break

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('table',width="900").find('table',width="900")
    return div

data=[

    ["gcjs_gqita_zhao_bian_gg","http://www.srjsgc.cn/1.html?page=1",["name","ggstart_time","href",'info'],f1,f2],
    ["gcjs_gqita_zhong_liu_gg","http://www.srjsgc.cn/2.html?page=1",["name","ggstart_time","href",'info'],f1,f2],
]


def work(conp,**args):
    est_meta(conp,data=data,diqu="江西省上饶市",**args)
    est_html(conp,f=f3,**args)



if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","jiangxi","shangrao"]

    work(conp=conp,headless=False,num=1)