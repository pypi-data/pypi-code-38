import re
from dateutil.parser import parse
import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import est_html, est_meta, add_info
import time

_name_='haicheng'
def f1(driver, num):
    locator = (By.XPATH,'//div[@class="RowPager"][1]')
    WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
    page_temp = driver.find_element_by_xpath('//div[@class="RowPager"][1]').text
    cnum = re.findall("(\d+) /", page_temp)[0]
    locator = (By.CLASS_NAME, 'GridView')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//table[@class="GridView"]//a').get_attribute("href")[-20:]
    if int(cnum) != int(num):
        locator = (By.ID,"grdBulletin_ctl18_NumGoto")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        driver.find_element_by_id("grdBulletin_ctl18_NumGoto").clear()
        driver.find_element_by_id("grdBulletin_ctl18_NumGoto").send_keys(num)
        driver.find_element_by_id("grdBulletin_ctl18_BtnGoto").click()
        locator = (
            By.XPATH, '//table[@class="GridView"]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    locator = (By.CLASS_NAME, 'GridView')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@class="GridView"]/tbody/tr[@class="Row"]')
    for content in content_list:
        if "Type=602" in driver.current_url or "Type=603" in driver.current_url:
            index = content.xpath("./td[2]/a/text()")[0]
            name_temp = content.xpath("./td[3]//span/text()")[0]
            name = index + name_temp
        else:
            type = ''.join(content.xpath("./td[1]")[0].xpath("string(.)").split("\xa0"))
            index = content.xpath("./td[2]/a/text()")[0]
            name_temp = content.xpath("./td[3]//span/text()")[0]
            name = type + index + name_temp
        ggstart_time = content.xpath("./td[last()]/text()")[0].strip()
        # print(ggstart_time)
        url = "http://www.hcsggzy.com/Bulletin/"+content.xpath("./td/a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df

def f2(driver):

    locator = (By.XPATH,'//div[@class="RowPager"][1]')
    WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
    page_temp = driver.find_element_by_xpath('//div[@class="RowPager"][1]').text
    total_page = re.findall("/ (\d+)", page_temp)[0]
    driver.quit()
    return int(total_page)

def f3(driver, url):
    driver.get(url)
    locator = (By.CLASS_NAME, "Section1")
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

    div = soup.find('div',class_="Section1")
    # print(div)
    return div


data = [
    ["zfcg_zhaobiao_gk_gg",
     "http://www.hcsggzy.com/Bulletin/BulletinList.aspx?ProType=12&AfficheType=601&Class=62&ModuleID=18",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{"method":"公开招标"}), f2],
    ["zfcg_zhaobiao_yq_gg",
     "http://www.hcsggzy.com/Bulletin/BulletinList.aspx?ProType=12&AfficheType=601&Class=63&ModuleID=18",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"method":"邀请招标"}), f2],
    ["zfcg_zhaobiao_xj_gg",
     "http://www.hcsggzy.com/Bulletin/BulletinList.aspx?ProType=12&AfficheType=601&Class=64&ModuleID=18",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"method":"询价"}), f2],
    ["zfcg_zhaobiao_jzxtp_gg",
     "http://www.hcsggzy.com/Bulletin/BulletinList.aspx?ProType=12&AfficheType=601&Class=65&ModuleID=18",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"method":"竞争性谈判"}), f2],
    ["zfcg_zhaobiao_dyly_gg",
     "http://www.hcsggzy.com/Bulletin/BulletinList.aspx?ProType=12&AfficheType=601&Class=66&ModuleID=18",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"method":"单一来源"}), f2],



    ["zfcg_biangeng_gg",
     "http://www.hcsggzy.com/Bulletin/BulletinList.aspx?ProType=12&AfficheType=602&ModuleID=18",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://www.hcsggzy.com/Bulletin/BulletinList.aspx?ProType=12&AfficheType=603&ModuleID=186",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["gcjs_zhaobiao_sg_gg",
     "http://www.hcsggzy.com/Bulletin/BulletinList.aspx?ProType=11&AfficheType=584&Class=16&ModuleID=17&ViewID=24",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"施工"}), f2],
    ["gcjs_zhaobiao_jl_gg",
     "http://www.hcsggzy.com/Bulletin/BulletinList.aspx?ProType=11&AfficheType=584&Class=17&ModuleID=17&ViewID=24",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"监理"}), f2],
    ["gcjs_zhaobiao_kc_gg",
     "http://www.hcsggzy.com/Bulletin/BulletinList.aspx?ProType=11&AfficheType=584&Class=18&ModuleID=17&ViewID=24",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"勘察"}), f2],
    ["gcjs_zhaobiao_sj_gg",
     "http://www.hcsggzy.com/Bulletin/BulletinList.aspx?ProType=11&AfficheType=584&Class=19&ModuleID=17&ViewID=24",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"设计"}), f2],
    ["gcjs_zhaobiao_qita_gg",
     "http://www.hcsggzy.com/Bulletin/BulletinList.aspx?ProType=11&AfficheType=584&Class=20&ModuleID=17&ViewID=24",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.hcsggzy.com/Bulletin/BulletinList.aspx?ProType=11&AfficheType=593&ModuleID=17&ViewID=24",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_bian_da_gg",
     "http://www.hcsggzy.com/Bulletin/BulletinList.aspx?ProType=11&AfficheType=591",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.hcsggzy.com/Bulletin/BulletinList.aspx?ProType=11&AfficheType=832&ModuleID=17&ViewID=24",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp,**args):
    est_meta(conp, data=data, diqu="辽宁省海城市",**args)
    est_html(conp, f=f3,**args)


if __name__ == "__main__":
    conp=["postgres", "since2015", "192.168.3.171", "liaoning", "haicheng"]
    import sys
    arg=sys.argv
    if len(arg) >3:
        work(conp,num=int(arg[1]),total=int(arg[2]),html_total=int(arg[3]))
    elif len(arg) == 2:
        work(conp, html_total=int(arg[1]))
    else:
        work(conp)