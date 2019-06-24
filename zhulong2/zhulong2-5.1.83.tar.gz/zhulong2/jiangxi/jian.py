import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from zhulong2.util.etl import est_tbs, est_meta, est_html, est_gg


# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_='jiangxi_jian'

def f1(driver,num):
    locator = (By.XPATH, '//div[@class="publicList bgwhite pagingList"]//li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum=int(driver.find_element_by_xpath("//a[@class='curpage']").text)

    if num != cnum:

        val = driver.find_element_by_xpath('//div[@class="publicList bgwhite pagingList"]//li[1]/a').get_attribute('href').rsplit(
            '/', maxsplit=1)[1]

        driver.execute_script("javascript:post('http://218.64.81.21:8082/search/search.jsp',{pag:'',keyword:'',search:'',column:'%s',starttime:'',endtime:''},%d);"%(column_mark,(num-1)*20))

        locator = (By.XPATH, '//div[@class="publicList bgwhite pagingList"]//li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    ht = driver.page_source
    soup = BeautifulSoup(ht, 'html.parser')
    div = soup.find('div', class_="publicList bgwhite pagingList")
    uls = div.find_all('li')

    data = []
    for li in uls:
        name = li.a.get_text()
        href = li.a['href']
        ggstart_time = li.span.get_text()
        tmp = [name, ggstart_time, href]
        print(tmp)
        data.append(tmp)

    df=pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="publicList bgwhite pagingList"]//li[1]/a')
    WebDriverWait(driver, 5).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath('//div[@id="div_page"]/a[last()]').get_attribute('href')
    total = re.findall('},(\d+)\)', total)[0]
    total=int(total)//20+1
    driver.quit()
    return total

def chang_type(f,num):
    def inner(*args):
        driver=args[0]
        locator = (By.XPATH, '//div[@class="publicList bgwhite pagingList"]//li[1]/a')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        column_list=['采购公告','变更公告','答疑澄清','结果公示','单一来源公示']

        global column_mark
        column_mark=column_list[num-1]

        url=driver.current_url
        if 'www.jazfcg.com.cn' in url:
            val=driver.find_element_by_xpath('//div[@id="div_page"]/a[last()]').get_attribute('href')
            se=Select(driver.find_element_by_xpath('//select[@id="searchColumn"]'))
            se.select_by_index(num)
            time.sleep(0.1)
            driver.find_element_by_xpath('//div[@class="fl intsub searchBtn"]').click()
            locator=(By.XPATH,'//div[@id="div_page"]/a[last()][not(contains(@href,"%s"))]'%val)
            WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
            time.sleep(10)
        return f(*args)
    return inner




def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="textmid"][string-length()>10]')
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
    div = soup.find('div',class_="textshow")
    return div



data=[

    ["zfcg_zhaobiao_gg","http://www.jazfcg.com.cn/cgxx/cggg/index.html",["name","ggstart_time","href",'info'],chang_type(f1,1),chang_type(f2,1)],
    ["zfcg_biangeng_gg","http://www.jazfcg.com.cn/cgxx/bggg/index.html",["name","ggstart_time","href",'info'],chang_type(f1,2),chang_type(f2,2)],
    ["zfcg_gqita_da_bian_gg","http://www.jazfcg.com.cn/cgxx/dycq/index.html",["name","ggstart_time","href",'info'],chang_type(f1,3),chang_type(f2,3)],
    ["zfcg_zhongbiao_gg","http://www.jazfcg.com.cn/cgxx/jggs/index.html",["name","ggstart_time","href",'info'],chang_type(f1,4),chang_type(f2,4)],
    ["zfcg_zhaobiao_danyilaiyuan_gg","http://www.jazfcg.com.cn/cgxx/dylygs/index.html",["name","ggstart_time","href",'info'],chang_type(f1,5),chang_type(f2,5)],
    

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="江西省吉安市",**args)
    est_html(conp,f=f3,**args)



if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","lch","jiangxi_jian"]

    work(conp=conp,headless=False,num=1)