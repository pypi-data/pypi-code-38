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


from zhulong.util.etl import est_tbs, est_meta, est_html, est_gg, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='fengcheng'

def f1(driver,num):
    url=driver.current_url
    mark = re.findall('ClassID=(\d+)&', url)[0]
    if mark=='19' or mark=='25':
        locator = (By.XPATH, "//td[@class='main_tdbg_575']//tr[1]//a[2]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    else:
        locator=(By.XPATH,"//td[@class='main_tdbg_575']/a[2]")
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    cnum=int(re.findall("page=([0-9]{1,})",url)[0])

    if num!=cnum:

        s="page=%d"%(num)
        url=re.sub("page=[0-9]+",s,url)
        # print(url)
        if mark=='19' or mark=='25':
            val=driver.find_element_by_xpath("//td[@class='main_tdbg_575']//tr[1]//a[2]").get_attribute(
            "href")[- 30:]

            driver.get(url)
            locator=(By.XPATH,"//td[@class='main_tdbg_575']//tr[1]//a[2][not(contains(@href,'%s'))]"%val)
            WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
        else:
            val = driver.find_element_by_xpath("//td[@class='main_tdbg_575']/a[2]").get_attribute(
            "href")[- 30:]

            driver.get(url)
            locator = (By.XPATH, "//td[@class='main_tdbg_575']/a[2][not(contains(@href,'%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find('td', class_='main_tdbg_575')
    tds = tables.find_all('a', attrs={'title': not None})
    data=[]
    for td in tds:

        href = td['href']
        href = 'http://www.fcgzj.gov.cn' + href
        content = td['title']
        name = re.findall('文章标题：(.+)', content)[0]
        ggstart_time = re.findall('更新时间：(\d+-\d+-\d+)', content)[0]

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df=pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):
    url = driver.current_url
    mark=re.findall('ClassID=(\d+)&',url)[0]
    if mark=='19' or mark=='25':
        locator = (By.XPATH, "//td[@class='main_tdbg_575']//tr[1]//a[2]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    else:
        locator = (By.XPATH, "(//td[@class='main_tdbg_575']/a[2])")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        page = driver.find_element_by_xpath("//div[@class='show_page']/a[last()]").get_attribute('href')
        total = re.findall(r'page=(\d+)', page)[0]
        total=int(total)
    except:
        total=1
    return total

def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '(//table[@class="bor1"])[2][string-length()>10]')

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
    div = soup.find('td',id="fontzoom")

    return div


data=[
    #包含招标,流标
    ["gcjs_gqita_zhao_bian_gg","http://www.fcgzj.gov.cn/Article/ShowClass.asp?ClassID=14&page=1",["name","ggstart_time","href",'info'],f1,f2],
    ["gcjs_gqita_zhong_liu_gg","http://www.fcgzj.gov.cn/Article/ShowClass.asp?ClassID=20&page=1",["name","ggstart_time","href",'info'],f1,f2],


    ##包含招标,流标
    ["zfcg_zhaobiao_gg","http://www.fcgzj.gov.cn/Article/ShowClass.asp?ClassID=15&page=1",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_gqita_zhong_liu_gg","http://www.fcgzj.gov.cn/Article/ShowClass.asp?ClassID=21&page=1",["name","ggstart_time","href",'info'],f1,f2],

    #乡镇交易
    ["jqita_zhaobiao_gg","http://www.fcgzj.gov.cn/Article/ShowClass.asp?ClassID=19&page=1",["name","ggstart_time","href",'info'],add_info(f1,{'tag':"乡镇交易"}),f2],
    ["jqita_gqita_zhong_liu_gg","http://www.fcgzj.gov.cn/Article/ShowClass.asp?ClassID=25&page=1",["name","ggstart_time","href",'info'],add_info(f1,{'tag':"乡镇交易"}),f2],
    #
    ["jqita_zhaobiao_gg","http://www.fcgzj.gov.cn/Article/ShowClass.asp?ClassID=18&page=1",["name","ggstart_time","href",'info'],f1,f2],
    ["jqita_gqita_zhong_liu_gg","http://www.fcgzj.gov.cn/Article/ShowClass.asp?ClassID=24&page=1",["name","ggstart_time","href",'info'],f1,f2],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="江西省丰城市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","jiangxi","fengcheng"]

    work(conp=conp,headless=False,num=1)