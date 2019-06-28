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

_name_='guyuan'

def f1(driver,num):
    try:
        locator = (By.XPATH, '//div[@id="showacticle"]//table//tr[2]//a')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    except:
        if '404' in driver.title:
            return
        else:
            raise TimeoutError
    url = driver.current_url

    cnum = re.findall('/(\d+)\.html', url)[0]

    if int(cnum) != num:
        main_url = url.rsplit('/', maxsplit=1)[0]
        val = driver.find_element_by_xpath('//div[@id="showacticle"]//table//tr[2]//a').get_attribute('href')[-30:-5]

        url = main_url + '/' + str(num) + '.html'

        driver.get(url)

        locator = (By.XPATH, '//div[@id="showacticle"]//table//tr[2]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', id='showacticle').find('div').find('table')
    lis = div.find_all('tr')

    for i in range(1, len(lis) - 1):
        tr = lis[i]
        href = tr.td.a['href']
        name = tr.td.a.get_text().strip()

        ggstart_time = tr.find_all('td')[1].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.gysggzyjy.cn' + href

        tmp = [name, href, ggstart_time]
        data.append(tmp)

    df=pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, '//div[@id="showacticle"]//table//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//span[@id="index"]').text
    page = re.findall('/(\d+)', page)[0]
    total=int(page)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@id="showacticle"][string-length()>10]')

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
    div = soup.find('div', id="showacticle")

    return div

data=[

    ##包含:招标,变更
    ["zfcg_gqita_zhao_bian_gg","http://www.gysggzyjy.cn/gysggzyjy/002/002001/1.html",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["gcjs_gqita_zhao_bian_gg","http://www.gysggzyjy.cn/gysggzyjy/002/002002/1.html",[ "name", "href", "ggstart_time","info"],f1,f2],

    ##包含:中标,流标
    ["zfcg_gqita_zhong_liu_gg","http://www.gysggzyjy.cn/gysggzyjy/003/003001/1.html",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["gcjs_gqita_zhong_liu_gg","http://www.gysggzyjy.cn/gysggzyjy/003/003002/1.html",[ "name", "href", "ggstart_time","info"],f1,f2],


]

def work(conp,**args):
    est_meta(conp,data=data,diqu="宁夏回族自治区固原市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","ningxia","guyuan"]

    work(conp=conp)