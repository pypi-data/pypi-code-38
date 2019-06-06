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


from zhulong.util.etl import est_tbs, est_meta, est_html, est_gg


# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='dexing'

def f1(driver,num):

    locator = (By.XPATH, '//*[@id="content"]/div[3]/div[2]/ul[1]/li[1]/a/span')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url

    cnum = re.findall('-(\d+?)\.html', url)[0]

    main_url = url.rsplit('-', maxsplit=1)[0]

    if int(cnum) != num:
        main_url=main_url+'-'+str(num)+'.html'
        val = driver.find_element_by_xpath('//*[@id="content"]/div[3]/div[2]/ul[1]/li[1]/a').get_attribute('href')[-30:-5]

        driver.get(main_url)

        locator = (By.XPATH, '//*[@id="content"]/div[3]/div[2]/ul[1]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data=[]
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='lb_ul')
    lis = div.find_all('li')
    for li in lis:
        href = li.a['href']
        name = li.a.span.get_text()
        ggstart_time = li.find('span', class_='sp2').get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.dxs.gov.cn'+href

        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):

    locator = (By.XPATH, '//*[@id="content"]/div[3]/div[2]/ul[1]/li[1]/a/span')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//*[@id="content"]/div[3]/div[3]/div[2]/a[4]').get_attribute('href')

    total = re.findall('-(\d+?)\.html', page)[0]
    total=int(total)
    driver.quit()
    return total

def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="printArea"][string-length()>10] | //div[@class="ewb-detail-box"][string-length()>10]')

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
    div = soup.find('div',class_='conTxt')
    if not div:
        div = soup.find('div',class_="ewb-detail-box")

    return div

data=[
    #
    ["zfcg_gqita_zhao_zhong_gg","http://www.dxs.gov.cn/news-list-zfcg-1.html",["name","ggstart_time","href",'info'],f1,f2],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="江西省德兴市",**args)
    est_html(conp,f=f3,**args)



if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","jiangxi","dexing"]

    work(conp=conp,headless=False,num=1)