import json
import time

import pandas as pd
import re

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from zhulong2.util.etl import est_meta, est_html, est_meta_large

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_ = 'hubei_wuhan2'


def f1(driver, num):
    locator = (By.XPATH, '(//div[@class="col-con"])[1]//a[@href]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url = driver.current_url

    cnum = int(re.findall("pageNo=(\d+)&", url)[0])

    if num != cnum:

        url_ = re.sub("(?<=pageNo=)\d+", str(num), url)

        val = driver.find_element_by_xpath('(//div[@class="col-con"])[1]//a[@href]').get_attribute('href')[-40:-5]
        print(val)
        driver.get(url_)

        locator = (By.XPATH, '(//div[@class="col-con"])[1]//a[@href][not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    ht = driver.page_source
    soup = BeautifulSoup(ht, 'html.parser')
    div = soup.find_all('div', class_="col-con")

    data = []
    for li in div:

        name = li.find('a')['title']
        href = li.find('a')['href']
        if 'http' in href:
            href = href
        else:
            href = 'http://www.whszfcg.com/wuhan/views/announce/' + href

        ggstart_time = li.find('a', href=False).get_text()

        tmp = [name, ggstart_time, href]
        print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):
    locator = (By.XPATH, '(//div[@class="col-con"])[1]//a[@href]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//a[@class="layui-laypage-last"]').text

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="czyhome_centers"][string-length()>50]')

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
    div = soup.find('div', class_="czyhome_centers")
    return div


data = [

    ["zfcg_zhaobiao_gg", "http://www.whszfcg.com/wuhan/views/announce/queryMore.html?type=1&pageNo=1&pageSize=10&info=0", ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["zfcg_zhongbiao_gg", "http://www.whszfcg.com/wuhan/views/announce/queryMore.html?type=1&pageNo=1&pageSize=10&info=1", ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["zfcg_biangeng_gg", "http://www.whszfcg.com/wuhan/views/announce/queryMore.html?type=1&pageNo=1&pageSize=10&info=2", ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["zfcg_liubiao_gg", "http://www.whszfcg.com/wuhan/views/announce/queryMore.html?type=1&pageNo=1&pageSize=10&info=3", ["name", "ggstart_time", "href", 'info'],f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省武汉市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':

    conp = ["postgres", "since2015", "192.168.3.171", "lch", "hubei_wuhan2"]
    work(conp=conp,num=1,total=3)