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
from zhulong.util.etl import est_tables, gg_meta, gg_html, est_meta, est_html, add_info

_name_='weihai'



def f1(driver, num):
    locator = (By.XPATH, '(//ul[@class="article-list2"]/li/div/a)[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    locator = (By.XPATH, "(//ul[@class='pages-list']/li)[1]")
    page_all = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall('(\d+)/', page_all)[0]
    if num != int(cnum):
        if "index.jhtml" in url:
            s = "index_%d" % (num) if num > 1 else "index_1"
            url = re.sub("index", s, url)
        elif num == 1:
            url = re.sub("index_[0-9]*", "index_1", url)
        else:
            s = "index_%d" % (num) if num > 1 else "index_1"
            url = re.sub("index_[0-9]*", s, url)
        val = driver.find_element_by_xpath("(//ul[@class='article-list2']/li/div/a)[1]").get_attribute('href')[-15:]
        driver.get(url)
        locator = (By.XPATH, "(//ul[@class='article-list2']/li/div/a)[1][not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    ul = soup.find("ul", class_="article-list2")
    trs = ul.find_all("li")
    data = []
    for li in trs:
        a = li.find("a")
        try:
            title = a['title']
        except:
            title = a.text.strip()
        link = "http://www.whggzyjy.cn" + a["href"]
        try:
            span1 = li.find_all("div", class_="list-times")[0].text
        except:
            span1 = "-"
        tmp = [title, span1.strip(), link]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"]=None
    return df


def f2(driver):
    locator = (By.XPATH, "(//ul[@class='pages-list']/li)[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "(//ul[@class='pages-list']/li)[1]")
    page_all = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    page = re.findall('/(\d+)', page_all)[0]

    driver.quit()
    return int(page)


def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH,"//div[@id='content'][string-length()>30]")
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
    div=soup.find('div',id='content')
    return div




data = [
        ["gcjs_gqita_yuzhaobiao_gg","http://www.whggzyjy.cn/jyxxzbxm/index.jhtml",
         ["name", "ggstart_time", "href","info"],add_info(f1,{'gglx':'招标项目'}),f2],

        ["gcjs_zhaobiao_gg", "http://www.whggzyjy.cn/jyxxzbgg/index.jhtml",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_kaibiao_gg", "http://www.whggzyjy.cn/jyxxkbjl/index.jhtml",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_zhongbiao_gg", "http://www.whggzyjy.cn/jyxxzbgs/index.jhtml",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_gqita_bian_cheng_gg", "http://www.whggzyjy.cn/jyxxzbwj/index.jhtml",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_yucai_gg", "http://www.whggzyjy.cn/jyxxcgxq/index.jhtml",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_zhaobiao_gg", "http://www.whggzyjy.cn/jyxxcggg/index.jhtml",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_biangeng_gg", "http://www.whggzyjy.cn/jyxxgzsx/index.jhtml",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["zfcg_gqita_zhong_liu_gg", "http://www.whggzyjy.cn/jyxxcjgg/index.jhtml",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_hetong_gg", "http://www.whggzyjy.cn/jyxxcght/index.jhtml",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_yanshou_gg", "http://www.whggzyjy.cn/jyxxysbg/index.jhtml",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_liubiao_gg", "http://www.whggzyjy.cn/jyxxfbgg/index.jhtml",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["qsy_zhaobiao_gg", "http://www.whggzyjy.cn/jyxxcqgq/index.jhtml",
         ["name", "ggstart_time", "href", "info"], add_info(f1,{'gglx':'国企采购公告'}), f2],

        ["qsy_zhongbiao_gg", "http://www.whggzyjy.cn/jyxxcqss/index.jhtml",
         ["name", "ggstart_time", "href", "info"], add_info(f1,{'gglx':'国企采购公示'}), f2],
]


def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省威海市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","weihai"])



