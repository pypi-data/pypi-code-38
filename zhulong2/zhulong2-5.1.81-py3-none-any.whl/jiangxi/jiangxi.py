import json
import time

import pandas as pd
import re

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from zhulong2.util.etl import est_meta, est_html, add_info, est_meta_large

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='jiangxi_jiangxi'


def f1(driver,num):
    try:
        locator = (By.XPATH, '//div[@id="gengerlist"]/div[1]//li[1]/a')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    except:
        if '404' in driver.title:
            return
        else:
            raise TimeoutError

    url = driver.current_url
    cnum = int(re.findall("/(\d+)\.html", url)[0])

    if num != cnum:
        s = "/%d.html" % (num)
        url = re.sub("/(\d+)\.html", s, url)
        val = driver.find_element_by_xpath('//div[@id="gengerlist"]/div[1]//li[1]/a').get_attribute('href').rsplit(
            '/', maxsplit=1)[1]

        driver.get(url)
        try:
            locator = (By.XPATH, "//div[@id='gengerlist']/div[1]//li[1]/a[not(contains(@href,'%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            if '404' in driver.title:
                return
            else:
                raise TimeoutError
    ht = driver.page_source
    soup = BeautifulSoup(ht, 'html.parser')
    uls = soup.find('div', class_="ewb-infolist")
    lis = uls.find_all('li')
    data = []
    for li in lis:
        name = li.a.get_text()
        href = li.a['href']
        href = 'http://www.ccgp-jiangxi.gov.cn' + href
        ggstart_time = li.span.get_text()
        diqu = re.findall('\[(.+?[县区级市])\]', name)
        if diqu:
            diqu = diqu[0]
            info = {'diqu': diqu}
            info = json.dumps(info, ensure_ascii=False)
        else:
            info=None

        tmp = [name, ggstart_time, href, info]

        data.append(tmp)
    df=pd.DataFrame(data=data)

    return df


def f2(driver):

    locator = (By.XPATH, '//*[@id="gengerlist"]/div[1]/ul/li[1]/a')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    total=int(driver.find_element_by_xpath('//*[@id="index"]').text.split('/')[1])

    driver.quit()
    return total

def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="article-info"][string-length()>10]')

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
    div = soup.find('div',class_="ewb-detail-box")
    return div



data=[

    ["zfcg_zhaobiao_gg","http://www.ccgp-jiangxi.gov.cn/web/jyxx/002006/002006001/1.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_biangeng_gg","http://www.ccgp-jiangxi.gov.cn/web/jyxx/002006/002006002/1.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_gqita_da_bian_gg","http://www.ccgp-jiangxi.gov.cn/web/jyxx/002006/002006003/1.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_zhongbiao_gg","http://www.ccgp-jiangxi.gov.cn/web/jyxx/002006/002006004/1.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_zhaobiao_danyilaiyuan_gg","http://www.ccgp-jiangxi.gov.cn/web/jyxx/002006/002006005/1.html",["name","ggstart_time","href",'info'],add_info(f1,{"zbfs":'单一来源'}),f2],

]

def work(conp,**args):
    est_meta_large(conp,data=data,diqu="江西省江西",**args)
    est_html(conp,f=f3,**args)



if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","lch","jiangxi_jiangxi"]

    work(conp=conp)