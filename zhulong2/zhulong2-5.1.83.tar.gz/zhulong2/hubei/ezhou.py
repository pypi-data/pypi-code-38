import json
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


from zhulong2.util.etl import est_tbs, est_meta, est_html, est_gg, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='hubei_ezhou'


def f1(driver,num):

    locator = (By.XPATH, '//div[@class="listtext_listpage"]/table[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        cnum = driver.find_element_by_xpath('//div[@id="AspNetPager1"]/span').text
    except:
        cnum=1

    cnum = int(cnum)

    if num != cnum:

        val = \
        driver.find_element_by_xpath('//div[@class="listtext_listpage"]/table[2]//a').get_attribute('href').rsplit(
            '?', maxsplit=1)[1]

        driver.execute_script("javascript:__doPostBack('AspNetPager1','{num}')".format(num=num))

        locator = (By.XPATH, '//div[@class="listtext_listpage"]/table[2]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    ht = driver.page_source
    soup = BeautifulSoup(ht, 'html.parser')
    div = soup.find('div', class_="listtext_listpage")
    tables = div.find_all('table', recursive=False)

    data = []
    for i in range(1, len(tables)):
        table = tables[i]
        tds = table.find_all('td')
        name = tds[0].a['title']
        href = tds[0].a['href']
        ggstart_time = tds[1].get_text()
        gkdw=tds[-1].get_text().strip()
        if 'http' in href:
            href = href
        else:
            href = 'http://www.ezhou.gov.cn/' + href
        info={'gkdw':gkdw}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]

        data.append(tmp)
    df=pd.DataFrame(data=data)

    return df


def f2(driver):
    time.sleep(1)
    locator = (By.XPATH, '//div[@class="listtext_listpage"]/table[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        total = driver.find_element_by_xpath('//div[@id="AspNetPager1"]/a[last()]').get_attribute('href')
        total = re.findall("page=(\d+)", total)[0].strip()
        total=int(total)
    except:
        total=1

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    time.sleep(0.5)
    driver.refresh()
    locator = (By.XPATH, '//div[@class="main"][string-length()>4500]')

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
    div = soup.find('div', class_="main")

    return div


def chang(f,num1,num2):
    def wrap(*arg):
        driver=arg[0]
        driver.refresh()
        locator = (By.XPATH, '//div[@class="listtext_listpage"]/table[2]//a')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        ctext=driver.find_element_by_xpath('//div[@class="f_mainlr_rj2"]').text.strip()
        driver.find_element_by_xpath('(//div[@id="TreeView1"]/div[2]/div[{num1}]/table[{num2}]//a)[2]'.format(num1=num1,num2=num2)).click()

        locator = (By.XPATH, '//div[@class="f_mainlr_rj2"][not(contains(text,"%s"))]' % ctext)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        return f(*arg)

    return wrap



data=[

    ["zfcg_zhaobiao_gg","http://www.ezhou.gov.cn/dgiMain.aspx?iid=70",["name","ggstart_time","href",'info'],chang(f1,5,1),chang(f2,5,1)],
    ["zfcg_zhongbiaohx_gg","http://www.ezhou.gov.cn/dgiMain.aspx?iid=70",["name","ggstart_time","href",'info'],chang(f1,5,2),chang(f2,5,2)],
    ["zfcg_gqita_mulu_gg","http://www.ezhou.gov.cn/dgiMain.aspx?iid=74",["name","ggstart_time","href",'info'],add_info(chang(f1,6,1),{"jylx":"采购目录"}),chang(f2,6,1)],
    ["zfcg_zhaobiao_xunjia_gg","http://www.ezhou.gov.cn/dgiMain.aspx?iid=74",["name","ggstart_time","href",'info'],add_info(chang(f1,6,2),{"jylx":"询价"}),chang(f2,6,2)],
    ["zfcg_zhongbiao_gg","http://www.ezhou.gov.cn/dgiMain.aspx?iid=74",["name","ggstart_time","href",'info'],chang(f1,6,3),chang(f2,6,3)],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="湖北省鄂州市",**args)
    est_html(conp,f=f3,**args)


# 该网站需修改headless=False,才能获取到内容
if __name__=='__main__':
    conp=["postgres","since2015","192.168.3.171","lch","hubei_ezhou"]
    work(conp=conp,headless=False,num=1)

    # driver=webdriver.Chrome()
    # url='http://www.ezhou.gov.cn/dgiShow.aspx?iid=13501'
    # f3(driver,url=url)