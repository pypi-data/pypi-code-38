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


_name_='xining'

def f1(driver,num):

    locator = (By.XPATH, '//div[@class="right-span-content"]/table/tbody/tr[1]/td[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url

    cnum = re.findall('Paging=(\d+)', url)[0]

    if int(cnum) != num:
        main_url = url.rsplit('=', maxsplit=1)[0]
        val = driver.find_element_by_xpath('//div[@class="right-span-content"]/table/tbody/tr[1]/td[2]/a').get_attribute('href')[-30:]

        url = main_url + '=' + str(num)
        driver.get(url)
        try:
            locator = (By.XPATH, '//div[@class="right-span-content"]/table/tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (
            By.XPATH, '//div[@class="right-span-content"]/table/tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='right-span-content').find('table')
    lis = div.find_all('tr')

    for li in lis:
        tds = li.find_all('td')
        href = tds[1].a['href']
        name = tds[1].a.get_text()
        ggstart_time = tds[2].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.xnggzy.org.cn' + href

        tmp = [name, href, ggstart_time]
        data.append(tmp)

    df=pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, '//div[@class="right-span-content"]/table/tbody/tr[1]/td[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    content=driver.page_source
    page=re.findall('<td class="huifont">\d/(\d+?)</td>',content)[0]

    total=int(page)
    driver.quit()
    return total

def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//table[@id="tblInfo"][string-length()>10]')

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

    div = soup.find('table', id="tblInfo")

    return div



data=[

    ["gcjs_zhaobiao_diqu1_gg","http://www.xnggzy.org.cn/xnweb/jsgc/012001/012001001/?Paging=1",[ "name", "href", "ggstart_time","info"],add_info(f1, {"diqu": '市本级'}),f2],
    ["gcjs_biangeng_diqu1_gg","http://www.xnggzy.org.cn/xnweb/jsgc/012002/012002001/?Paging=1",[ "name", "href", "ggstart_time","info"],add_info(f1, {"diqu": '市本级'}),f2],
    ["gcjs_zhongbiao_diqu1_gg","http://www.xnggzy.org.cn/xnweb/jsgc/012003/012003001/?Paging=1",[ "name", "href", "ggstart_time","info"],add_info(f1, {"diqu": '市本级'}),f2],
    ["gcjs_liubiao_diqu1_gg","http://www.xnggzy.org.cn/xnweb/jsgc/012004/012004001/?Paging=1",[ "name", "href", "ggstart_time","info"],add_info(f1, {"diqu": '市本级'}),f2],

    ["zfcg_zhaobiao_diqu1_gg","http://www.xnggzy.org.cn/xnweb/zfcg/013001/013001001/?Paging=1",[ "name", "href", "ggstart_time","info"],add_info(f1, {"diqu": '市本级'}),f2],
    ["zfcg_biangen_diqu1_gg","http://www.xnggzy.org.cn/xnweb/zfcg/013002/013002001/?Paging=1",[ "name", "href", "ggstart_time","info"],add_info(f1, {"diqu": '市本级'}),f2],
    ["zfcg_zhongbiao_diqu1_gg","http://www.xnggzy.org.cn/xnweb/zfcg/013003/013003001/?Paging=1",[ "name", "href", "ggstart_time","info"],add_info(f1, {"diqu": '市本级'}),f2],
    ["zfcg_liubiao_diqu1_gg","http://www.xnggzy.org.cn/xnweb/zfcg/013004/013004001/?Paging=1",[ "name", "href", "ggstart_time","info"],add_info(f1, {"diqu": '市本级'}),f2],


    ["gcjs_zhaobiao_diqu2_gg","http://www.xnggzy.org.cn/xnweb/jsgc/012001/012001002/?Paging=1",[ "name", "href", "ggstart_time","info"],add_info(f1, {"diqu": '区县'}),f2],
    ["gcjs_biangeng_diqu2_gg","http://www.xnggzy.org.cn/xnweb/jsgc/012002/012002002/?Paging=1",[ "name", "href", "ggstart_time","info"],add_info(f1, {"diqu": '区县'}),f2],
    ["gcjs_zhongbiao_diqu2_gg","http://www.xnggzy.org.cn/xnweb/jsgc/012003/012003002/?Paging=1",[ "name", "href", "ggstart_time","info"],add_info(f1, {"diqu": '区县'}),f2],
    ["gcjs_liubiao_diqu2_gg","http://www.xnggzy.org.cn/xnweb/jsgc/012004/012004002/?Paging=1",[ "name", "href", "ggstart_time","info"],add_info(f1, {"diqu": '区县'}),f2],

    ["zfcg_zhaobiao_diqu2_gg","http://www.xnggzy.org.cn/xnweb/zfcg/013001/013001002/?Paging=1",[ "name", "href", "ggstart_time","info"],add_info(f1, {"diqu": '区县'}),f2],
    ["zfcg_biangeng_diqu2_gg","http://www.xnggzy.org.cn/xnweb/zfcg/013002/013002002/?Paging=1",[ "name", "href", "ggstart_time","info"],add_info(f1, {"diqu": '区县'}),f2],
    ["zfcg_zhongbiao_diqu2_gg","http://www.xnggzy.org.cn/xnweb/zfcg/013003/013003002/?Paging=1",[ "name", "href", "ggstart_time","info"],add_info(f1, {"diqu": '区县'}),f2],
    ["zfcg_liubiao_diqu2_gg","http://www.xnggzy.org.cn/xnweb/zfcg/013004/013004002/?Paging=1",[ "name", "href", "ggstart_time","info"],add_info(f1, {"diqu": '区县'}),f2],

]


##域名变更 http://www.xnggzy.org.cn
##变更时间 2019-5-16


def work(conp,**args):
    est_meta(conp,data=data,diqu="青海省西宁市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","qinghai","xining"]


    work(conp=conp,num=10,pageloadstrategy='none')