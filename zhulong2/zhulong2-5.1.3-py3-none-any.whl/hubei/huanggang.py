import json
import time

import pandas as pd
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from zhulong2.util.etl import est_meta, est_html

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='hubei_huanggang'


def f1(driver,num):
    locator = (By.XPATH, '//tr[@class="tr_main_value_odd"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum=driver.find_element_by_xpath('//table[@class="tb_title"]/tbody/tr/td[1]').text
    cnum=int(re.findall('第(\d+)页',cnum)[0])

    if num != cnum:

        val = driver.find_element_by_xpath('//tr[@class="tr_main_value_odd"][1]//a').get_attribute('href')[-30:-5]

        driver.execute_script("Javascript:funGoPage('/module/xxgk/search.jsp',%d);"%num)

        locator = (By.XPATH, '//tr[@class="tr_main_value_odd"][1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    ht = driver.page_source
    soup = BeautifulSoup(ht, 'html.parser')
    trs = soup.find_all('tr', class_=re.compile('tr_main_value_(odd|even)'))

    data = []
    for li in trs:
        tds=li.find_all('td')
        name = tds[0].a['title']
        href = tds[0].a['href']
        fbdw = tds[1].get_text()
        ggstart_time = tds[2].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.hg.gov.cn' + href
        info={'dw':fbdw}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]
        data.append(tmp)
    df=pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//tr[@class="tr_main_value_odd"][1]/td[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//table[@class="tb_title"]/tbody/tr/td[1]').text
    total = re.findall('记录.*共(.+?)页', total)[0].strip()
    total=int(total)

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="info-container"]/div[2][string-length()>10]')

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
    div = soup.find('div',class_="info-container").find_all('div',recursive=False)[1]
    return div



data=[

    ["zfcg_zhaobiao_gg","http://www.hg.gov.cn/col/col13664/index.html?number=A00010A00001",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_zhongbiao_gg","http://www.hg.gov.cn/col/col13664/index.html?number=A00010A00002",["name","ggstart_time","href",'info'],f1,f2],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="湖北省黄冈市",**args)
    est_html(conp,f=f3,**args)



if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","lch","hubei_huanggang"]

    work(conp=conp)