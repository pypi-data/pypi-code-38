import time

import pandas as pd
import re

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from zhulong2.util.etl import est_meta, est_html

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='hunan_xiangtan'


def f1(driver,num):
    locator = (By.XPATH, '(//td[@class="text"])[3]/a[2]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url

    cnum = url.rsplit('=', maxsplit=1)[1]
    main_url = url.rsplit('=', maxsplit=1)[0]

    if int(cnum) != num:
        val = driver.find_element_by_xpath('(//td[@class="text"])[3]/a[2]').get_attribute('href')[-10:]

        url_ = main_url + '=%d' % num

        driver.get(url_)

        locator = (By.XPATH, '(//td[@class="text"])[3]/a[2][not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    tds = soup.find_all('td', class_='text')

    for i in range(2, len(tds) - 1, 2):
        href = tds[i].find_all('a')[1]['href']
        name = tds[i].find_all('a')[1].get_text()
        ggstart_time = tds[i + 1].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://xtcg.cz.xiangtan.gov.cn/' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df=pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):
    locator = (By.XPATH, '(//td[@class="text"])[3]/a[2]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('(//td[@class="text"])[last()]/a[@title="尾页"]').get_attribute('href')

    total = re.findall('page=(\d+)', total)[0]
    total = int(total)

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//tr[@id="textflag"][string-length()>10]')

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
    div = soup.find('tr', id="textflag")
    if div == None:
        raise ValueError('return div is None')

    return div



data=[
    ["zfcg_zhaobiao_gg","http://xtcg.cz.xiangtan.gov.cn/Main.asp?Tid=14&page=1",["name", "ggstart_time","href",'info'],f1,f2],
    ["zfcg_zhongbiaohx_gg","http://xtcg.cz.xiangtan.gov.cn/Main.asp?Tid=16&page=1",["name", "ggstart_time","href",'info'],f1,f2],
    ["zfcg_zhongbiao_gg","http://xtcg.cz.xiangtan.gov.cn/Main.asp?Tid=17&page=1",["name", "ggstart_time","href",'info'],f1,f2],
    ["zfcg_gqita_da_bian_gg","http://xtcg.cz.xiangtan.gov.cn/Main.asp?Tid=15&page=1",["name", "ggstart_time","href",'info'],f1,f2],
    ["zfcg_liubiao_gg","http://xtcg.cz.xiangtan.gov.cn/Main.asp?Tid=80&page=1",["name", "ggstart_time","href",'info'],f1,f2],
]

def work(conp,**args):
    est_meta(conp,data=data,diqu="湖南省湘潭市",**args)
    est_html(conp,f=f3,**args)



if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","lch","hunan_xiangtan"]

    work(conp=conp,pageloadtimeout=60,pageloadstrategy='none',headless=False,num=1,cdc_total=1)