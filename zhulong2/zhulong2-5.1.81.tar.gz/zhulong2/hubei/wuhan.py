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

_name_='hubei_wuhan'


def f1(driver,num):
    locator = (By.XPATH, '//ul[@class="news-list-content list-unstyled"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url = driver.current_url

    cnum = int(re.findall("index_(\d+)\.html", url)[0])

    if num != cnum:
        s = "index_%d.html" % (num)

        url_ = re.sub("index_(\d+)\.html", s, url)

        val = driver.find_element_by_xpath('//ul[@class="news-list-content list-unstyled"]/li[1]/a').get_attribute(
            'href').rsplit('/', maxsplit=1)[1]
        driver.get(url_)

        locator = (By.XPATH, '//ul[@class="news-list-content list-unstyled"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    ht = driver.page_source
    soup = BeautifulSoup(ht, 'html.parser')
    div = soup.find('ul', class_="news-list-content list-unstyled")
    uls = div.find_all('li')

    data = []
    for li in uls:
        name = li.a['title']
        href = li.a['href']
        if 'http' in href:
            href = href
        else:
            href = 'http://27.17.40.162:8000' + href
        ggstart_time = li.find('span', recursive=False).get_text()
        ly = li.div.find_all('span')[0].font.get_text()
        jy_type = li.div.find_all('span')[1].font.get_text()
        gg_type = li.div.find_all('span')[2].font.get_text()
        info={'zbfs':jy_type,'tag':ly,'gg_type':gg_type}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]
        data.append(tmp)
    df=pd.DataFrame(data=data)
   
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="news-list-content list-unstyled"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//ul[@class="pagination"]/li[last()]').text
    total = re.findall('共.+/(.+?)页', total)[0].strip()
    total=int(total)

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="art_con"][string-length()>10]')

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
    div = soup.find('div',class_="art_con")
    return div




data=[

    ["zfcg_zhaobiao_gg","http://27.17.40.162:8000/notice/cggg/index_1.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_zhongbiao_gg","http://27.17.40.162:8000/notice/zbgg/index_1.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_biangeng_gg","http://27.17.40.162:8000/notice/gzgg/index_1.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_liubiao_gg","http://27.17.40.162:8000/notice/fbgg/index_1.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_zhaobiao_danyilaiyuan_gg","http://27.17.40.162:8000/notice/dylygg/index_1.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_gqita_gg","http://27.17.40.162:8000/notice/qtgg/index_1.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_gqita_jinkou_gg","http://27.17.40.162:8000/notice/jkcpgg/index_1.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_gqita_dianzi_gg","http://27.17.40.162:8000/notice/dzscgg/index_1.html",["name","ggstart_time","href",'info'],f1,f2],

]

def work(conp,**args):
    est_meta_large(conp,data=data,diqu="湖北省武汉市",**args)
    est_html(conp,f=f3,**args)



if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","lch","hubei_wuhan"]

    work(conp=conp)