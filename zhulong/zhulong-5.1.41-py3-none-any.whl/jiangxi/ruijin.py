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

#
# url="http://gcjs.gzzbtbzx.com:88/zbgg/more_xian.asp?dq=rj&xian=%C8%F0%BD%F0&keyword=&cut=&page=1"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='ruijin'

def f1(driver,num):

    locator = (By.XPATH, "/html/body/table[3]/tbody/tr/td[3]/table[2]/tbody/tr[1]/td[2]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=url.rsplit('=', maxsplit=1)[1]


    if str(num) !=cnum:
        url = url.rsplit('=', maxsplit=1)[0] + '=' + '{}'.format(num)

        val = driver.find_element_by_xpath("/html/body/table[3]/tbody/tr/td[3]/table[2]/tbody/tr[1]/td[2]/a").text
        driver.get(url)
        locator = (
        By.XPATH, "/html/body/table[3]/tbody/tr/td[3]/table[2]/tbody/tr[1]/td[2]/a[not(contains(string(),'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url = driver.current_url
    mark = re.findall(r'http://www.rjggzyjyw.com/(.+)\?id=', url)[0]

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    data = []
    trs = soup.find_all('tr', attrs={'bgcolor': '#FFFFFF'})
    for tr in trs:

        tds = tr.find_all('td')
        if mark == 'news_xzgg.asp':
            name = tds[1].get_text().strip()
            href = tds[1].find_all('a')[1]
            href = href['href']
            # print(href)
        else:
            href = tds[1].a['href']

            name = tds[1].a.get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.rjggzyjyw.com/' + href
        ggstart_time = tds[2].get_text()

        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df

def f4(driver,num):
    locator = (By.XPATH, "//td[@bgcolor='#DFDFDF']/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[4]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    c_url=driver.current_url
    cnum=re.findall('page=(\d+)',c_url)[0]

    if int(cnum) !=num:
        url = 'http://gcjs.gzzbtbzx.com:88/zbgg/more_xian.asp?dq=rj&xian=%C8%F0%BD%F0&keyword=&cut=&page={}'.format(num)
        val = driver.find_element_by_xpath(
            "//td[@bgcolor='#DFDFDF']/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[4]/td/a").text
        driver.get(url)
        try:
            locator = (By.XPATH,
                       '//td[@bgcolor="#DFDFDF"]/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[4]/td/a[not(contains(string(),"%s"))]' % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            time.sleep(1)

    main_url = driver.current_url

    data = []
    main_url = main_url.rsplit('/', maxsplit=1)[0]

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('td', attrs={'bgcolor': '#DFDFDF'})
    table = content.find_all('table')
    table = table[1]
    trss = table.find('table').find('table')
    trs = trss.find_all('tr')

    for i in range(3, len(trs), 2):
        tr = trs[i]
        tds = tr.find_all('td')
        href = tds[0].a['href']
        if 'http' in href:
            href = href
        else:
            href = main_url + '/' + href
        name = tds[0].a.get_text()
        ggstart_time = tds[2].get_text()

        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df

def f2(driver):

    locator = (By.XPATH, "/html/body/table[3]/tbody/tr/td[3]/table[2]/tbody/tr[1]/td[2]/a | "
                         "//td[@bgcolor='#DFDFDF']/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[4]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        page = driver.find_element_by_xpath(
            "/html/body/table[3]/tbody/tr/td[3]/table[2]/tbody/tr[31]/td/a[2]").get_attribute('href')
        total = page.rsplit('=', maxsplit=1)[1]
    except:
        try:
            total=driver.find_element_by_xpath('//select[@name="page"]/option[last()]').text
        except:
            total=1

    total=int(total)
    driver.quit()
    return total

def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//table[@width="95%"]')

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
    div = soup.find('table',width="95%")
    return div


data = [
    ##f4
    ["gcjs_zhaobiao_gg", "http://gcjs.gzzbtbzx.com:88/zbgg/more_xian.asp?dq=rj&xian=%C8%F0%BD%F0&keyword=&cut=&page=1",
     ["name", "ggstart_time",  "href",'info'],f4,f2],
    ["gcjs_zhongbiaohx_gg", "http://www.rjggzyjyw.com/more.asp?id=68&city=0&dept=%D6%D0%B1%EA%B9%AB%CA%BE&pageshow=1",
     ["name", "ggstart_time",  "href",'info'],f1,f2],
    ["gcjs_gqita_da_bian_gg", "http://www.rjggzyjyw.com/more.asp?id=67&city=0&dept=%B4%F0%D2%C9&pageshow=1",
     ["name", "ggstart_time",  "href",'info'],f1,f2],


    ["zfcg_zhaobiao_gg", "http://www.rjggzyjyw.com/more.asp?id=57&city=0&dept=%D5%D0%B1%EA%B9%AB%B8%E6&pageshow=1",
     ["name", "ggstart_time",  "href",'info'],f1,f2],
    ["zfcg_gqita_da_bian_gg", "http://www.rjggzyjyw.com/more.asp?id=58&city=0&dept=%CF%EE%C4%BF%B4%F0%D2%C9&pageshow=1",
     ["name", "ggstart_time", "href",'info'],f1,f2],
    ["zfcg_zhongbiao_gg", "http://www.rjggzyjyw.com/more.asp?id=59&city=0&dept=%D6%D0%B1%EA%B9%AB%CA%BE&pageshow=1",
     ["name", "ggstart_time", "href",'info'],f1,f2],


    ["jqita_zhaobiao_gg", "http://www.rjggzyjyw.com/news_xzgg.asp?id=49&ctid=&pageshow=1",["name", "ggstart_time",  "href",'info'],add_info(f1,{"gclx":"乡镇交易"}),f2],
    ["jqita_gqita_da_bian_gg", "http://www.rjggzyjyw.com/news_xzgg.asp?id=50&ctid=&pageshow=1",["name", "ggstart_time",  "href",'info'],add_info(f1,{"gclx":"乡镇交易"}),f2],
    ["jqita_zhongbiao_gg", "http://www.rjggzyjyw.com/news_xzgg.asp?id=51&ctid=&pageshow=1",["name", "ggstart_time",  "href",'info'],add_info(f1,{"gclx":"乡镇交易"}),f2],

]
def work(conp,**args):
    est_meta(conp,data=data,diqu="江西省瑞金市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':


    conp=["postgres","since2015","192.168.3.171","jiangxi","ruijin"]

    work(conp=conp,headless=False,num=1)