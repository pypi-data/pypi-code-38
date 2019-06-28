import json
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
from zhulong.util.etl import est_tables, gg_html, gg_meta, est_html, est_meta, add_info

_name_='qingdao'



def f1(driver, num):
    locator = (By.XPATH, '(//td[@class="box_td"]/a)[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = int(re.findall("pageIndex=(.*)", url)[0])
    if num != cnum:
        if num == 1:
            url = re.sub("pageIndex=[0-9]*", "pageIndex=1", url)
        else:
            s = "pageIndex=%d" % (num) if num > 1 else "pageIndex=1"
            url = re.sub("pageIndex=[0-9]*", s, url)
        val = driver.find_element_by_xpath("(//td[@class='box_td']/a)[1]").get_attribute('href')[-35:]
        driver.get(url)
        locator = (By.XPATH, "(//td[@class='box_td']/a)[1][not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    ul = soup.find("div", class_="info_con")
    trs = ul.find_all("tr")
    data = []
    for li in trs:
        td = li.find("td", class_="box_td")
        a = td.find("a")
        title = a.text.strip()
        href = a["href"]
        if 'http' in href:
            link = href
        else:
            link = "https://ggzy.qingdao.gov.cn" + href
        span2 = li.find_all("td")[1]
        info = {}
        if re.findall(r'\[(\w+?)\]', title):
            diqu = re.findall(r'\[(\w+?)\]', title)[0]
            info['diqu'] = diqu
            title2 = title.split(']', maxsplit=1)[1]
            if re.findall(r'^\[(\w+?)\]', title2):
                zbfs = re.findall(r'^\[(\w+?)\]', title2)[0]
                info['zbfs'] = zbfs
        if info:info = json.dumps(info, ensure_ascii=False)
        else:info = None
        tmp = [title, span2.text.strip(), link, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, '(//td[@class="box_td"]/a)[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, '//div[@class="pages"]/a[last()]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        url = driver.current_url
        page = int(re.findall("pageIndex=(.*)", url)[0])
    except Exception as e:
        page = 1
    driver.quit()
    return int(page)


def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH, "//div[@class='ewb-main'][string-length()>30] | //div[@class='detail'][string-length()>30] | //div[@id='htmlTable'][string-length()>30]")
    WebDriverWait(driver,5).until(EC.presence_of_all_elements_located(locator))
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
    if "htmlTable" in page:
        div=soup.find('div',id='htmlTable')
    else:
        div=soup.find('div',class_='detail')
    if div == None:
        div = soup.find('div', class_='ewb-main')
    return div



data = [
        ["gcjs_zhaobiao_gg", "https://ggzy.qingdao.gov.cn/Tradeinfo-GGGSList/0-0-0?pageIndex=1",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_zgysjg_gg", "https://ggzy.qingdao.gov.cn/Tradeinfo-GGGSList/0-0-4?pageIndex=1",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_zhongbiaohx_gg", "https://ggzy.qingdao.gov.cn/Tradeinfo-GGGSList/0-0-2?pageIndex=1",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_liubiao_gg", "https://ggzy.qingdao.gov.cn/Tradeinfo-GGGSList/0-0-3?pageIndex=1",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_zhongbiao_gg", "https://ggzy.qingdao.gov.cn/Tradeinfo-GGGSList/0-0-8?pageIndex=1",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_gqita_jiaoyijincheng_gg", "https://ggzy.qingdao.gov.cn/Tradeinfo-GGGSList/0-0-9?pageIndex=1",
         ["name", "ggstart_time", "href","info"],add_info(f1,{'gglx':'交易进程'}),f2],

        ["zfcg_zhaobiao_gg", "https://ggzy.qingdao.gov.cn/Tradeinfo-GGGSList/1-1-0?pageIndex=1",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_biangeng_gg", "https://ggzy.qingdao.gov.cn/Tradeinfo-GGGSList/1-1-5?pageIndex=1",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_zhongbiao_gg", "https://ggzy.qingdao.gov.cn/Tradeinfo-GGGSList/1-1-2?pageIndex=1",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_liubiao_gg", "https://ggzy.qingdao.gov.cn/Tradeinfo-GGGSList/1-1-3?pageIndex=1",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["zfcg_gqita_jiaoyijincheng_gg", "https://ggzy.qingdao.gov.cn/Tradeinfo-GGGSList/1-1-11?pageIndex=1",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '交易进程'}), f2],
    ]




def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省青岛市",**args)
    est_html(conp,f=f3,**args)

# 网址变更：https://ggzy.qingdao.gov.cn/PortalQDManage/
# 修改时间：2019/6/27
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","qingdao"])



