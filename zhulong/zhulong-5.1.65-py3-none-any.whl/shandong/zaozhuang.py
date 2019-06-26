import time
import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zhulong.util.etl import est_tables, gg_html, gg_meta, est_meta, est_html, add_info

_name_='zaozhuang'


def f1(driver, num):
    locator = (By.XPATH, "(//table[@align='center']/tbody/tr/td/a)[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # 获取当前页的url
    url = driver.current_url
    locator = (By.XPATH, '//td[@class="huifont"]')
    page_all = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall('(\d+)/', page_all)[0]
    if num != int(cnum):
        if "?Paging" not in url:
            s = "?Paging=%d" % (num) if num > 1 else "?Paging=1"
            url = url + s
        elif num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        val = driver.find_element_by_xpath('(//table[@align="center"]/tbody/tr/td/a)[1]').get_attribute('href')[-35:]
        driver.get(url)
        locator = (By.XPATH, "(//table[@align='center']/tbody/tr/td/a)[1][not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    html_data = driver.page_source
    soup = BeautifulSoup(html_data, 'html.parser')
    ul = soup.find("table", align="center", width='98%')
    lis = ul.find_all("tr", height='30')
    data = []
    for li in lis[:-2]:
        a = li.find("a")
        title = a["title"]
        link = "http://www.zzggzy.com" + a["href"]
        span = li.find("td", width='90').text
        span = re.findall(r"\[(.*)\]", span)[0]
        tmp = [title, span.strip(), link]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"]=None
    return df


def f2(driver):
    if ("本栏目信息正在更新中" in driver.page_source) or ('404' in driver.title):
        return 0
    locator = (By.XPATH, "(//table[@align='center']/tbody/tr/td/a)[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//td[@class="huifont"]')
    page_all = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    page = re.findall('/(\d+)', page_all)[0]
    driver.quit()
    return int(page)


def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH,"//td[@height='500'][string-length()>40]")
    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))
    before=len(driver.page_source)
    time.sleep(0.1)
    after=len(driver.page_source)
    i=0
    while before!=after:
        before=len(driver.page_source)
        time.sleep(0.1)
        after=len(driver.page_source)
        i+=1
        if i>5:break
    page=driver.page_source
    soup=BeautifulSoup(page,'html.parser')
    div=soup.find('td',height="500")
    return div


data = [
        ["gcjs_zhaobiao_gg", "http://www.zzggzy.com/TPFront/jyxx/070001/070001001/",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_zgysjg_gg", "http://www.zzggzy.com/TPFront/jyxx/070001/070001003/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{'gglx':'未入围公示'}),f2],

        ["gcjs_zhongbiaohx_gg", "http://www.zzggzy.com/TPFront/jyxx/070001/070001004/",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_zhongbiao_gg", "http://www.zzggzy.com/TPFront/jyxx/070001/070001005/",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_biangeng_gg", "http://www.zzggzy.com/TPFront/jyxx/070001/070001008/",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_zhaobiao_gg", "http://www.zzggzy.com/TPFront/jyxx/070002/070002001/",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_biangeng_gg", "http://www.zzggzy.com/TPFront/jyxx/070002/070002002/",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_zhongbiao_gg", "http://www.zzggzy.com/TPFront/jyxx/070002/070002003/",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_yucai_gg", "http://www.zzggzy.com/TPFront/jyxx/070002/070002004/",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["qsy_zhaobiao_gg", "http://www.zzggzy.com/TPFront/jyxx/070004/070004001/",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["qsy_biangeng_gg", "http://www.zzggzy.com/TPFront/jyxx/070004/070004002/",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["qsy_zhongbiao_gg", "http://www.zzggzy.com/TPFront/jyxx/070004/070004003/",
         ["name", "ggstart_time", "href","info"],f1,f2],
    ]


def work(conp,**args):
    est_meta(conp,data=data,diqu="山东枣庄市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","zaozhuang"])


